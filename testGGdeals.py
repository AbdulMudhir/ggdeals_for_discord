import requests
from bs4 import BeautifulSoup as bs4


def key_shop_prices(game_name):
    key_shop_page = requests.get(f"https://gg.deals/game/{game_name}/?tab=keyshops")
    soup = bs4(key_shop_page.content, "html.parser")

    key_shop_deals = soup.find_all("div", class_="game-deals-item")
    for deal in key_shop_deals:

        direct_link_find = deal.find('a', class_="shop-link")
        direct_link = direct_link_find.get('href')
        deal_price = deal.find('span', class_="numeric").text
        company = direct_link_find.img.get('alt')

        print(deal_price, direct_link)



key_shop_prices("grand-theft-auto-v")




