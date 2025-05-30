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


def load_initial_data(production_line):
    time_now_date = datetime.utcnow() + timedelta(hours=8)
    time_now = time_now_date.strftime('%Y-%m-%d %H:%M:%S')
    time_last = (time_now_date-timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')

    query = f'''
    select p.product_name, ti.test_items, r.timestamp, r.value, r.position,r.roll
    from {tables_spc['test_result']} r
    left join {tables_spc['product']} p on r.productnameid=p.id
    left join {tables_spc['test_items']} ti on r.testitemsid=ti.id
    where 
    r.production_line='{production_line}'
    and r.timestamp >='{time_last}'
    and r.timestamp <='{time_now}'
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
    two_days_ago = (time_now_date - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
    #time_now = time_now_date.strftime('%Y-%m-%d %H:%M:%S')
    df = df[df['timestamp'] >= two_days_ago]
    return df




def spc_signalvalue(df):
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

    df['value_avg'] = value_avg
    df['value_ucl'] = value_ucl
    df['value_lcl'] = value_lcl

    df['diff_avg'] = diff_avg
    df['diff_ucl'] = diff_ucl
    df['diff_lcl'] = diff_lcl
    return df



def plot(df, x, y, controls, title):
    df['roll'] = df['roll'].astype(str)
    fig = px.scatter(df, x=x, y=[y], color='roll')
    # --- Add horizontal lines ---
    fig.add_hline(y=controls[0], line_dash="dash", line_color="black", annotation_text=f"CCL:{controls[0]}                                      ",annotation_position="bottom right")
    fig.add_hline(y=controls[1], line_dash="dash", line_color="red", annotation_text=f"UCL:{controls[0]}     ",annotation_position="top right")
    fig.add_hline(y=controls[2], line_dash="dash", line_color="red", annotation_text=f"LCL:{controls[2]}     ",annotation_position="bottom right")
    # --- Set the title ---
    # --- Update layout with title and center it ---
    # --- 添加数值标签在直线中间 ---
    '''
    for c in controls:

        fig.add_annotation(

            x=df[x].min(),  # 将文本的 x 坐标设置在 x 轴的中间

            y=c,      # 将文本的 y 坐标设置在水平线的值

            text=c,

            showarrow=False,     # 不显示箭头

            xanchor="center",    # 水平居中文本

            yanchor="middle",    # 垂直居中文本

            font=dict(size=12, color="green"),

            bgcolor="white",

            opacity=0.8

        )'''
    fig.update_layout(
        title=title,
        xaxis_title="Timestamp",
        yaxis_title="Value",
        showlegend=False,
        title_x=0.5,  # Set title_x to 0.5 for centering,
        legend_title="roll:",  # 设置图例标题
        legend=dict(
            x=1.02,  # 设置图例的 x 坐标（1 是图表右边缘，大于 1 会将其移到图表外）
            y=1,     # 设置图例的 y 坐标（1 是图表顶部）
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            ),
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=2
    )
    )

    #show
    st.plotly_chart(fig)
    #fig.show()




def plot_oneitem(df):
    #df_spc = df.groupby(['product','part2']).apply(spc_signalvalue)
    df_spc = spc_signalvalue(df)

    #df_spc = df_spc.dropna()

    control_value = df_spc[['value_avg','value_ucl','value_lcl']].drop_duplicates().values[0]
    plot(df=df_spc, x='timestamp', y='value', controls=control_value, title='SPC 单值控制图')

    #diff plot
    st.divider()
    control_diff = df_spc[['diff_avg','diff_ucl','diff_lcl']].drop_duplicates().values[0]
    plot(df=df_spc, x='timestamp', y='diff', controls=control_diff, title='SPC 极差控制图')
