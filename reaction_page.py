from discord.ext import commands
from database import DataBase
import discord


class Reactions(commands.Cog):
    emojis = ['\N{open book}', '\N{shield}']

    def __init__(self, bot):
        self.bot = bot
        self.book_navigation = ['\N{black left-pointing triangle}',
                                '\N{black right-pointing triangle}',
                                ]

        self.reaction = None
        self.database = DataBase('database.db')

    def book(self, champion_id):
        pass

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        users = await reaction.users().flatten()

        self.reaction = reaction

        if user != self.bot.user and self.bot.user in users:

            embed_message, = reaction.message.embeds

            channel_message_from = reaction.message.channel

            game_title = embed_message.title

            if reaction.emoji == '▶':

                video_link, = self.database.get_video_url(game_title.lower())
                await channel_message_from.send(video_link)

                await reaction.remove(user)

            elif reaction.emoji == "📖":

                await reaction.remove(user)

            elif reaction.emoji == '❌':

                await reaction.remove(user)




            elif reaction.emoji == "🗑":
                await reaction.remove(user)
                await reaction.message.delete()
