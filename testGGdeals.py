import requests
from bs4 import BeautifulSoup as bs4


def key_shop_prices(game_name):
    key_shop_page = requests.get(f"https://gg.deals/game/{game_name}/?tab=keyshops")
    soup = bs4(key_shop_page.content, "html.parser")

    key_shop_deals = soup.find_all("div", class_="game-deals-item")



    key_shop = {}

    for deal in key_shop_deals:

        direct_link_find = deal.find('a', class_="shop-link")
        direct_link = f"https://gg.deals{direct_link_find.get('href')}"
        deal_price = deal.find('span', class_="numeric").text
        company = direct_link_find.img.get('alt')

        discount = deal.find("span", class_="before-price-wrapper")
        if discount is None:
            discount = "None"
        else:
            discount = discount.text

        if key_shop.get(company) is None:
            key_shop[company] = [direct_link, deal_price, discount]
        else:
            pass

    return key_shop

t = key_shop_prices("grand-theft-auto-v")


print(t)

