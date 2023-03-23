import json
from selenium import webdriver


def create_chrome_driver(*, PROXY_HOST, PROXY_PORT, headless=False):  # 创建谷歌浏览器对象，用selenium控制浏览器访问url
    options = webdriver.ChromeOptions()
    options.add_argument('log-level=2')
    options.add_argument('--proxy-server=http://%s:%s' % (PROXY_HOST, PROXY_PORT))
    # 开启指定浏览器，避免每次都打开新的浏览器
    # options.add_argument('--user-data-dir=C:\\Users\\快乐\\AppData\\Local\\Google\\Chrome\\User Data\\Default')
    if headless:  # 如果为True，则爬取时不显示浏览器窗口
        options.add_argument('--headless')
    prefs = {
        "profile.managed_default_content_settings.images": 1,  # 禁止加载图片
        # 'permissions.default.stylesheet': 2,  # 禁止加载css
    }
    # options.addArguments('--blink-settings=imagesEnabled=false')# 禁止加载图片
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    # 创建浏览器对象
    browser = webdriver.Chrome(options=options,
                               executable_path=r"D:\WorkSpace_Extra\TaoBao\TaoBao\util\chromedriver.exe")
    browser.execute_cdp_cmd(
        'Page.addScriptToEvaluateOnNewDocument',
        {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'}
    )

    return browser


def add_cookies(browser, cookie_file):  # 给浏览器对象添加登录的cookie
    with open(cookie_file, 'r') as file:
        cookie_list = json.load(file)
        for cookie_dict in cookie_list:
            if cookie_dict['secure']:
                browser.add_cookie(cookie_dict)
