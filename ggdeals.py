import requests
from bs4 import BeautifulSoup as bs4
from discord.ext import commands
from discord.ext import tasks
import discord

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'}

bot = commands.Bot(command_prefix="!")


class GGDeals(commands.Cog):

    def __init__(self, bot_client):
        self.bot = bot_client
        self.token = ""
        self.link = "https://gg.deals/deals/best-deals/"
        self.posted_deals = ''
        self.current_deals = ''

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'We have logged in as {self.bot.user}\n')
        self.channel = self.bot.get_channel(702208238149435533)
        self.start_sending.start()

    def deals(self):
        deals_found = {}

        for page_number in range(1, 2):

            ggdeals_best_deal = requests.get(f"https://gg.deals/deals/best-deals/?page={page_number}",
                                             headers=header).content

            soup = bs4(ggdeals_best_deal, 'html.parser')

            find_deal = soup.find_all('div', class_='deal-list-item')

            for deal in find_deal:

                title = deal.find_next('a', class_="ellipsis title").text
                current_price = deal.find_next('span', class_="numeric").text
                previous_price = deal.find_next('span', class_="bottom").text
                direct_link = f"https://gg.deals{deal.find_next('a', class_='shop-link').get('href')}"
                platform = deal.find_next('a', class_="shop-link").img.get('alt')
                deal_posted_date = deal.find_next('div', class_='time-tag').span.text
                genre = deal.find_next('div', class_='tag- ellipsis tag with-bull').span.text
                percentage = deal.find_next('span', class_="discount-badge badge").text
                historical = "Historical low" in str(deal)


                # get img tag from the html to check if  links are in the right attributes
                image_class = deal.find_next('a', class_="main-image").img.get('class')

                if not self.check_lazy_load(image_class):
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
                                      'platform_image': platform_image,
                                      'date_posted': deal_posted_date,
                                      'genre': genre,
                                      'percentage':percentage}

        return deals_found

    async def get_posted_deals(self):

        messages = await self.channel.history(limit=50).flatten()
        # get the title of each embeds and the message id
        posted_deals = {message.embeds.pop().title: message.id for message in messages}

        return posted_deals

    async def send_deals(self):
        # get the posted deals
        self.posted_deals = await self.get_posted_deals()
        # get the deals from the website
        self.current_deals = self.deals()

        for game_title, game_info in self.current_deals.items():
            pass

            # if game_title not in self.posted_deals:
            #     price = game_info.get('price')
            #
            #     price_formatted = f'```yaml\n{price}```' if price == "Free" else price
            #
            #     embed = discord.Embed(
            #         title=game_title,
            #         description=f" **Price:** {price_formatted}\n"
            #                     f" **Previous Price:** {game_info.get('p_price')}\n"
            #                     f"**Platform:** {game_info.get('platform')}\n"
            #                     f" **Genre:** {game_info.get('genre')}",
            #         colour=2470660,
            #         url=game_info.get('direct_link'))
            #     embed.set_thumbnail(url=game_info.get('game_image'))
            #     await self.channel.send(embed=embed)

        # update the posted deals that have been sent across
        self.posted_deals = await self.get_posted_deals()

    @tasks.loop(hours=1)
    async def start_sending(self):
        await self.send_deals()
        await self.remove_outdated_deals()

    async def remove_outdated_deals(self):

        for post, post_id in self.posted_deals.items():

            if post not in self.current_deals:
                # get the message that was sent
                get_message = await self.channel.fetch_message(post_id)
                # delete the message as the deal most likely expired
                await get_message.delete()

        # reset the deals found on gg.deals
        self.current_deals = ''

    @staticmethod
    def check_lazy_load(class_):
        # check if the image link are been hidden
        return type(class_) == list


if __name__ == "__main__":
    bot.add_cog(GGDeals(bot))
    bot.remove_command('help')
    bot.run(open('token_key', 'r').read())
