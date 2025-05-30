import pandas as pd
import streamlit as st
import fun_data as fd
import fun_plot as fp
import fun_layout as fl
from datetime import datetime, timedelta
import time
#import threading
from streamlit_autorefresh import st_autorefresh

#import plotly.express as px

# show current product spc

st.set_page_config(
    page_title="C11 SPC DEMO",
    page_icon="",
    layout="wide",  # 可以是 "centered" 或 "wide"
)


refresh_interval = 30 #s
count = st_autorefresh(interval=refresh_interval*1000, limit=None, key='auto_refresh')

tables_spc = {
    'product':'xxxt',
    'test_items':'xxx',
    'test_result':'xxx',
}

shema2write = 'ods'
db2write = 'ks_project_yyk'

production_line = 'C11'


def set_initail_data():
    #st.session_state = {}
    #production_line = st.sidebar.radio(label='1.Production Line: ', options=['C11'], index=0)
    st.session_state['production_line'] = production_line
    st.session_state['data_history'] = False
    if 'data' not in st.session_state:
        st.session_state['data'] = fd.load_initial_data(production_line=production_line)
        time_now =  datetime.utcnow() + timedelta(hours=8)#.strftime('%Y-%m-%d %H:%M:%S')
        st.session_state['last_update_time'] = time_now
    
    #get spc spec
    #if 'spc_spec' not in st.session_state:
    #    curday=time_now.strftime('%Y-%m-%d')
    #    st.session_state['spc_spec'] = fd.cal_spc_ctl(production_line=production_line, curday=curday)

    
    


#st.write(time_range)
st.title("C11 SPC DEMO")



#fun to update data
def update_df_periodically():
    #while True:
        #st.write('test_rerun0',st.session_state['last_update_time'])
        #time.sleep(10)
    try:
        latest_data = fd.load_latest_data(last_update_time=st.session_state['last_update_time'],production_line=st.session_state['production_line'])
        if not latest_data.empty:
            st.session_state['data'] = pd.concat([st.session_state['data'], latest_data]).drop_duplicates() # 假设有一个唯一ID列
        if not st.session_state['data_history']:
            st.session_state['data'] = fd.clean_old_data(st.session_state['data'])
        time_now =  datetime.utcnow() + timedelta(hours=8)
        st.session_state['last_update_time'] = time_now 
        #st.write('test_rerun',st.session_state['last_update_time'])
        #st.rerun() # 触发 Streamlit 重新运行
    except Exception as e:
        st.error(f"后台更新线程发生错误: {e}", icon="🚨")
        #time.sleep(60)



def work():
    #update data
    update_df_periodically()

    

    layout_choose = fl.mylayout(df=st.session_state['data'])
    if layout_choose:
        df_show,product_select,test_item,time_range,postion_choose= layout_choose
        #st.session_state['product_select'] = product_select
        #st.session_state['test_item'] = test_item
        #st.session_state['time_range'] = time_range
        #st.session_state['postion_choose'] = postion_choose
        
        
        if not df_show.empty:
            col_merge = ['product_name','test_items']
            if postion_choose:
                col_merge = ['product_name','test_items','pos_bin']
            
            #curday=time_now.strftime('%Y-%m-%d')
            curday = st.session_state['last_update_time'].strftime('%Y-%m-%d %H:00:00')
            st.session_state['spc_spec'] = fd.cal_spc_ctl(production_line=production_line, curday=curday)
       
            df_show_spc = df_show.merge(st.session_state['spc_spec'],on=col_merge, how='left')
            df_show_spc = df_show_spc.sort_values('timestamp')
            df_show_spc['diff'] = abs(df_show_spc['value'].diff())
            #st.write('spc_spec',st.session_state['spc_spec'].head())
            #st.write('df_show_spc',df_show_spc.head())
            fp.plot_oneitem(df_spc=df_show_spc)


#time_now =  datetime.utcnow() + timedelta(hours=8)
#time_diff = int(time_now-st.session_state['last_update_time']).total_seconds()
#if time_diff < refresh_interval:
 #   st.rerun()

    

#update_df_periodically()
set_initail_data()
#st.write('2', st.session_state['data'].head())
work()

