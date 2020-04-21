import requests
import discord
from bs4 import BeautifulSoup as bs4

header = {'user-agent':
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'}

ggdeals_best_deal = requests.get("https://gg.deals/deals/best-deals/", headers=header).content

soup = bs4(ggdeals_best_deal, 'html.parser')

find_deal = soup.find_all('div', class_='deal-list-item')

for deal in find_deal:
    title = deal.find_next('a', class_="ellipsis title").text
    current_price = deal.find_next('span', class_="numeric").text
    previous_price = deal.find_next('span', class_="bottom").text
    direct_link = f"https://gg.deals{deal.find_next('a', class_='shop-link').get('href')}"
    platform = deal.find_next('a', class_="shop-link").img.get('alt')


    image_class = deal.find_next('a', class_="main-image").img.get('class')

    print(image_class)
    image = deal.find_next('a', class_="main-image").img

    # print( deal.find_next('a', class_="shop-link").img)
    platform_image = deal.find_next('a', class_="shop-link").img.get('data-src')

    # print(f'{title}\n{current_price}\n{previous_price}\n{direct_link}\n{image}\n{platform}\n{platform_image}')


def check_lazy_load(class_):
    return class_ == 'lazyload'
