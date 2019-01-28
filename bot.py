from pyshorteners import Shortener
import discord
import string
import requests
import json
import re

with open('../KEY') as apiKey:
    KEY = apiKey.readline()

TINEYE_LOCATION = 'https://www.tineye.com/search'
GOOGLE_LOCATION = 'https://www.google.com/searchbyimage?image_url={}&encoded_image=&image_content=&filename=&hl=en'
LINK_SHORTENER_LOCATION = 'https://www.googleapis.com/urlshortener/v1/url?key={}'.format(KEY)
RESULT_REGEX = re.compile('\d{1,3}(,\d{3})*(\.\d+)? results?')
MATCHING_REGEX = re.compile('Pages that include matching images')
URL_REGEX = '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})'
PIC_EXT = ['.jpg','.png','.jpeg'] # If message 'endswith', it will considers it an attachment
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}

client = discord.Client()
shortener = Shortener('Tinyurl')

async def send(location, message):
    global client
    embed = discord.Embed(title="", description=message)
    await client.send_message(location, embed=embed)

def shorten(link):
    return shortener.short(link)

async def findDuplicates(url, message):
    print('Performing reverse image search on ' + url + '...')
    results = []

    # Tineye reverse image search
    response = requests.post(TINEYE_LOCATION, data={'url': url})
    lines = response.text.split('\n')
    for line in lines:
        if re.match(RESULT_REGEX, line):
            if int(re.sub('\D', '', line)):
                results.append('Tineye: ' + shorten(response.url))
                break

    # Google reverse image search
    searchUrl = 'https://www.google.com/searchbyimage?image_url={}'.format(url)
    response = requests.get(searchUrl, allow_redirects=True, headers=HEADERS)
    result = re.search(MATCHING_REGEX, response.text)
    if result: results.append('Google: ' + shorten(response.url))

    if results:
        await send(message.channel, 'Other instances of this image have been found on the internet.\nThey can be found here: \n{}'.format('\n'.join(results)))
    else:
        await client.add_reaction(message, '\u2611')
    print('Done!')
    
@client.event
async def on_message(message):
    if message.attachments:
        imageUrl = message.attachments[0]['url']
        await findDuplicates(imageUrl, message)
    else:
        # Message still might be an image
        for ext in PIC_EXT:
            if message.content.endswith(ext):
                match = re.match(URL_REGEX, message.content)
                if match:
                    # Message now definitely contains an image url
                    imageUrl = match.group(1)
                    await findDuplicates(imageUrl, message)

@client.event
async def on_ready():
    print('Logged in!')

with open('../TOKEN') as tokenFile:
    TOKEN = tokenFile.readline()

client.run(TOKEN)