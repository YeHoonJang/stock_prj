import os
import argparse
import platform
import pandas as pd
import tqdm
import time

from crawling import crawling_news_list, crawling_news

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--search_keyword', type=str, default=None, help='Keyword to search')
    parser.add_argument('--start_date', type=str, default=None, help='Start date to search, expected form: YYYYMMDD')
    parser.add_argument('--end_date', type=str, default=None, help='End date to search, expected form: YYYYMMDD')
    parser.add_argument('--search_list_path', type=str, default='./data/id_code.csv', help='Allowed press to search')
    parser.add_argument('--webdriver_path', type=str, default=None, help='spectific webdriver to use for selenium')
    parser.add_argument('--output_file_path', type=str, default='./result', help='Result path')
    parser.add_argument('--crawling_list_path', type=str, default='./data/crawling_list.csv', help='Crawling List Path')
    parser.add_argument('--start_index', type=int, default=0, help='Crawling Start index')
    parser.add_argument('--dart_class', type=str, default=None, help='DART Class ex) "배당", "장래사업계획", "영업잠정실적"')
    parser.add_argument('--dart_id', type=int, default=None, help='DART id')
    parser.add_argument('--crawling_news_list', action='store_true')
    parser.add_argument('--crawling_news', action='store_true')

    args = parser.parse_args()

    # Arguments preprocessing
    if args.webdriver_path is None:
        if platform.system() == 'Darwin':
            if platform.machine() == 'x86_64':
                args.webdriver_path = './webdriver/chromedriver_darwin_x86'
            elif platform.machine() == 'arm64':
                args.webdriver_path = './webdriver/chromedriver_darwin_arm64'
        elif platform.system() == 'Linux':
            args.webdriver_path = './webdriver/chromedriver_linux'
        elif platform.system() == 'Windows':
            args.webdriver_path = './webdriver/chromedriver.exe'


    # make dir for output_file_path if directory not exists
    if not os.path.exists(os.path.dirname(args.output_file_path)):
        os.makedirs(os.path.dirname(args.output_file_path))

    # url crawling
    if args.crawling_news_list is True:
        dart_df = pd.read_csv("./data/dart_data.csv") 
        dart_df = dart_df[dart_df['구분']==args.dart_class]
        df = pd.read_csv(args.search_list_path)

        if not os.path.isfile(args.crawling_list_path):
            tmp = pd.DataFrame(columns=['name', 'url', 'id'])
            tmp.to_csv(args.crawling_list_path, index=False, encoding='utf-8-sig')

        dart_class_dict = {"배당": "배당", "장래사업계획": "장래 사업 경영 계획", "영업잠정실적": "영업 잠정 실적"}
        for i in range(len(dart_df)):
            # id 0 / 날짜 2 / 기업명 6 / 구분 7
            args.search_keyword = dart_df.iloc[i, 6]
            date = dart_df.iloc[i, 2]
            args.dart_id = dart_df.iloc[i, 0]
            args.start_date = date.replace("-", "")
            args.end_date = date.replace("-", "")
            print(f"Start Crawling {args.search_keyword} News Url...")
            crawling_news_list(args)
            time.sleep(3)


    # news crawling
    if args.crawling_news is True:
        news_list = pd.read_csv(args.crawling_list_path)
        names = list(set(news_list['name']))
        dart_df = pd.read_csv("./data/dart_data.csv")

        for i in range(len(news_list)):
            # name 0 / url 1 / id 2
            info_df = pd.read_csv(args.search_list_path)
            name = news_list.iloc[i, 0]
            args.dart_id = news_list.iloc[i, 2]
            url = [news_list.iloc[i, 1]]
            num = info_df.loc[info_df['name']== name.replace('+', ' '), 'num'].item()
            kind = info_df.loc[info_df['name'] == name.replace('+', ' '), 'class'].item()
            args.output_file_path = os.path.join(os.getcwd(), 'result_dart', f'crawling_result_{str(num)}_{str(name)}.csv')
            print(f"Start Crawling {name} News ...")
            crawling_news(args, name, num, kind, url)

            



