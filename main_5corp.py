import os
import argparse
import platform
import pandas as pd

from crawling_5corp import crawling

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--search_keyword', type=str,
                        default=None,
                        help='Keyword to search')
    parser.add_argument('--max_page', type=int,
                        default=1000,
                        help='Maximum news page to search')
    parser.add_argument('--exact_search', type=bool,
                        default=True,
                        help='Exact search or not')
    parser.add_argument('--start_date', type=str,
                        default=None,
                        help='Start date to search, expected form: YYYYMMDD')
    parser.add_argument('--end_date', type=str,
                        default=None,
                        help='End date to search, expected form: YYYYMMDD')
    parser.add_argument('--search_list_path', type=str,
                        default='./data/id_code.csv',
                        help='Allowed press to search')
    parser.add_argument('--allowed_press_path', type=str,
                        default='./data/allowed_press.txt',
                        help='Allowed press to search')
    parser.add_argument('--excluded_press_path', type=str,
                        default='./data/excluded_press.txt',
                        help='Excluded press while searching')
    parser.add_argument('--webdriver_path', type=str,
                        default=None,
                        help='spectific webdriver to use for selenium')
    parser.add_argument('--output_file_path', type=str,
                        default='./result_3',
                        help='Result path')

    args = parser.parse_args()

    # Arguments preprocessing
    # Check if only one of start_date and end_date is specified
    if args.start_date is None and args.end_date is None:
        pass
    elif args.start_date is not None and args.end_date is not None:
        pass
    else:
        print('Please specify both start_date and end_date or none of them')
        exit(1)

    if args.webdriver_path is None:
        # Use default webdriver
        if platform.system() == 'Darwin':
            if platform.machine() == 'x86_64':
                args.webdriver_path = './webdriver/chromedriver_darwin_x86'
            elif platform.machine() == 'arm64':
                args.webdriver_path = './webdriver/chromedriver_darwin_arm64'
        elif platform.system() == 'Linux':
            args.webdriver_path = './webdriver/chromedriver_linux'
        elif platform.system() == 'Windows':
            args.webdriver_path = './webdriver/chromedriver.exe'

    with open(args.allowed_press_path, 'r', encoding='UTF8') as f:
        args.allowed_press = f.readlines()
        args.allowed_press = [x.strip() for x in args.allowed_press]

    with open(args.excluded_press_path, 'r', encoding='UTF8') as f:
        args.excluded_press = f.readlines()
        args.excluded_press = [x.strip() for x in args.excluded_press]

    # make dir for output_file_path if directory not exists
    if not os.path.exists(os.path.dirname(args.output_file_path)):
        os.makedirs(os.path.dirname(args.output_file_path))
    
    if args.search_list_path is None:
        if args.search_keyword is None:
            print('Please specify search keyword')
            exit(1)
        else:
            args.search_keyword = args.search_keyword.replace(' ', '+')
        crawling(args)

    else:
        df = pd.read_csv(args.search_list_path)
        
        for i in range(len(df)):
            args.search_keyword = df.loc[i, 'name']
            # args.search_keyword = '대한제분'
            args.search_keyword = args.search_keyword.replace(' ', '+')
            args.stock_num = df.loc[i, 'num']
            args.output_file_path = './result_3/' + 'crawling_result_' + str(args.stock_num) + '_' + str(args.search_keyword) + '.csv'

            date_list = pd.date_range(start='2018-01-02', end='2021-07-30')
            for date in date_list:
                args.start_date = date.strftime("%Y%m%d")
                args.end_date = date.strftime("%Y%m%d")
                crawling(args)


