import re
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import tqdm
import time

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"}

def crawling_news_list(args, dart_class):
    # url 설정
    search_keyword = f"{(args.search_keyword.replace(' ', '+')).replace('&', '%26')}+{dart_class}"
    news_url = f"https://search.naver.com/search.naver?where=news&sm=tab_jum&query={search_keyword}&nso=p%3Afrom{args.start_date}to{args.end_date}"

    news_dict = {}
    idx = 0
    current_page = 1    # 시작 페이지
    crawled_news = []   # 기사 중복 방지를 위한 url list
    crawling = 1        # while 조정하는 flag
    while crawling != 0:
        page_url = news_url + f"&start={current_page}"
        req = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(req.text, 'html.parser')
        table = soup.find('ul', {'class' : 'list_news'})

        # 해당 날짜에 기사가 없는 경우 pass
        if table is None:
            break
        li_list = table.find_all('li', {'id' : re.compile('sp_nws.*')})
        area_list = [li.find('div', {'class' : 'news_area'}) for li in li_list]
        info_list = [area.find('div', {'class' : 'info_group'}) for area in area_list] # 언론사 & 날짜 리스트
        # title_list = [area.find('a', {'class' : 'news_tit'}) for area in area_list]


        # 네이버뉴스 href 가 있으면 저장
        for i in range(len(area_list)):
            for info in info_list[i].find_all('a'):
                # 뉴스 카테고리만 수집 (스포츠, 연예, 날씨 등 제외)
                # keyword_list = [args.search_keyword, args.dart_class]
                if info.get('href').split("//")[1].startswith("news.naver") and info.get('href') not in crawled_news:
                    crawled_news.append(info.get('href'))
                    news_dict[idx] = {}
                    news_dict[idx]['name'] = args.search_keyword
                    news_dict[idx]['url'] = info.get('href')
                    news_dict[idx]['id'] = args.dart_id
                    idx += 1

            # 페이지 내 마지막 기사 url 까지 저장 후 처리
            if i==(len(area_list)-1):
                if soup.find('a', {'class': 'btn_next'}).get('href'):   # '다음' 버튼이 활성화 돼있으면 페이지 추가
                    current_page += 10
                else:                                                   # '다음' 버튼이 활성화 돼있지 않으면 마지막 페이지 -> 크롤링 중단
                    crawling = 0

    # 네이버 뉴스 url 저장
    columns = ['name', 'url', 'id']
    if news_dict:
        news_df = pd.DataFrame(news_dict).T
        news_df.to_csv(args.crawling_list_path, index=False, columns=columns, encoding='utf-8-sig', mode='a', header=None)



def crawling_news(args, name, num, kind, urls):
    news_dict = {}
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(executable_path=args.webdriver_path, options=options)

    with tqdm.tqdm(total=len(urls), desc=f"{name} Crawling News") as pbar:
        for idx, url in enumerate(urls):
            try:
                news_dict[idx] = {}
                driver.get(url)
                # time.sleep(2)

                # redirect 되는 기사 pass
                if driver.current_url.split("//")[1].startswith("news"):
                    req = requests.get(url, headers=headers)
                    soup = BeautifulSoup(req.text, 'html.parser')

                    # 기사 헤더
                    header = soup.find('div', {'class': 'article_header'})
                    info = header.find('div', {'class': 'article_info'})
                    title = info.find('h3').get_text()
                    press_name = header.find('div', {'class': 'press_logo'}).find('a').find('img').get('title')
                    dates = info.find_all('span', {'class': 't11'})

                    if len(dates) == 2:
                        date = dates[0].get_text().split(" ")
                        publish_date = date[0]
                        publish_time = date[1] + " " + date[2]

                        date = dates[1].get_text().split(" ")
                        modify_date = date[0]
                        modify_time = date[1] + " " + date[2]
                    else:
                        date = dates[0].get_text().split(" ")
                        publish_date = date[0]
                        publish_time = date[1] + " " + date[2]
                        modify_date = date[0]
                        modify_time = date[1] + " " + date[2]

                    # 기사 본문
                    body = soup.find('div', {'id': 'articleBody'})
                    content = body.find('div', {'class': '_article_body_contents'}).get_text()
                    content = content.replace("\n", "")
                    content = content.replace("\t", "")
                    content = content.replace("// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}", "")

                    # # 기사 반응
                    # try:
                    #     reaction_good = driver.find_element_by_xpath(
                    #         '//*[@id="spiLayer"]/div[1]/ul/li[1]/a/span[2]').get_attribute('innerHTML')
                    #     reaction_warm = driver.find_element_by_xpath(
                    #         '//*[@id="spiLayer"]/div[1]/ul/li[2]/a/span[2]').get_attribute('innerHTML')
                    #     reaction_sad = driver.find_element_by_xpath(
                    #         '//*[@id="spiLayer"]/div[1]/ul/li[3]/a/span[2]').get_attribute('innerHTML')
                    #     reaction_angry = driver.find_element_by_xpath(
                    #         '//*[@id="spiLayer"]/div[1]/ul/li[4]/a/span[2]').get_attribute('innerHTML')
                    #     reaction_want = driver.find_element_by_xpath(
                    #         '//*[@id="spiLayer"]/div[1]/ul/li[5]/a/span[2]').get_attribute('innerHTML')
                    # except:
                    #     reaction_good = 0
                    #     reaction_warm = 0
                    #     reaction_sad = 0
                    #     reaction_angry = 0
                    #     reaction_want = 0

                    # Save data to file
                    news_dict[idx]['num'] = num
                    news_dict[idx]['name'] = name
                    news_dict[idx]['class'] = kind
                    news_dict[idx]['title'] = title
                    news_dict[idx]['press'] = press_name
                    news_dict[idx]['url'] = url
                    news_dict[idx]['content'] = content
                    news_dict[idx]['publish_date(8)'] = publish_date
                    news_dict[idx]['publish_time(4)'] = publish_time
                    news_dict[idx]['modify_date(8)'] = modify_date
                    news_dict[idx]['modify_time(4)'] = modify_time
                    news_dict[idx]['publish_date'] = f"{publish_date} {publish_time}"
                    news_dict[idx]['modify_date'] = f"{modify_date} {modify_time}"
                    news_dict[idx]['id']=args.dart_id
                    # news_dict[idx]['reaction_good'] = reaction_good
                    # news_dict[idx]['reaction_warm'] = reaction_warm
                    # news_dict[idx]['reaction_sad'] = reaction_sad
                    # news_dict[idx]['reaction_angry'] = reaction_angry
                    # news_dict[idx]['reaction_want'] = reaction_want
                pbar.update(1)


                columns = ['num', 'name', 'class', 'title', 'press', 'url', 'content', 'publish_date(8)',
                           'publish_time(4)', 'modify_date(8)', 'modify_time(4)', 'publish_date', 'modify_date', 'id']
                news_df = pd.DataFrame(news_dict).T
                news_df.dropna(axis=0, inplace=True)
                if os.path.isfile(args.output_file_path):
                    news_df.to_csv(args.output_file_path, columns=columns, mode='a', index=False, header=None,
                                   encoding='utf-8-sig')
                else:
                    news_df.to_csv(args.output_file_path, columns=columns, index=False, encoding='utf-8-sig')
                news_dict = {}
            except:
                print("except error")
                pbar.update(1)



    driver.close()
