import os
import json
import requests
from datetime import *
from news_model import News
from twilio.rest import Client

# AlphaVantage API Info
ALPHAVANTAGE_API_KEY = os.environ.get("AV_KEY")
FUNCTION = "TIME_SERIES_DAILY"
STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

# News API info
NEWS_API_KEY = os.environ.get("NEWS_KEY")

# Twilio Account Information
auth_token = os.environ.get("AUTH_TOKEN")
account_sid = os.environ.get("ACCOUNT_SID")

# API EndPoints
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

# Alphavantage Parameters & Response
stock_parameter = {
    "function": FUNCTION,
    "symbol": STOCK_NAME,
    "apikey": ALPHAVANTAGE_API_KEY,
}

response = requests.get(url=STOCK_ENDPOINT, params=stock_parameter)
response.raise_for_status()
alphavantage_data = response.json()

# News Parameters & Response
news_parameter = {
    "q": COMPANY_NAME[0:5].lower(),
    "apiKey": NEWS_API_KEY
}

response = requests.get(url=NEWS_ENDPOINT, params=news_parameter)
response.raise_for_status()
news_data = response.json()

# Optional JSON data to Limit Free Trail Daily Limit
# with open("avdata.json") as file:
#     alphavantage_data = json.load(file)

daily = alphavantage_data["Time Series (Daily)"]
last_refreshed_date = alphavantage_data["Meta Data"]["3. Last Refreshed"]

# Get yesterday's closing stock price

# previous_day = date(2024, 3, 6)
lrd_year = int(last_refreshed_date[0:4])
lrd_month = int(last_refreshed_date[5:7])
lrd_day = int(last_refreshed_date[8:10])

current_day = date(lrd_year, lrd_month, lrd_day)
yesterday_date = str(current_day - timedelta(days=1))
day_before = str(current_day - timedelta(days=2))
print("Current :", current_day)
print("Yesterday: ", yesterday_date)
print("Day Before: ", day_before)

for day in daily:
    if day == yesterday_date:
        yesterday_closing_price = alphavantage_data["Time Series (Daily)"][day]["4. close"]
        yesterday_value = float(yesterday_closing_price)
        print("Yesterday Closing Price :", yesterday_closing_price)

# Gets the closing price for day before
day_before_closing_price = "0.00"

for day in daily:
    if day == day_before:
        day_before_closing_price = alphavantage_data["Time Series (Daily)"][day]["4. close"]
        day_before_value = float(day_before_closing_price)

# Find the positive difference
postive_difference = round(abs(yesterday_value - day_before_value), 3)

# percentage difference in price between yesterday and day before closing price

percentage_difference = round((yesterday_value - day_before_value) / day_before_value, 3)
print("Percentage Diff : ", percentage_difference)

# percentage is greater than 5 get headline and description send via Twilio.

if percentage_difference > 0.05:
    print("Get News")

    get_articles = news_data["articles"]

    articles_list = []
    news_counter = 0

    for article in get_articles:
        if news_counter < 3:
            article_title = article["title"]
            article_description = article["description"]
            news_info = News(article_title, article_description)
            articles_list.append(news_info)
            news_counter += 1
    print(*articles_list, sep="")

    # Send each article as a separate message via Twilio.

    for article_message in articles_list:
        client = Client(account_sid, auth_token)
        message = client.messages \
            .create(
            body=f"{STOCK_NAME}: \n {article_message}",
            from_="+18662228888",
            to="+16785554444"
        )
    print(message.sid)