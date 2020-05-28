import discord
from discord import Embed
from discord.ext import commands
import json

bot = commands.Bot(command_prefix="")


class DiscordEmbed:
    def __init__(self, channel, embed):
        self.channel = channel
        self.embed = embed


# Embeds
async def checkEmbeds():
    # Get embeds from the config
    discord_embeds = []
    channels = []
    with open('config.json', encoding='utf-8') as json_file:
        data = json.load(json_file)

        for configchannel in data['Embeds']:
            for e in data['Embeds'][configchannel]:
                channel = bot.get_channel(int(configchannel))

                if channel:
                    channels.append(channel)

                if 'color' in e:
                    e['color'] = int(e['color'].replace("#", ""), 16)

                try:
                    embed = discord.Embed.from_dict(e)
                except Exception as error:
                    print(f"Error while getting embed from config - {error}")
                    continue

                discord_embeds.append(DiscordEmbed(channel, embed))

    # Check channels for the embeds
    channels = set(channels)
    for channel in channels:
        channel_embeds = [embed for embed in discord_embeds if embed.channel.id is channel.id]

        with open('config.json') as json_file:
            data = json.load(json_file)

            history_limit = data['BotConfig']['max_message_checks']

            current_botembeds = []
            async for message in channel.history(limit=history_limit):
                if (message.author == bot.user) and (len(message.embeds) >= 1):
                    current_botembeds.append(message)
            # Reverse because it reads from the bottom up
            current_botembeds.reverse()

            embed_index = 0
            for channel_embed in channel_embeds:
                embed = channel_embed.embed
                current_embed_message = None
                current_embed = None
                found_embed = False
                try:
                    current_embed_message = current_botembeds[embed_index]
                    current_embed = current_embed_message.embeds[0]
                    found_embed = True
                except IndexError:
                    print("No message for this embed_index yet")

                embed_index += 1

                if found_embed:
                    print("Checking for differences...")

                    # Difference checks
                    authornamecheck = embed.author.name
                    if authornamecheck == "":
                        authornamecheck = Embed.Empty

                    if current_embed.title != embed.title:
                        print("title difference")
                    elif current_embed.description != embed.description:
                        print("description difference")
                    elif current_embed.color != embed.color:
                        print("color difference")
                    elif current_embed.timestamp != embed.timestamp:
                        print("timestamp difference")
                    elif current_embed.image.url != embed.image.url:
                        print("image difference")
                    elif current_embed.video.url != embed.video.url:
                        print("video difference")
                    elif current_embed.thumbnail.url != embed.thumbnail.url:
                        print("thumbnail difference")
                    elif (current_embed.footer.text != embed.footer.text) or (current_embed.footer.icon_url != embed.footer.icon_url):
                        print("footer difference")
                    elif (current_embed.author.name != authornamecheck) or (current_embed.author.url != embed.author.url) or (current_embed.author.icon_url != embed.author.icon_url):
                        print("author difference")
                    elif current_embed.fields != embed.fields:
                        if (current_embed.fields == Embed.Empty) and (embed.fields != Embed.Empty):
                            print("fields difference - old is empty")
                        elif (current_embed.fields != Embed.Empty) and (embed.fields == Embed.Empty):
                            print("fields difference - new is empty")
                        elif len(current_embed.fields) != len(embed.fields):
                            print("fields difference - len")
                        else:
                            field_i = 0
                            found_difference = False
                            for current_field in current_embed.fields:
                                field = embed.fields[field_i]

                                if current_field.name != field.name:
                                    print("fields difference - name")
                                    found_difference = True
                                    break
                                elif current_field.value != field.value:
                                    print("fields difference - value")
                                    found_difference = True
                                    break
                                elif current_field.inline != field.inline:
                                    if (current_field.inline is not False) and (field.inline is not Embed.Empty):
                                        print("fields difference - inline")
                                        found_difference = True
                                        break
                                field_i += 1
                            if not found_difference:
                                print("No differences!")
                                continue
                    else:
                        print("No differences!")
                        continue
                    await current_embed_message.edit(embed=embed)
                else:
                    print("No current_embed, sending embed")
                    await channel.send(embed=embed)


@bot.event
async def on_ready():
    print("EmbedBot has (re)connected to Discord!")

    print("> Checking the embeds! <")
    await checkEmbeds()
    print("> Done checking the embeds! <")
    print("\n")


# Run bot
with open('config.json') as json_file:
    data = json.load(json_file)

    token = data['BotConfig']['token']
    if token:
        bot.run(token)
