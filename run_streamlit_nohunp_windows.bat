@echo off
set python_exe="C:\Users\adm caren kan\myenv\com\Scripts\python.exe"
set app_script="C:\Users\adm caren kan\myenv\01_project_yyk\01_SPC\02_demo_streamlit\spc_demo_streamlit_v5.py"
set log_file="C:\Users\adm caren kan\myenv\01_project_yyk\01_SPC\02_demo_streamlit\streamlit_log.log"

REM log file
if not exist %log_file% (
    echo.> %log_file%
)

REM : address
cd /d "C:\Users\adm caren kan\myenv\01_project_yyk\01_SPC\02_demo_streamlit"

REM run
%python_exe% -m streamlit run %app_script% >> %log_file% 2>&1
