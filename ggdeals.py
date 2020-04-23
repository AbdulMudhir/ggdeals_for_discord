import requests
from bs4 import BeautifulSoup as bs4
from discord.ext import commands
from discord.ext import tasks
import discord
from database import DataBase

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'}

bot = commands.Bot(command_prefix=".")


class GGDeals(commands.Cog):

    def __init__(self, bot_client):
        self.bot = bot_client
        self.token = ""
        self.link = "https://gg.deals/deals/best-deals/"
        self.posted_deals = ''
        self.current_deals = ''
        self.database = DataBase('database.db')

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'We have logged in as {self.bot.user}\n')
        self.channel = self.bot.get_channel(702208238149435533)
        self.server_bot_channel = self.bot.get_channel(557662591942524930)
        self.start_sending.start()

    def deals(self):
        deals_found = {}

        for page_number in range(1, 3):

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
                # check if this is the lowest deal
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
                                      'percentage': percentage,
                                      'historical_low': historical}

        return deals_found

    async def get_posted_deals(self):

        messages = await self.channel.history(limit=50).flatten()

        # await self.channel.delete_messages(messages)
        # get the title of each embeds and the message id
        posted_deals = {message.embeds.pop().title: message.id for message in messages}

        return posted_deals

    async def send_deals(self):
        # get the posted deals
        self.posted_deals = await self.get_posted_deals()
        # get the deals from the website
        self.current_deals = self.deals()

        server_wish_list = self.database.view_wish_list()

        for game_title, game_info in self.current_deals.items():

            if game_title not in self.posted_deals:

                formatted_game_list = [games[0] for games in server_wish_list]

                wish_deal_found = ' '.join([game for game in formatted_game_list if game in game_title.lower()])

                if wish_deal_found:
                    await self.send_users_wish_list(wish_list_game=wish_deal_found, game_info=game_info,
                                                    game_title=game_title)

                price = game_info.get('price')
                percentage = game_info.get('percentage')

                if price == "Free":

                    price_formatted = f"{price} ({percentage})"
                    colour = 181488
                elif game_info.get('historical_low'):

                    price_formatted = f"{price} ({percentage})"
                    colour = 2470660
                else:
                    price_formatted = f"{price} ({percentage})"
                    colour = 8618883

                embed = discord.Embed(
                    title=game_title,
                    description=f"**Price:** {price_formatted}\n"
                                f"**Previous Price:** {game_info.get('p_price')}\n"
                                f"**Platform:** {game_info.get('platform')}\n"
                                f"**Genre:** {game_info.get('genre')}",
                    colour=colour,
                    url=game_info.get('direct_link'))
                embed.set_thumbnail(url=game_info.get('game_image'))
                await self.channel.send(embed=embed)

        # update the posted deals that have been sent across
        self.posted_deals = await self.get_posted_deals()

    @tasks.loop(hours=1)
    async def start_sending(self):
        pass
        # await self.send_deals()
        # await self.remove_outdated_deals()

    async def send_users_wish_list(self, game_title, game_info, wish_list_game):

        user_with_game_list = self.database.get_user_with_game_list(wish_list_game)
        formatted_user_list = [user_id[0] for user_id in user_with_game_list]

        for user_id in formatted_user_list:

            user = self.bot.get_user(user_id)

            price = game_info.get('price')
            percentage = game_info.get('percentage')

            if price == "Free":
                price_formatted = f"{price} ({percentage})"
                colour = 181488
            elif game_info.get('historical_low'):

                price_formatted = f"{price} ({percentage})"
                colour = 2470660
            else:
                price_formatted = f"{price} ({percentage})"
                colour = 8618883

            embed = discord.Embed(
                title=game_title.title(),
                description=f" **Price:** {price_formatted}\n"
                            f" **Previous Price:** {game_info.get('p_price')}\n"
                            f"**Platform:** {game_info.get('platform')}\n"
                            f" **Genre:** {game_info.get('genre')}",
                colour=colour,
                url=game_info.get('direct_link'))

            embed.set_thumbnail(url=game_info.get('game_image'))

            await self.server_bot_channel.send(f"{user.mention} {game_title.title()} was from your  wish list",
                                               embed=embed)

    @commands.command()
    async def wish(self, ctx, *args):

        user = ctx.author
        game_title = ' '.join(args).strip().lower()

        if game_title:
            if self.database.game_exist(user, game_title):
                await ctx.channel.send(f'{game_title.title()} is already on your wish list', delete_after=5)
            else:
                self.database.add_wish_list(user, game_title)
                await ctx.channel.send(f'{game_title.title()} has been added to your wish list')

    @commands.command()
    async def view(self, ctx):
        user = ctx.author
        users_wish_list = self.database.view_user_wish_list(user)

        formatted_user_list = '\n'.join(
            [f"#{number} {games[0].title()}" for number, games in enumerate(users_wish_list, start=1)])

        embed = discord.Embed(
            title=f"{user.name}#{user.discriminator}",
            description=formatted_user_list,
            colour=2470660,

        )
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def remove(self, ctx, *args):

        user = ctx.author
        game_title = ' '.join(args).strip().lower()

        if game_title:

            if self.database.game_exist(user, game_title):
                self.database.remove_wish_list(user, game_title)
                await ctx.channel.send(f'{game_title.title()} has been removed from your wish list')
            else:
                await ctx.channel.send(f'{game_title.title()} does not exist in your wish list', delete_after=5)

    @commands.command()
    async def search(self, ctx, *args):

        game_title = '+'.join(args)

        if args:
            ggdeals_best_deal = requests.get(f"https://gg.deals/games/?title={game_title}", headers=header).content
            soup = bs4(ggdeals_best_deal, 'html.parser')

            game_card = soup.find('div', class_='with-badges')

            game_name = game_card.find_next('a', class_='ellipsis title').text
            game_picture = game_card.find_next('img').get('src')

            current_price = game_card.find_next('span', class_="numeric").text
            direct_link = f"https://gg.deals{game_card.find_next('a', class_='ellipsis title').get('href')}"
            tag = game_card.find_next('div', class_="tag-tags")
            genre = tag.find_next('span', class_='value').span.get('title')
            historical = "Historical low" in str(game_card)

            print(current_price, direct_link,  historical, test, game_name, game_picture)



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
