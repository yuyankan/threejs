import pandas as pd
import myquery_db as query_db
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta


tables_spc = {
    'product':xxx,
    'test_items':xxx,
    'test_result':xxx,
}

shema2write = 'ods'
db2write = 'db'

production_lines = ['C11']
days_initial_load = 10

@st.cache_data
def load_initial_data(production_line):
    time_now_date = datetime.utcnow() + timedelta(hours=8)
    time_now = time_now_date.strftime('%Y-%m-%d %H:%M:%S')
    time_last = (time_now_date-timedelta(days=days_initial_load)).strftime('%Y-%m-%d %H:%M:%S')

    query = f'''
    select p.product_name, ti.test_items, r.timestamp, r.value, r.position,r.roll
    from {tables_spc['test_result']} r
    left join {tables_spc['product']} p on r.productnameid=p.id
    left join {tables_spc['test_items']} ti on r.testitemsid=ti.id
    where 
    r.production_line='{production_line}'
    and r.timestamp >='{time_last}'
    --and r.timestamp <='{time_now}'
    '''
    df = query_db.query_ksdata(query=query,db_default='ks_project_yyk')
    #st.write('111-df', df.head())
    return df

@st.cache_data
def load_history_data(production_line,test_item, product_name, time_gap=7):

    query = f'''
    select p.product_name, ti.test_items, r.timestamp, r.value, r.position,r.roll
    from {tables_spc['test_result']} r
    join {tables_spc['product']} p on r.productnameid=p.id and p.product_name='{product_name}'
    join {tables_spc['test_items']} ti on r.testitemsid=ti.id and ti.test_items='{test_item}'
    where 
    r.production_line='{production_line}'
    and r.timestamp >=DATEADD(day, -{time_gap}, GETDATE())

    '''
    df = query_db.query_ksdata(query=query,db_default='ks_project_yyk')
    return df


def load_latest_data(last_update_time, production_line):
    #time_now_date = datetime.utcnow() + timedelta(hours=8)
    #time_now = time_now_date.strftime('%Y-%m-%d %H:%M:%S')
    last_update_time= last_update_time.strftime('%Y-%m-%d %H:%M:%S')
    query = f'''
    select p.product_name, ti.test_items, r.timestamp, r.value, r.position,r.roll
    from {tables_spc['test_result']} r
    left join {tables_spc['product']} p on r.productnameid=p.id
    left join {tables_spc['test_items']} ti on r.testitemsid=ti.id
    where 
    r.production_line='{production_line}'
    and r.timestamp >='{last_update_time}'
    '''
    df = query_db.query_ksdata(query=query,db_default='ks_project_yyk')
    return df

def clean_old_data(df):
    time_now_date = datetime.utcnow() + timedelta(hours=8)
    two_days_ago = (time_now_date - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')
    #time_now = time_now_date.strftime('%Y-%m-%d %H:%M:%S')
    df = df[df['timestamp'] >= two_days_ago]
    return df




def spc_signalvalue(df):
    df = df.sort_values('timestamp')
    df['value'] = df['value'].astype(float)
    df['diff'] = abs(df['value'].diff())


    value_avg = df['value'].mean()
    diff_avg = df['diff'].mean()
    d2 = 1.128 
    D4 = 3.267
    D3 = 0

    value_ucl = value_avg + 3*diff_avg/d2
    value_lcl = value_avg - 3*diff_avg/d2

    diff_lcl = D3 * diff_avg
    diff_ucl = D4 * diff_avg
    df_re = pd.DataFrame([[value_avg,value_ucl,value_lcl,diff_avg,diff_ucl,diff_lcl]],
                         columns=['value_avg','value_ucl','value_lcl','diff_avg','diff_ucl','diff_lcl'])

    #df['value_avg'] = value_avg
    #df['value_ucl'] = value_ucl
    #df['value_lcl'] = value_lcl

    #df['diff_avg'] = diff_avg
    #df['diff_ucl'] = diff_ucl
    #df['diff_lcl'] = diff_lcl
    #df_re = df.drop('value', axis=1)
    return df_re

def cal_position_bin(p_value):
    p_value_factor = p_value//20
    p_value_factor_y = 1 if (p_value%20) else 0
    p_bin = f'({int(max(p_value_factor+p_value_factor_y-1,0)*20)},{int((p_value_factor+p_value_factor_y)*20)}])'
  
    return p_bin


@st.cache_data
def cal_spc_ctl(production_line, curday):
    #time_now_date = datetime.utcnow() + timedelta(hours=8)
    #time_now = time_now_date.strftime('%Y-%m-%d %H:%M:%S')
    query = f'''
    select p.product_name, ti.test_items, r.timestamp, r.value, r.position,r.roll,r.production_line
    from {tables_spc['test_result']} r
    left join {tables_spc['product']} p on r.productnameid=p.id
    left join {tables_spc['test_items']} ti on r.testitemsid=ti.id
    where 
    r.production_line='{production_line}'
    --and r.timestamp <= FORMAT(GETDATE(), 'yyyy-MM-dd')
    and r.timestamp <= '{curday}'
    ;
    '''
    df = query_db.query_ksdata(query=query, db_default='ks_project_yyk')

    if not df.empty:
        split_items = ['NDC_AdhesiveCW', 'NDC_Mois_F', 'NDC_Mois_L']
        conda_special = df['test_items'].isin(split_items)
        df_rest = df[~conda_special]
        df_special = df[conda_special].dropna()
        df_special['pos_bin'] = df_special['position'].apply(cal_position_bin)

        df_rest_spec = df_rest.groupby(['production_line','product_name','test_items'])[['timestamp','value']].apply(spc_signalvalue).droplevel(-1).reset_index()
        df_special_spec = df_special.groupby(['production_line','product_name','test_items','pos_bin'])[['timestamp','value']].apply(spc_signalvalue).droplevel(-1).reset_index()
        df_result = pd.concat([df_rest_spec, df_special_spec])
        return df_result
        #st.session_state['spc_spec'] = df_result
    
