import os
import random
import threading
import time

from openpyxl.utils.dataframe import dataframe_to_rows
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from setting import setting
from util.browserUtil import create_chrome_driver
from util.mysqlUtil import MySQLTool
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import openpyxl
from queue import Queue

from util.proxies import run_proxy_pool

url_queue = Queue()
proxies_queue = Queue()
proxies_abandon = []
lock = threading.Lock()


# 定义爬取线程类
class CrawlThread(threading.Thread):
    def __init__(self, PROXY_HOST, PROXY_PORT):
        threading.Thread.__init__(self)
        self.PROXY_HOST = PROXY_HOST
        self.PROXY_PORT = PROXY_PORT
        self.dri = create_chrome_driver(PROXY_HOST=self.PROXY_HOST, PROXY_PORT=self.PROXY_PORT)
        self.login()

    def run(self):
        first = True
        while True:
            time.sleep(random.randint(1, 5))
            lock.acquire()
            try:
                if url_queue.empty():
                    break
                journal_id = url_queue.get()
            finally:
                lock.release()

            url = f'https://www.letpub.com.cn/index.php?journalid={journal_id}&page=journalapp&view=detail'
            print(url)
            try:
                self.dri.get(url)
                if first:
                    first = False
                    div = WebDriverWait(self.dri, 60, 0.5).until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#layui-layer1 > span.layui-layer-setwin > a")))
                    div.click()
                time.sleep(0.5)
                WebDriverWait(self.dri, 80, 0.5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(13)")))
                html = self.dri.page_source
                self.parse(html, journal_id)
            except:
                html = self.dri.page_source
                if html.find('注册或登录后，查看影响因子和历年趋势图') != -1:
                    first = True
                    lock.acquire()
                    url_queue.put(journal_id)
                    lock.release()
                    self.dri.quit()
                    time.sleep(1)
                    self.dri = create_chrome_driver(PROXY_HOST=self.PROXY_HOST, PROXY_PORT=self.PROXY_PORT)
                    while True:
                        try:
                            self.login()
                            break
                        except:
                            print('登陆出错！')
                if html.find("您使用的IP地址") != -1:
                    proxies_abandon.append(self.PROXY_HOST + ':' + self.PROXY_PORT)
                    try:
                        lock.acquire()
                        url_queue.put(journal_id)
                        while proxies_queue.empty():
                            proxies = run_proxy_pool()
                            for p in proxies:
                                proxies_queue.put(p)
                        proxie = proxies_queue.get()
                        proxie = proxie.split(':')
                        self.PROXY_HOST = proxie[0]
                        self.PROXY_PORT = proxie[1]
                    finally:
                        lock.release()
                    first = True
                    self.dri.quit()
                    time.sleep(1)
                    self.dri = create_chrome_driver(PROXY_HOST=self.PROXY_HOST, PROXY_PORT=self.PROXY_PORT)
                    while True:
                        try:
                            self.login()
                            break
                        except:
                            print('登陆出错！')
                continue

    def parse(self, html, journal_id):
        if html.find('P-ISSN') != -1:
            # 定位到要删除的节点
            element_to_delete = self.dri.find_element(By.CSS_SELECTOR,
                                                      '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(4)')
            self.dri.execute_script('arguments[0].parentNode.removeChild(arguments[0]);', element_to_delete)

        if html.find('E-ISSN') != -1:
            # 定位到要删除的节点
            element_to_delete = self.dri.find_element(By.CSS_SELECTOR,
                                                      '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(4)')
            self.dri.execute_script('arguments[0].parentNode.removeChild(arguments[0]);', element_to_delete)

        if html.find('作者指南网址') != -1:
            # 定位到要删除的节点
            element_to_delete = self.dri.find_element(By.CSS_SELECTOR,
                                                      '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(11)')
            self.dri.execute_script('arguments[0].parentNode.removeChild(arguments[0]);', element_to_delete)

        if html.find('OA期刊相关信息') != -1:
            # 定位到要删除的节点
            element_to_delete = self.dri.find_element(By.CSS_SELECTOR,
                                                      '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(13)')
            self.dri.execute_script('arguments[0].parentNode.removeChild(arguments[0]);', element_to_delete)

        journal_name = self.dri.find_element(By.CSS_SELECTOR,
                                             '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(2) > td:nth-child(2) > span:nth-child(1) > a').text
        ISSN = self.dri.find_element(By.CSS_SELECTOR,
                                     '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(3) > td:nth-child(2)').text
        Impact_factor = self.dri.find_element(By.XPATH, '//*[@id="yxyz_content"]/table[2]/tbody/tr[4]/td[2]').text
        seif_c_r = self.dri.find_element(By.XPATH, '//*[@id="yxyz_content"]/table[2]/tbody/tr[5]/td[2]').text
        Impact_factor = Impact_factor.replace('点击查看影响因子趋势图', '')
        seif_c_r = seif_c_r.replace('点击查看自引率趋势图', '')
        h_index = self.dri.find_element(By.CSS_SELECTOR,
                                        '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(6) > td:nth-child(2)').text
        try:
            cite_score = self.dri.find_element(By.CSS_SELECTOR,
                                               '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(7) > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(1)').text
            cs_m_cate = self.dri.find_element(By.XPATH,
                                              '//*[@id="yxyz_content"]/table[2]/tbody/tr[7]/td[2]/table/tbody/tr[2]/td[4]/table/tbody/tr[2]/td[1]').text
            temp = cs_m_cate.split('\n')
            cs_m_cate = temp[0]
            cs_s_cate = temp[1]
            cs_division = self.dri.find_element(By.CSS_SELECTOR,
                                                '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(7) > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(4) > table > tbody > tr:nth-child(2) > td:nth-child(2)').text
            cs_rank = self.dri.find_element(By.CSS_SELECTOR,
                                            '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(7) > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(4) > table > tbody > tr:nth-child(2) > td:nth-child(3) > span').text
            cs_percent = self.dri.find_element(By.CSS_SELECTOR,
                                               '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(7) > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(4) > table > tbody > tr:nth-child(2) > td:nth-child(4) > div > div > span').text
            cs_m_cate = cs_m_cate.replace('大类：', '')
            cs_s_cate = cs_s_cate.replace('小类：', '')
        except:
            cite_score = '无'
            cs_m_cate = '无'
            cs_s_cate = '无'
            cs_division = '无'
            cs_rank = '无'
            cs_percent = '无'
        j_intro = self.dri.find_element(By.CSS_SELECTOR,
                                        '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(8) > td:nth-child(2)').text
        j_web = self.dri.find_element(By.CSS_SELECTOR,
                                      '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(9) > td:nth-child(2)').text
        j_contribute = self.dri.find_element(By.CSS_SELECTOR,
                                             '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(10) > td:nth-child(2) > a').text
        isOA = self.dri.find_element(By.CSS_SELECTOR,
                                     '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(12) > td:nth-child(2)').text
        isOA = isOA.strip()
        if len(isOA) > 3:
            isOA = '无'
        research_dirction = self.dri.find_element(By.CSS_SELECTOR,
                                                  '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(15) > td:nth-child(2)').text
        country = self.dri.find_element(By.CSS_SELECTOR,
                                        '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(16) > td:nth-child(2)').text
        language = self.dri.find_element(By.CSS_SELECTOR,
                                         '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(17) > td:nth-child(2)').text
        period = self.dri.find_element(By.CSS_SELECTOR,
                                       '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(18) > td:nth-child(2)').text
        wos_district = self.dri.find_element(By.CSS_SELECTOR,
                                             '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(23) > td:nth-child(2)').text
        temp = wos_district.split('\n')
        wos_district = temp[0]
        cas_warn = self.dri.find_element(By.CSS_SELECTOR,
                                         '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(24) > td:nth-child(2)').text
        try:
            major_cate = self.dri.find_element(By.CSS_SELECTOR,
                                               '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(25) > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(1)').text
            temp = major_cate.split('\n')
            major_cate = temp[0]
            cas_district = temp[1]
            sub_cate = self.dri.find_element(By.CSS_SELECTOR,
                                             '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(25) > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr > td:nth-child(1)').text
            temp = sub_cate.split('\n')
            sub_cate = temp[1]
            isTop = self.dri.find_element(By.CSS_SELECTOR,
                                          '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(25) > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(3)').text
            isSummarize = self.dri.find_element(By.CSS_SELECTOR,
                                                '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(25) > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(4)').text
        except:
            major_cate = '无'
            cas_district = '无'
            sub_cate = '无'
            isTop = '无'
            isSummarize = '无'
        r_speed = self.dri.find_element(By.CSS_SELECTOR,
                                        '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(31) > td:nth-child(2)').text
        em_rate = self.dri.find_element(By.CSS_SELECTOR,
                                        '#yxyz_content > table:nth-child(13) > tbody > tr:nth-child(32) > td:nth-child(2)').text
        r_speed = r_speed.replace('\n', ' ')
        em_rate = em_rate.replace('\n', ' ')

        print('期刊名字：' + journal_name.strip())
        print('h_index：' + h_index.strip())
        print('ISSN：' + ISSN.strip())
        print('Impact_factor：' + Impact_factor.strip())
        print('seif_c_r：' + seif_c_r.strip())
        print('cite_score：' + cite_score.strip())
        print('cs_m_cate:' + cs_m_cate)
        print('cs_s_cate:' + cs_s_cate)
        print('cs_division:' + cs_division)
        print('cs_rank:' + cs_rank)
        print('cs_percent:' + cs_percent)
        print('j_intro：' + j_intro.strip())
        print('j_web：' + j_web.strip())
        print('j_contribute：' + j_contribute.strip())
        print('isOA：' + isOA.strip())
        print('research_dirction：' + research_dirction.strip())
        print('country：' + country.strip())
        print('language：' + language.strip())
        print('period：' + period.strip())
        print('wos_district：' + wos_district.strip())
        print('cas_warn：' + cas_warn.strip())
        print('cas_district：' + cas_district.strip())
        print('major_cate：' + major_cate.strip())
        print('sub_cate：' + sub_cate.strip())
        print('isTop：' + isTop.strip())
        print('isSummarize：' + isSummarize.strip())
        print('r_speed:' + r_speed)
        print('em_rate:' + em_rate)
        mysqlUtil = MySQLTool('localhost', 'root', 'Mysql123321221', 'journal01')
        mysqlUtil.connect()
        mysqlUtil.insert_journal(journal_id, ISSN, journal_name, Impact_factor, seif_c_r, h_index, cite_score,
                                 cs_m_cate,
                                 cs_s_cate,
                                 cs_division, cs_rank,
                                 cs_percent, j_intro, j_web, j_contribute, isOA, research_dirction, country,
                                 language,
                                 period, wos_district,
                                 cas_warn, major_cate, sub_cate, cas_district, isTop, isSummarize, r_speed, em_rate)
        mysqlUtil.disconnect()
        new_data = [journal_id, ISSN, journal_name, Impact_factor, seif_c_r, h_index, cite_score, cs_m_cate,
                    cs_s_cate,
                    cs_division, cs_rank, cs_percent, j_intro, j_web, j_contribute, isOA, research_dirction,
                    country,
                    language, period, wos_district, cas_warn, major_cate, sub_cate, cas_district, isTop,
                    isSummarize,
                    r_speed, em_rate]
        self.write_to_excel([new_data], 'journals.xlsx')

    def write_to_excel(self, data, excel_file):
        """
            将数据写入Excel文件中
            参数：
            - data: 要写入Excel文件的数据，必须为列表或pandas DataFrame格式
            - excel_file: Excel文件路径和名称，字符串格式
            """
        # 如果数据不是pandas DataFrame格式，则将其转换为DataFrame
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data, columns=["journal_id", "ISSN", "journal_name", "Impact_factor", "seif_c_r",
                                               "h_index",
                                               "cite_score", "cs_m_cate", "cs_s_cate", "cs_division", "cs_rank",
                                               "cs_percent", "j_intro", "j_web", "j_contribute", "isOA",
                                               "research_dirction", "country", "language", "period", "wos_district",
                                               "cas_warn", "major_cate", "sub_cate", "cas_district", "isTop",
                                               "isSummarize",
                                               "r_speed", "em_rate"])

        # 判断Excel文件是否存在，存在则将数据追加到现有Excel文件中，否则创建新文件并写入数据
        lock.acquire()
        if os.path.exists(excel_file):
            try:
                wb = openpyxl.load_workbook(excel_file)
                ws = wb.active
                for r in dataframe_to_rows(data, index=False, header=False):
                    row = [r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13],
                           r[14], r[15],
                           r[16], r[17], r[18], r[19], r[20], r[21], r[22], r[23], r[24], r[25], r[26], r[27], r[28]]
                    ws.append(row)
                wb.save(excel_file)
                wb.close()
            finally:
                lock.release()
            print("数据已追加到Excel文件")
        else:
            with pd.ExcelWriter(excel_file) as writer:
                data.to_excel(writer, sheet_name='Sheet1', index=False)
            print("Excel文件不存在，已创建新文件并写入数据")

    def login(self):
        url = 'https://www.letpub.com.cn/index.php?page=login'
        self.dri.get(url)
        time.sleep(random.randint(2, 7))
        WebDriverWait(self.dri, 60, 0.5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#form > div:nth-child(6) > img")))
        self.dri.find_element(By.CSS_SELECTOR, '#email').send_keys(setting['email'])
        self.dri.find_element(By.CSS_SELECTOR, '#password').send_keys(setting['password'])
        self.dri.find_element(By.CSS_SELECTOR, '#form > div:nth-child(6) > img').click()
        time.sleep(1)


def get_url_queue():
    mysqlUtil = MySQLTool('localhost', 'root', setting['mysqlPassword'], 'journal01')
    mysqlUtil.connect()
    results = mysqlUtil.select_journal_id()
    journal_ids = []
    for result in results:
        journal_ids.append(result[0])
    mysqlUtil.disconnect()
    for i in range(1, 12000):
        if i not in journal_ids and (i < 9020 or i > 9342):
            url_queue.put(i)


if __name__ == '__main__':
    print("程序启动")
    crawl_threads = []
    get_url_queue()
    for i in range(3):
        while proxies_queue.empty():
            proxies = run_proxy_pool()
            for p in proxies:
                proxies_queue.put(p)
        time.sleep(0.5)
        proxie = proxies_queue.get()
        proxie = proxie.split(':')
        PROXY_HOST = proxie[0]
        PROXY_PORT = proxie[1]
        crawl_thread = CrawlThread(PROXY_HOST, PROXY_PORT)
        crawl_thread.start()
        crawl_threads.append(crawl_thread)

    url_queue.join()
    for crawl_thread in crawl_threads:
        crawl_thread.join()
