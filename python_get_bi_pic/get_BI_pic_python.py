import os
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import base64
import python2gmail_by_api as pba

# === 可配置参数 ===
PBI_URL = "https://app.powerbi.com/groups/6bfcff47-831c-42f4-9b91-698f09603fb6/reports/b32fa71a-f310-4ab0-aa0b-e7866c9a1477/74c669750ae2fb0ddc9b?experience=power-bi"
  # 替换为你的报表链接
AUTH_JSON = "auth.json"
SCREENSHOT_PATH = "report.png"

def is_auth_json_valid():
    """验证 auth.json 是否有效（尝试打开页面）"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=AUTH_JSON)
            page = context.new_page()
            page.goto(PBI_URL)
            page.wait_for_selector("div.visualContainerHost", timeout=10000)
            browser.close()
            return True
    except Exception as e:
        print(f"⚠️ 登录状态无效，需要重新认证: {e}")
        return False

def save_new_auth_cookie():
    """调用 codegen 手动登录一次，保存 auth.json"""
    print("🔐 正在打开浏览器以登录 Power BI，请手动登录...")#!!!!!: log in manually and get new auth_json
    os.system(f"playwright codegen {PBI_URL} --save-storage {AUTH_JSON}")# have to close manually, here
    print("✅ 登录完成，Cookie 已保存到 auth.json")


def capture_report():
    """Open the Power BI report and capture screenshot after all visuals are loaded"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=AUTH_JSON, device_scale_factor=3) # pix more good: device_scale_factor
        page = context.new_page()
        

        try:
            # 1. 导航到页面，并等待初始加载完成
            print("Navigating to Power BI report...")
            page.goto(PBI_URL)
            #page.goto(PBI_URL, timeout=90000, wait_until='domcontentloaded')
            
            # 2. 等待核心报表容器出现 (这步依然保留，作为基础检查)
            print("Waiting for the main report container...")
            page.wait_for_selector("div.visualContainerHost", timeout=180000)#3min

            # Wait for loading overlays (like spinners) to disappear
            print("Wait for loading overlays (like spinners) to disappear")
            for selector in [".spinner", ".busyIcon", ".loadingIcon", ".ghostContainer"]:
                try:
                    page.wait_for_selector(selector, state="detached", timeout=60000)
                except PlaywrightTimeoutError:
                    print(f"⚠️ Timeout while waiting for {selector} to disappear.")

            # Additional wait: ensure all visual containers have rendered
            print("Additional wait: ensure all visual containers have rendered")
            page.wait_for_function(
                """() => {
                    const containers = document.querySelectorAll('div.visualContainer');
                    if (containers.length < 19) return false;  // 可根据你的图表数量调整
                    return Array.from(containers).every(container => {
                        const visible = container.offsetWidth > 10 && container.offsetHeight > 10;
                        const hasChart = container.querySelector('svg, canvas, .bar, .card, .textRun,table,.pivotTable') !== null;
                        return visible && hasChart;
                    });
                }""",
                timeout=180000
            )


            # Screenshot
            page.screenshot(path=SCREENSHOT_PATH, full_page=True)
            content = page.query_selector("div.visualContainerHost")
            if content:
                image_file = 'image.jpg'
                content.screenshot(path=image_file)
                #content_byte = content.screenshot()
                #base64 str
                #pic_base64 = base64.b64encode(content_byte).decode('utf-8')
                #print('pic_base64',pic_base64)
                #send to gmail!!!
                pba.work(subject='C11 SPC DAILY REPORT',
                content='Hi,\nPlease find below C11 SPC ALARM DAILY REPORT',
                image_url_list =[image_file],
                image_desc_list =['',],
                receivers_list=['caren.kan@ap.averydennison.com']
                )
                #sg.work(df_list=['',],pic_url_list=['',],pic_description_list=["pic_test"],pic_base64str_list=[pic_base64])


           
            print(f"📸 Report screenshot saved: {SCREENSHOT_PATH}")

        except PlaywrightTimeoutError:
            print("❌ Report load timeout or error")
        finally:
            browser.close()

#caren.kan@averydennison1.onmicrosoft.com
if __name__ == "__main__":

    #check first
    if not Path(AUTH_JSON).exists() or not is_auth_json_valid():
        save_new_auth_cookie()

    capture_report()
