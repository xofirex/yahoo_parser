import pandas as pd
from driver.selenium import Driver
import time
from datetime import datetime, timedelta
import os

CompanyList = [
    'PD',
    'ZUO',
    'PINS',
    'ZM',
    'PVTL',
    'DOCU',
    'CLDR',
    'RUN',
]


def company_stats(company, period):
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{company}?period1=0&period2={period}&interval=1d&events=history&includeAdjustedClose=true"
        df_stats = pd.read_csv(url)
        df_stats_3day = pd.read_csv(url, usecols=["Date", "Close"])
        df_stats["Date"] = pd.to_datetime(df_stats["Date"])
        df_stats_3day["Date"] = pd.to_datetime(df_stats["Date"])
        df_stats_3day.rename(columns={'Date': 'New date', 'Close': 'Close before 3 day'}, inplace=True)
        df_stats["New date"] = df_stats["Date"] - timedelta(days=3)
        df = pd.merge(df_stats, df_stats_3day, on="New date", how="left")
        df["3day_before_change"] = df["Close"] / df["Close before 3 day"]
        df = df.drop(['Close before 3 day', 'New date'], axis='columns')
        df.to_csv(f"./yahoo_csv/{company}.csv", index=False)
        company_news_save(company)
    except Exception as e:
        print(e)


def company_news_save(company):
    company_news = []
    with Driver() as driver:
        driver.get(f'https://finance.yahoo.com/quote/{company}/')
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, 1820)")
        for elem in driver.find_elements_by_xpath('//div[@id="quoteNewsStream-0-Stream"]/ul/*'):
            company_news.append({"url": elem.find_element_by_xpath('.//div/div/div/h3/a').get_attribute('href'),
                                 "title": elem.find_element_by_xpath('.//div/div/div/h3').text})
    df = pd.DataFrame(company_news)
    df.to_csv(f"./yahoo_csv/{company}_news.csv", index=False)


period = int((datetime.now() - datetime(1970, 1, 1)).total_seconds())
os.mkdir("yahoo_csv")
for company in CompanyList:
    company_stats(company, period)
