from fastapi import FastAPI,WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
from typing import List, Dict
import asyncio
#import pyodbc  # 导入 pyodbc 库
import myquery_db as query_db
from datetime import datetime
import json
app = FastAPI()

fresh_seconds = 5
# 允许跨域访问 (WebSocket 需要单独处理，这里可能不需要，但保留以防万一)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境请配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

part_name_index = 'KSP_C11.Device1.C11_OPCDA.C11'
parts_read_o = ['Web temp in silicone dryer1',''
                'Temp of Cooled water CLU1',
                'Energydata_Roll1_DS_Pressure',
                'Power of Corona #1',
                'Web temp in adhesive dryer4',
                'Tension between PlU-Die',
                'Web temp in adhesive dryer6',
                'Web temp in adhesive dryer5'
    ]

name_new = ["roller_d",
            "roller_silicone",
            "oven_silicone",
            "roller_glue",
            "oven_glue",
            "roller_merge",
            "roller_f",
            "roller_finish"]

name_maping = {}
parts_read = []
parts_mapping = {}
for i in range(len((parts_read_o))):
    p = parts_read_o[i]
    p_temp = '.'.join([part_name_index, p])
    parts_read.append(p_temp) 
    parts_mapping[p_temp] = p
    name_maping[p_temp] = name_new[i]
	


connected_clients: List[WebSocket] = []  # Store connected WebSocket clients
df = pd.DataFrame()

part_colors_state = ["#ff0000", "#00ff00", "#ff0000", "#00ff00", "#ff0000", "#00ff00", "#ff0000", "#00ff00"]
color_toggle = True
parts_info_from_db: List[Dict] = []  # 用于存储从数据库读取的零件信息

async def fetch_parts_info_from_db():
    global parts_info_from_db
    global parts_read
    global parts_mapping
    global name_maping

    global df
 
    query = f'''
        with temp as (
            SELECT _name, _value, _timestamp, rank() over(PARTITION by _name order by _timestamp desc) rk
            FROM KEP_KSP_DATA.dbo.KSP_C11_2_New
            where _QUALITY='192'
            --and  kcn._name='KSP_C11.Device1.C11_OPCDA.C11.Product Number'
            and _name in ({str(set(parts_read))[1:-1]})
        )
        select _name part0, _value value, _timestamp 'timestamp'
        from temp
        where rk<=5
        order by 'timestamp' desc
    '''
    df = query_db.query_ksdata(query=query,db='ksdata')
    print('1',df)

    df['part2'] = df['part0'].map(parts_mapping)
    df['part'] = df['part0'].map(name_maping)
   
    #df.drop('part0',axis=1, inplace=True)

    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    col_show = ['part','timestamp','value']

    parts_info_from_db = df[col_show].to_dict(orient='records')


#backup
async def fetch_parts_info_from_db_backup():
    global parts_info_from_db
    global name_new
    global df
 
    
    df = pd.DataFrame()
    df['part'] = name_new
    df['timestamp'] = pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    df['value'] = [1, 2, 3, 4, 5, 6, 7, 8]
    print('1',df)


    parts_info_from_db = df.to_dict(orient='records')
 
      


#后台任务， 定时广播数据
async def update_data_and_colors():
    """Update data and colors, and send to clients via WebSocket."""
    global part_colors_state
    global color_toggle
    global parts_info_from_db

    while True:
        # 1. 更新颜色
        new_colors = []
        for color in part_colors_state:
            if color == "#ff0000":
                new_colors.append("#00ff00" if color_toggle else "#ff0000")
            elif color == "#00ff00":
                new_colors.append("#ff0000" if color_toggle else "#00ff00")
            else:
                new_colors.append(color)
        part_colors_state = new_colors
        color_toggle = not color_toggle

        # 2. 从数据库刷新零件信息
        await fetch_parts_info_from_db()#use backup
        #await fetch_parts_info_from_db_backup()#use backup

        # 3. Prepare the data to send
        data_to_send = {
            "part_colors": part_colors_state,
            "parts_info": parts_info_from_db
        }
        # 4. Send data to all connected clients
        print('client', connected_clients)
        for client in connected_clients:
            try:
                await client.send_text(json.dumps(data_to_send))
                print('data sented--------------------')
            except WebSocketDisconnect:
                connected_clients.remove(client)  # Clean up disconnected clients

        await asyncio.sleep(fresh_seconds)  # 颜色和数据刷新频率保持一致



@app.get("/status")
async def get_status():
    global parts_info_from_db
    global df
    return {'df':df,
            "name_maping":name_maping,
        "part_colors": part_colors_state,
        "parts_info": parts_info_from_db
    }


#这是一个 FastAPI 装饰器，用于声明一个 WebSocket 路由
#它指定了当客户端尝试建立 WebSocket 连接到 "/ws" 路径时， FastAPI 应该调用下面的函数 (websocket_endpoint).

#这与使用 @app.get() 等装饰器定义 HTTP 路由非常相似，但它是专门为 WebSocket 连接准备的。
@app.websocket("/ws/data")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connection."""
    await websocket.accept()
    connected_clients.append(websocket)  # Add client to the list of connected clients
    print(f"Client connected: {websocket.client}")
    try:
        # Send initial data on connection
        #await websocket.send_text(json.dumps({
        #    "part_colors": part_colors_state,
        #    "parts_info": parts_info_from_db
        #}))

        while True:
            # Keep the connection open to allow for sending updates
            await asyncio.sleep(0.1)  # prevent the loop from consuming too much CPU
    except WebSocketDisconnect:
        connected_clients.remove(websocket)  # Remove client on disconnect
        print(f"Client disconnected: {websocket.client}")

#这是一个 FastAPI 装饰器，用于注册一个在应用程序启动时执行的事件处理程序。
#启动后台广播任务
@app.on_event("startup")
async def startup_event():
    """Start the background task on startup."""
    asyncio.create_task(update_data_and_colors())

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
