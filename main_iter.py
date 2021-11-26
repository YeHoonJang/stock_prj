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
        df = pd.read_csv(args.search_list_path)
        if not os.path.isfile(args.crawling_list_path):
            tmp = pd.DataFrame(columns=['name', 'url'])
            tmp.to_csv(args.crawling_list_path, index=False, encoding='utf-8-sig')

        for i in range(len(df)):
            args.search_keyword = df.loc[i, 'name']
            args.search_keyword = args.search_keyword.replace(' ', '+')

            date_list = pd.date_range(start='2018-01-02', end='2021-07-30')
            with tqdm.tqdm(total=len(date_list), desc=f"{args.search_keyword} News List Crawling:") as date_bar:
                for date in date_list:
                    args.start_date = date.strftime("%Y%m%d")
                    args.end_date = date.strftime("%Y%m%d")
                    crawling_news_list(args)
                    date_bar.update(1)
                    time.sleep(5)


    # news crawling
    if args.crawling_news is True:
        news_list = pd.read_csv(args.crawling_list_path)

        names = list(set(news_list['name']))
        for name in names:
            info_df = pd.read_csv(args.search_list_path)
            num = info_df.loc[info_df['name']== name, 'num'].item()
            kind = info_df.loc[info_df['name'] == name, 'class'].item()
            urls = [url for url in news_list.loc[news_list['name'] == name, 'url']]
            args.output_file_path = os.path.join(os.getcwd(), 'result', f'crawling_result_{str(num)}_{str(name)}.csv')
            crawling_news(args, name, num, kind, urls)

            



