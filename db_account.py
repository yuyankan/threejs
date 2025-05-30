
db = {
    'sqlserver':{
        'mars':{
            'server':xxx,  # SQL Server 服务器名称或 IP 地址
            'database':xxx,  # 数据库名称
            'username' :xxx,  # SQL Server 用户名
            'password' : xxx,  # SQL Server 密码
            'driver' : '{ODBC Driver 17 for SQL Server}',  # 推荐使用最新的 ODBC 驱动
        },
        'ksdata':{
            'server':xxx,  # SQL Server 服务器名称或 IP 地址
            'database':xxx,  # 数据库名称
            'username' : xxx,  # SQL Server 用户名
            'password' : xxx,  # SQL Server 密码
            'driver' : '{ODBC Driver 17 for SQL Server}',  # 推荐使用最新的 ODBC 驱动
        },
        
        'ems_gz':{
            'server':xxx',#'10.161.17.10',  # SQL Server 服务器名称或 IP 地址
            'database':xxx',  # 数据库名称
            'username' : xxx,  # SQL Server 用户名
            'password' : xxx,  # SQL Server 密码
            'driver' : '{ODBC Driver 17 for SQL Server}',  # 推荐使用最新的 ODBC 驱动
        },
    },
    'postgresssql':
        {
        'ems_ks':{
            'server':xxx,#server
            'port':xxx,
            'database':xxx,  # 数据库名称
            'username' : xxx,  # SQL Server 用户名
            'password' : xxx,  # SQL Server 密码
            }
        }
}
