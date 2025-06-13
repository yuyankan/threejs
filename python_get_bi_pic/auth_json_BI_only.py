import time
from playwright.sync_api import sync_playwright, Page, expect

def save_powerbi_auth_state(
    auth_file_path: str = "powerbi_auth_state.json", 
    headless: bool = False,
    timeout: int = 180000  # 将超时时间延长至 3 分钟 (180,000 毫秒)
):
    """
    启动一个浏览器实例，引导用户手动登录 Power BI,
    然后将浏览器的认证状态保存到指定文件中。

    Args:
        auth_file_path (str): 用于保存认证状态的 JSON 文件路径。
                              默认为 "powerbi_auth_state.json"。
        headless (bool): 是否以无头模式运行浏览器。
                         手动登录时必须设置为 False。
        timeout (int): 等待用户登录成功的最大时长（以毫秒为单位）。
    """
    print("--- Power BI 认证状态保存工具 ---")
    if headless:
        print("警告: 无头模式无法进行手动登录。请将 headless 设置为 False。")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1. 导航到 Power BI 登录页面
            print("正在打开 Power BI 登录页面...")
            page.goto("https://app.powerbi.com", timeout=60000)

            # 2. 提示用户进行手动登录
            print("\n=========================================================")
            print("请在打开的浏览器窗口中手动完成登录操作。")
            print(f"脚本将等待您登录，最长等待时间为 {timeout / 60000} 分钟。")
            print("=========================================================")

            # 3. 等待登录成功的关键元素出现
            # 等待URL变为登录成功后的主页地址
            expected_url = "https://app.powerbi.com/home?experience=power-bi"
            expect(page).to_have_url(expected_url, timeout=timeout)

            print("\n检测到登录成功!")

            # 4. 保存认证状态
            context.storage_state(path=auth_file_path)
            print(f"认证状态已成功保存到文件: '{auth_file_path}'")

        except Exception as e:
            print(f"\n操作失败或超时: {e}")
            print("请确保您在指定时间内成功登录，并且网络连接正常。")

        finally:
            # 5. 关闭浏览器
            print("正在关闭浏览器...")
            browser.close()
            print("程序执行完毕。")


if __name__ == "__main__":
    # --- 如何使用 ---
    # 运行此脚本后，会弹出一个浏览器窗口。
    # 您需要在该窗口中手动输入您的 Power BI 账号和密码完成登录。
    # 登录成功后，脚本会自动检测并将登录信息（Cookies、LocalStorage等）
    # 保存到 `powerbi_auth_state.json` 文件中。
    
    # 下次运行其他需要登录的 Playwright 脚本时，
    # 您可以通过 browser.new_context(storage_state="powerbi_auth_state.json")
    # 直接加载此文件，跳过登录步骤。
    
    save_powerbi_auth_state()
