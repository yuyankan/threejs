import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import fun_data as fd


def update_choice(k,v):
        st.session_state[k] = st.session_state[v]


def add_history_data():
     st.session_state['data_history'] = True
     df_past_7day = fd.load_history_data(production_line=st.session_state['production_line'],
                                         test_item=st.session_state['test_item'], 
                                         product_name=st.session_state['product_select'], 
                                         time_gap=7)
     st.session_state['data'] = pd.concat([st.session_state['data'],df_past_7day]).drop_duplicates()
     

def mylayout(df):
    
    #df = pd.read_csv('df_spc_result.csv')
    #df = pd.read_csv('c11_demo_2.csv')
    #df = pd.read_csv('df_spc_result3.csv')
    #df = pd.read_csv('c11_spc_demo_4.csv')
    #df = fs.read_data_default('C11')
    # 在侧边栏中添加一个标题
    st.sidebar.header("SPC 项目选择")

    colum_overall = ['product', 'roll','test_items_o', 'test_items','timestamp','timestamp_speed','speed','point_num', 'position','pos_bin']

    # default: latest product: order by time
    df = df.sort_values('timestamp', ascending=False)
    #st.write(df.head())
    productions = list(df['product_name'].unique())
    
    st.sidebar.divider()
    #st.write(st.session_state.keys())

    #st.write(f'1: {datetime.utcnow()}')
    #st.write(st.session_state['product_select'],
    #         st.session_state['test_item'],
    ##         st.session_state['time_range']
    #         )
    if 'product_select' not in st.session_state:
         st.session_state['product_select'] = productions[0]

    product_select = st.sidebar.radio(label='2.Product', 
                                      options=productions,
                                       index=productions.index(st.session_state['product_select']) if (('product_select' in st.session_state) and (st.session_state['product_select'])) else 0,
                                        on_change=update_choice,
                                        key='product_select0',
                                        args=('product_select','product_select0')
                                       ) # default current one
    #st.write(f'2.product_select,{product_select}', datetime.utcnow())
    st.sidebar.divider()
    test_items_options = list(df['test_items'].unique())
    test_item = st.sidebar.selectbox(label='3.Test Item', 
                                     options=test_items_options, 
                                     index=test_items_options.index(st.session_state['test_item']) if (('test_item' in st.session_state ) and (st.session_state['test_item'])) else None,
                                     on_change=update_choice,
                                     key='test_item0',
                                     args=('test_item','test_item0') 
                                     )
    df_show = pd.DataFrame()
    postion_choose = None
    c1, c2 = st.columns([4,1])
    with c1:
            st.header(f'SPC: {st.session_state['production_line']}_{product_select}_{test_item}' if not postion_choose else f'SPC: {st.session_state['production_line']}_{product_select}_{test_item}_postion:{postion_choose}')
    with c2:
            #st.write(f'Current time: ', st.session_state['last_update_time'].strftime('%Y-%m-%d %H:%M:%S'))
            st.markdown(f"<mark style='background-color: transparent; color: green; font-weight: bold;'>Current time: {st.session_state['last_update_time'].strftime('%Y-%m-%d %H:%M:%S')}</mark>", unsafe_allow_html=True)
            st.button(label='Load history data: 7 days',on_click=add_history_data)



    if product_select and test_item:
        
        df_show = df[(df['product_name']==product_select) &(df['test_items']==test_item)]
        #postion items
        postion_col_items = ['NDC_AdhesiveCW', 'NDC_Mois_F', 'NDC_Mois_L']
        if test_item in postion_col_items:
            st.divider()
            #add posbin columns
            df_show['pos_bin'] = df_show['position'].apply(fd.cal_position_bin)
            pos_bins_options = list(df_show['pos_bin'].unique())
            postion_choose = st.sidebar.selectbox(label='4. Chosse positon',
                                                  options=pos_bins_options, 
                                                  index=pos_bins_options.index(st.session_state['postion_choose']) if (('postion_choose' in st.session_state) and (st.session_state['postion_choose']))else None,
                                                  on_change=update_choice,
                                                  key='postion_choose0',
                                                  args=('postion_choose','postion_choose0') 
                                                  )
            if not postion_choose:
                st.write('Have to choose one postion')
                return None
            conda_positon = df_show['pos_bin']==postion_choose
            df_show = df_show[ conda_positon]
                
        
        st.sidebar.divider()
        df_show['timestamp'] = pd.to_datetime(df_show['timestamp'])
        start_time = df_show['timestamp'] .min().to_pydatetime()
        end_time = df_show['timestamp'].max().to_pydatetime()
        minute_step = timedelta(minutes=1)
        if 'time_range' not in st.session_state:
            st.session_state['time_range'] = (start_time, end_time)


   
        time_range = st.sidebar.slider(label="5.Time range",  
                                min_value=start_time, 
                                max_value=end_time, 
                                value=(start_time, end_time),#st.session_state['time_range'],

                                step = minute_step,

                                format="YYYY-MM-DD HH:mm:ss" , # 自定义显示格式),
                                on_change=update_choice,
                                key='time_range0',
                                args=('time_range','time_range0') 

    )
       
        conda_time = (df_show['timestamp']>=time_range[0]) & (df_show['timestamp']<=time_range[1])
        df_show = df_show[conda_time]
    
        return [df_show,product_select,test_item,time_range,postion_choose]








