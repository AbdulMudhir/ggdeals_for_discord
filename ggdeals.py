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

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'We have logged in as {self.bot.user}\n')
        self.channel = self.bot.get_channel(702208238149435533)
        await self.send_deals()

    def deals(self):
        deals_found = {}

        ggdeals_best_deal = requests.get(self.link, headers=header).content

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
                                  'genre': genre}

        return deals_found

    async def get_posted_deals(self):

        chat_logs = {}

        msg = await self.channel.history(limit=1000).flatten()

        for messages in msg:

            embed_content = messages.embeds
            for content in embed_content:
                title = content.title  # title of the embed
                chat_logs[title] = messages.id

        return chat_logs

    async def send_deals(self):

        retrieve_log = await self.get_posted_deals()

        price_sorted = {game_title:game_info for game_title, game_info in
                        sorted(self.deals().items(), key=lambda deal: deal[1].get('price'), reverse=True)}

        print(price_sorted)
        #print(price_sorted)

        # for game_title, game_info in self.deals().items():
        #     print(game_info.get('platform_image'))
        #     embed = discord.Embed(
        #         title=game_title,
        #         description=f" **Price:** {game_info.get('price')}\n"
        #                     f"**Platform:** {game_info.get('platform')}\n"
        #                     f" **Genre:** {game_info.get('genre')}",
        #         colour=2470660,
        #         url=game_info.get('direct_link'))
        #     embed.set_thumbnail(url=game_info.get('game_image'))
        #     await self.channel.send(embed=embed)

    @staticmethod
    def check_lazy_load(class_):
        # check if the image link are been hidden
        return type(class_) == list


if __name__ == "__main__":
    bot.add_cog(GGDeals(bot))
    bot.remove_command('help')
    bot.run('NjAyNDM5MTM0ODA3NTg4ODg1.Xp8s_g.Ktwjkv7c-F5DyjySND9gftynsvY')
