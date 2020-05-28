from datetime import datetime

import discord
from discord import Embed
from discord.ext import commands
import os
import json

bot = commands.Bot(command_prefix="")


class ConfigEmbed:
    def __init__(self, channelid, title=None, description=None, timestamp=None, color=None, footertext=None,
                 footericon=None, imageurl=None, thumbnailurl=None, authorname=None, authoricon=None, authorurl=None,
                 fields=None):
        self.channel = channelid
        self.title = title
        self.description = description
        self.timestamp = timestamp
        self.color = color
        self.footertext = footertext
        self.footericon = footericon
        self.image = imageurl
        self.thumbnail = thumbnailurl
        self.authorname = authorname
        self.authoricon = authoricon
        self.authorurl = authorurl
        self.fields = fields


class DiscordEmbed:
    def __init__(self, channel, embed):
        self.channel = channel
        self.embed = embed


# Embeds
async def checkEmbeds():
    # Get embeds from the config
    with open('config.json', encoding='utf-8') as json_file:
        data = json.load(json_file)

        embeds = []
        for channel in data['Embeds']:
            for e in data['Embeds'][channel]:
                footertext, footerurl, authorname, authorimage, authorurl, title, color, desc, imageurl, timestamp, \
                thumbnailurl = None, None, None, None, None, None, None, None, None, None, None

                # Footer and author
                if 'footer' in e:
                    if 'text' in e['footer']:
                        footertext = e['footer']['text']
                    if 'icon_url' in e['footer']:
                        footerurl = e['footer']['icon_url']
                if 'author' in e:
                    if 'name' in e['author']:
                        authorname = e['author']['name']
                    if 'image' in e['author']:
                        authorimage = e['author']['image']
                    if 'url' in e['author']:
                        authorurl = e['author']['url']

                # Fields
                fields = []
                if 'fields' in e:
                    for field in e['fields']:
                        if ('title' in field) and ('content' in field):
                            fieldtitle = field['title']
                            fieldcontent = field['content']
                            if not 'inline' in field:
                                fieldinline = True
                            else:
                                fieldinline = field['inline']

                            fields.append({"title": fieldtitle, "content": fieldcontent, "inline": fieldinline})

                # Standard keys
                if 'title' in e:
                    title = e['title']
                if 'color' in e:
                    color = e['color'].replace("#", "")
                if 'description' in e:
                    desc = e['description']
                if 'timestamp' in e:
                    try:
                        timestamp = datetime.strptime(e['timestamp'], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        print("Couldn't get timestamp from embed. Timestamp '" + e['timestamp'] + "' doesn't match the "
                              "format '%Y-%m-%d %H:%M:%S'")
                if 'image' in e:
                    imageurl = e['image']
                if 'thumbnail' in e:
                    thumbnailurl = e['thumbnail']

                embed = ConfigEmbed(channelid=channel, title=title, color=color, description=desc,
                                    imageurl=imageurl, thumbnailurl=thumbnailurl, authoricon=authorimage,
                                    authorname=authorname, authorurl=authorurl, footertext=footertext,
                                    footericon=footerurl, fields=fields, timestamp=timestamp)

                embeds.append(embed)

    # Send/check the embeds
    discord_embeds = []
    channels = []
    for e in embeds:
        channel = bot.get_channel(int(e.channel))

        if channel:
            channels.append(channel)

            title = Embed.Empty
            if e.title:
                title = e.title
            description = Embed.Empty
            if e.description:
                description = e.description
            color = None
            if e.color:
                color = discord.Color(value=int(e.color, 16))
            timestamp = None
            if e.timestamp:
                timestamp = e.timestamp

            if color and timestamp:
                embed = discord.Embed(title=title, description=description, color=color, timestamp=timestamp)
            elif color:
                embed = discord.Embed(title=title, description=description, color=color)
            elif timestamp:
                embed = discord.Embed(title=title, description=description, timestamp=timestamp)
            else:
                embed = discord.Embed(title=title, description=description)

            # Footer
            footertext = Embed.Empty
            if e.footertext:
                footertext = e.footertext
            footericon = Embed.Empty
            if e.footericon:
                footericon = e.footericon

            embed.set_footer(text=footertext, icon_url=footericon)

            # Images
            if e.image:
                embed.set_image(url=e.image)

            if e.thumbnail:
                embed.set_thumbnail(url=e.thumbnail)

            # Author
            authorname = ""
            if e.authorname:
                authorname = e.authorname
            authoricon = Embed.Empty
            if e.authoricon:
                authoricon = e.authoricon
            authorurl = Embed.Empty
            if e.authorurl:
                authorurl = e.authorurl

            embed.set_author(name=authorname, icon_url=authoricon, url=authorurl)

            # Fields
            if e.fields:
                for field in e.fields:
                    embed.add_field(name=field['title'], value=field['content'], inline=field['inline'])

            # Channel
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
