import requests
from bs4 import BeautifulSoup

def get_latest_yahoo_news():
    # URL of Yahoo News
    url = 'https://news.yahoo.com/'

    # Sending a request to the website
    response = requests.get(url)
    if response.status_code != 200:
        return "Failed to retrieve news"

    # Parsing the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Finding news items - assuming they are under <h3> tags with class 'Mb(5px)'
    news_items = soup.find_all('h3', class_='Mb(5px)')

    # Extracting the first 5 news titles and URLs
    news_list = []
    for item in news_items[:5]:
        title = item.text.strip()
        link = item.find('a', href=True)['href']
        news_list.append({'title': title, 'link': link})
    if not news_list:
        return "Failed to retrieve news"
    return news_list

# Getting the latest news from Yahoo News
latest_news = get_latest_yahoo_news()
print(latest_news)