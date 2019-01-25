import discord
import string
import requests, re
from pytineye import TinEyeAPIRequest

searchLocation = 'https://www.tineye.com/search'
resultRegex = re.compile('\d{1,3}(,\d{3})*(\.\d+)? results?')
urlRegex = '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})'
pic_ext = ['.jpg','.png','.jpeg']
client = discord.Client()

with open('../TOKEN') as tokenFile:
    TOKEN = tokenFile.readline()

async def send(location, message):
    global client
    await client.send_message(location, message)

async def findDuplicates(url, message):
    response = requests.post(searchLocation, data = {'url': url})
    lines = response.text.split('\n')
    for line in lines:
        if re.match(resultRegex, line):
            print(line)
            numResults = int(re.sub("\D", "", line))
            if numResults:
                await send(message.channel, '**{}** other instance(s) of this image have been found on the internet.\nThey can be found here: {}'.format(numResults, response.url))
            else:
                await client.add_reaction(message, "\u2611")
            break

@client.event
async def on_message(message):
    if message.attachments:
        imageUrl = message.attachments[0]['url']
        await findDuplicates(imageUrl, message)
    else:
        for ext in pic_ext:
            if message.content.endswith(ext):
                match = re.match(urlRegex, message.content)
                if match:
                    imageUrl = match.group(1)
                    await findDuplicates(imageUrl, message)

@client.event
async def on_ready():
    print('Logged in!')
        
client.run(TOKEN)