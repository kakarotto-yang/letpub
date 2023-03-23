import requests
from bs4 import BeautifulSoup
import time
def get_proxies():
    proxies = []
    for page in range(1,3):
        url = f'http://www.ip3366.net/free/?stype=1&page={page}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        ips = soup.select('#list > table > tbody > tr')
        for ip in ips:
            proxy = ip.select('td:nth-child(1)')[0].text+ ':' +ip.select('td:nth-child(2)')[0].text
            proxies.append(proxy)
    return proxies

def check_proxy(proxies):
    url = 'https://www.letpub.com.cn/index.php'
    available_proxies = []
    for proxy in proxies:
        try:
            response = requests.get(url, proxies={'http': proxy, 'https': proxy}, timeout=3)
            if response.status_code == 200:
                print(proxy + ' 可用')
                available_proxies.append(proxy)
        except:
            pass
    return available_proxies


def run_proxy_pool():

    proxies = get_proxies()
    available_proxies = check_proxy(proxies)
    print('共找到可用代理IP：', len(available_proxies))
    time.sleep(10)
    return available_proxies

if __name__ == '__main__':
    run_proxy_pool()