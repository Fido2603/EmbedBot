import discord
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


# Embeds
async def checkEmbeds():
    # Get embeds from the config
    with open('config.json') as json_file:
        data = json.load(json_file)

        embeds = []
        for channel in data['Embeds']:
            for e in data['Embeds'][channel]:
                footertext, footerurl, authorname, authorimage, authorurl, title, color, desc, imageurl, thumbnailurl =\
                    None, None, None, None, None, None, None, None, None, None

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
                if 'image' in e:
                    imageurl = e['image']
                if 'thumbnail' in e:
                    thumbnailurl = e['thumbnail']

                embed = ConfigEmbed(channelid=channel, title=title, color=color, description=desc,
                                    imageurl=imageurl, thumbnailurl=thumbnailurl, authoricon=authorimage,
                                    authorname=authorname, authorurl=authorurl, footertext=footertext,
                                    footericon=footerurl, fields=fields)

                embeds.append(embed)

    # Send/check the embeds
    for e in embeds:
        channel = bot.get_channel(int(e.channel))

        if channel:
            title = ""
            if e.title:
                title = e.title
            description = ""
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
            footertext = ""
            if e.footertext:
                footertext = e.footertext
            footericon = ""
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
            authoricon = ""
            if e.authoricon:
                authoricon = e.authoricon
            authorurl = ""
            if e.authorurl:
                authorurl = e.authorurl

            embed.set_author(name=authorname, icon_url=authoricon, url=authorurl)

            # Fields
            if e.fields:
                for field in e.fields:
                    embed.add_field(name=field['title'], value=field['content'], inline=field['inline'])

            await channel.send(embed=embed)


@bot.event
async def on_ready():
    print("EmbedBot has (re)connected to Discord!")

    print("Checking the embeds!")
    await checkEmbeds()
    print("Done checking the embeds!")
    print("\n")


# Run bot
with open('config.json') as json_file:
    data = json.load(json_file)

    token = data['BotConfig']['token']
    if token:
        bot.run(token)
