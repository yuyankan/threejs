import pandas as pd
import myquery_db as query_db
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta


tables_spc = {
    'product':'ks_project_yyk.ods.meta_product',
    'test_items':'ks_project_yyk.ods.spc_meta_test_parameters',
    'test_result':'ks_project_yyk.ods.spc_test_parameters_value',
}

shema2write = 'ods'
db2write = 'ks_project_yyk'

production_lines = ['C11']



def plot(df, x, y, controls, title):
    df['roll'] = df['roll'].astype(str)
    fig = px.scatter(df, x=x, y=[y], color='roll')
    # --- Add horizontal lines ---
    fig.add_hline(y=controls[0], line_dash="dash", line_color="black", annotation_text=f"CCL:{round(controls[0],2)}                                      ",annotation_position="bottom right")
    fig.add_hline(y=controls[1], line_dash="dash", line_color="red", annotation_text=f"UCL:{round(controls[1],2)}     ",annotation_position="top right")
    fig.add_hline(y=controls[2], line_dash="dash", line_color="red", annotation_text=f"LCL:{round(controls[2],2)}     ",annotation_position="bottom right")
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




def plot_oneitem(df_spc):
    #df_spc = df.groupby(['product','part2']).apply(spc_signalvalue)
    #df_spc = spc_signalvalue(df)
    

    #df_spc = df_spc.dropna()

    control_value = df_spc[['value_avg','value_ucl','value_lcl']].drop_duplicates().values[0]
    plot(df=df_spc, x='timestamp', y='value', controls=control_value, title='SPC 单值控制图')

    #diff plot
    st.divider()
    control_diff = df_spc[['diff_avg','diff_ucl','diff_lcl']].drop_duplicates().values[0]
    plot(df=df_spc, x='timestamp', y='diff', controls=control_diff, title='SPC 极差控制图')
