import requests
import discord
from bs4 import BeautifulSoup as bs4

header = {'user-agent':
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'}


#


def check_lazy_load(class_):
    # check if the image link are been hidden
    return type(class_) == list


def deals(link):

    deals_found = {}

    ggdeals_best_deal = requests.get(link, headers=header).content

    soup = bs4(ggdeals_best_deal, 'html.parser')

    find_deal = soup.find_all('div', class_='deal-list-item')

    for deal in find_deal:
        title = deal.find_next('a', class_="ellipsis title").text
        current_price = deal.find_next('span', class_="numeric").text
        previous_price = deal.find_next('span', class_="bottom").text
        direct_link = f"https://gg.deals{deal.find_next('a', class_='shop-link').get('href')}"
        platform = deal.find_next('a', class_="shop-link").img.get('alt')

        # get img tag from the html to check if  links are in the right attributes
        image_class = deal.find_next('a', class_="main-image").img.get('class')

        if not check_lazy_load(image_class):
            # check if the image link are been hidden
            game_image = deal.find_next('a', class_="main-image").img.get('src')
            platform_image = deal.find_next('a', class_="shop-link").img.get('src')

        else:
            game_image = deal.find_next('a', class_="main-image").img.get('data-src')
            platform_image = deal.find_next('a', class_="shop-link").img.get('data-src')

        deals_found[title] = {'price': current_price,
                              'p_price': previous_price,
                              'direct_link': direct_link,
                              'platform': platform,
                              'game_image': game_image,
                              'platform_image': platform_image}

    return deals_found


test = deals("https://gg.deals/deals/best-deals/")
print(test)
