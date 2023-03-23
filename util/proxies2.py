import requests
from bs4 import BeautifulSoup
import time
def get_proxies():
    proxies = []
    for page in range(1,30):
        url = f'https://www.kuaidaili.com/free/inha/{page}/'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        ips = soup.find_all('td', {'data-title': 'IP'})
        ports = soup.find_all('td', {'data-title': 'PORT'})
        for i in range(len(ips)):
            proxy = ips[i].text + ':' + ports[i].text
            proxies.append(proxy)
    return proxies

def check_proxy(proxies):
    url = 'http://www.baidu.com'
    available_proxies = []
    for proxy in proxies:
        try:
            response = requests.get(url, proxies={'http': proxy, 'https': proxy}, timeout=3)
            if response.status_code == 200:
                print(proxy + ' 可用')
                available_proxies.append(proxy)
        except:
            print(proxy + ' 不可用')
    return available_proxies


def run_proxy_pool():
    while True:
        proxies = get_proxies()
        available_proxies = check_proxy(proxies)
        print('共找到可用代理IP：', len(available_proxies))
        time.sleep(10)

if __name__ == '__main__':
    run_proxy_pool()