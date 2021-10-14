import re
import os
import time
import requests
from pandas import DataFrame
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm.auto import tqdm


headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"}

def crawling(args):
    print('Start crawling! Keyword: {} Start date: {} End date: {} Exact search: {} Press code: {}'.format(args.search_keyword, args.start_date, args.end_date, args.exact_search, args.press_code))

    if args.start_date is None:
        news_url = 'https://search.naver.com/search.naver?where=news&query={}&related=0&mynews=1&office_type=1&news_office_checked={}'
        news_url = news_url.format(args.search_keyword, args.press_code)
    else:
        news_url = 'https://search.naver.com/search.naver?where=news&query={}&pd=3&ds={}&de={}&related=0&mynews=1&office_type=1&news_office_checked={}'
        news_url = news_url.format(args.search_keyword, args.start_date, args.end_date, args.press_code)



    # print(news_url)
    req = requests.get(news_url, headers=headers)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')


    news_dict = {}
    idx = 0
    current_page = 1

    pages = soup.find('div', {'class': 'sc_page_inner'})
    # print("1 p.text:", p.text)
    for p in pages.find_all('a'):
        print("p.text:", p.text)
        if p.text == str(current_page):
            next_page_url = 'https://search.naver.com/search.naver' + p.get('href')
            print("p.get('href')", p.get('href'))

    # Article title / press / url
    table = soup.find('ul', {'class': 'list_news'})
    if not table:
        return None
    li_list = table.find_all('li', {'id': re.compile('sp_nws.*')})
    area_list = [li.find('div', {'class': 'news_area'}) for li in li_list]
    a_list = [area.find('a', {'class': 'news_tit'}) for area in area_list]  # 뉴스 제목 리스트
    info_list = [area.find('div', {'class': 'info_group'}) for area in area_list]  # 언론사 & 날짜 리스트
    print(len(a_list))

    # with tqdm(total = len(a_list), desc='Crawling article title') as pbar:
    #     crawled_news = []   # 기사 중복 방지를 위한 url list
    #     while current_page <= args.max_page:
    #
    #         # li_list = table.find_all('li', {'id' : re.compile('sp_nws.*')})
    #         # area_list = [li.find('div', {'class' : 'news_area'}) for li in li_list]
    #         # a_list = [area.find('a', {'class' : 'news_tit'}) for area in area_list]  # 뉴스 제목 리스트
    #         # info_list = [area.find('div', {'class' : 'info_group'}) for area in area_list] # 언론사 & 날짜 리스트
    #         #
    #
    #         for i in range(len(area_list)):
    #             if args.exact_search:
    #                 title = a_list[i].get('title')
    #                 if args.search_keyword not in title:
    #                     continue # drop the news if the title doesn't contain the query exactly
    #
    #             # 지정 언론사가 아닌 기사는 pass
    #             infos = [info for info in info_list[i].find_all('a')]
    #             # print(infos)
    #
    #             # if not (any(press in infos[0].text for press in args.allowed_press) and all(press not in infos[0].text for press in args.excluded_press)):
    #             #     continue
    #
    #             # 뉴스 카테고리만 수집 (스포츠, 연예, 날씨 등 제외)
    #             if infos[-1].get('href').split("//")[1].startswith("news") and infos[-1].get('href') not in crawled_news:
    #                 crawled_news.append(infos[-1].get('href'))

    crawled_news = []  # 기사 중복 방지를 위한 url list
    for i in range(len(area_list)):
        infos = [info for info in info_list[i].find_all('a')]
        if infos[-1].get('href').split("//")[1].startswith("news") and infos[-1].get('href') not in crawled_news:
            crawled_news.append(infos[-1].get('href'))
        news_dict[idx] = {}
        news_dict[idx]['title'] = a_list[i].get('title')
        news_dict[idx]['press'] = infos[0].text
        news_dict[idx]['url'] = infos[-1].get('href')
        idx += 1
    current_page += 1

    print(news_dict)
    #         pbar.update(1)
    #
    # pages = soup.find('div', {'class' : 'sc_page_inner'})
    # # print("1 p.text:", p.text)
    # for p in pages.find_all('a'):
    #     print("p.text:", p.text)
    #     if p.text == str(current_page):
    #         next_page_url = 'https://search.naver.com/search.naver' + p.get('href')
    #         print("p.get('href'):", p.get('href'))
    #         print("next_page_url:", next_page_url)
    #         req = requests.get(next_page_url, headers=headers)
    #         soup = BeautifulSoup(req.text, 'html.parser')
    #         break

    # Article content / publish_date / modify_date / reaction
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(args.webdriver_path, options=options)

    for idx in tqdm(range(len(a_list)), desc='Crawling article content'):
        driver.get(news_dict[idx]['url'])
        time.sleep(1)

        # redirect 되는 기사 pass
        if driver.current_url.split("//")[1].startswith("news"):
            news_dict[idx]['url'] = driver.current_url
            req = requests.get(news_dict[idx]['url'], headers=headers)
            soup = BeautifulSoup(req.text, 'html.parser')

            # 기사 내용
            content_div = soup.find('div', {'class' : '_article_body_contents'})
            content = content_div.get_text()
            content = content.replace("\n", "")
            content = content.replace("\t", "")
            content = content.replace("// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}", "")
            news_dict[idx]['content'] = content

            # 기사 작성/수정 시간
            sponsor_div = soup.find('div', {'class' : 'sponsor'})
            dates = sponsor_div.find_all('span', {'class' : 't11'})

            news_dict[idx]['publish_date'] = dates[0].string
            if len(dates) == 2:
                news_dict[idx]['modify_date'] = dates[1].string

            # 기사 반응
            try:
                reaction_good = driver.find_element_by_xpath('//*[@id="spiLayer"]/div[1]/ul/li[1]/a/span[2]').get_attribute('innerHTML')
                reaction_warm = driver.find_element_by_xpath('//*[@id="spiLayer"]/div[1]/ul/li[2]/a/span[2]').get_attribute('innerHTML')
                reaction_sad = driver.find_element_by_xpath('//*[@id="spiLayer"]/div[1]/ul/li[3]/a/span[2]').get_attribute('innerHTML')
                reaction_angry = driver.find_element_by_xpath('//*[@id="spiLayer"]/div[1]/ul/li[4]/a/span[2]').get_attribute('innerHTML')
                reaction_want = driver.find_element_by_xpath('//*[@id="spiLayer"]/div[1]/ul/li[5]/a/span[2]').get_attribute('innerHTML')
            except:
                reaction_good = 0
                reaction_warm = 0
                reaction_sad = 0
                reaction_angry = 0
                reaction_want = 0

            news_dict[idx]['reaction_good'] = reaction_good
            news_dict[idx]['reaction_warm'] = reaction_warm
            news_dict[idx]['reaction_sad'] = reaction_sad
            news_dict[idx]['reaction_angry'] = reaction_angry
            news_dict[idx]['reaction_want'] = reaction_want

        else:
            del news_dict[idx]
            # Save data to file
        news_df = DataFrame(news_dict).T
        if args.output_file_path.endswith('.csv'):
            news_df.to_csv(args.output_file_path, encoding='utf-8', index=False, mode='a')
        elif args.output_file_path.endswith('.xlsx'):
            news_df.to_excel(args.output_file_path, index=False)
        elif args.output_file_path.endswith('.json'):
            news_df.to_json(args.output_file_path, orient='records', force_ascii=False)

    driver.close()

    print('Done! saved crawling result to {}'.format(args.output_file_path))