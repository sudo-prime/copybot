import discord
import string
import requests, re

TINEYE_LOCATION = 'https://www.tineye.com/search'
GOOGLE_LOCATION = 'https://www.google.com/searchbyimage?image_url={}&encoded_image=&image_content=&filename=&hl=en'
RESULT_REGEX = re.compile('\d{1,3}(,\d{3})*(\.\d+)? results?')
URL_REGEX = '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})'
# If message 'endswith', it will consides it an attachment
PIC_EXT = ['.jpg','.png','.jpeg']

client = discord.Client()

async def send(location, message):
    global client
    await client.send_message(location, message)

async def findDuplicates(url, message):
    # # Perform request to tineye service
    # response = requests.post(TINEYE_LOCATION, data = {'url': url})
    # lines = response.text.split('\n')
    # numResults = 0
    # for line in lines:
    #     if re.match(resultRegex, line): # Parse number of results
    #         numResults += int(re.sub('\D', '', line))
    #         break
    
    print("performing on {}".format(url))
    # Google reverse image search

    searchUrl = 'https://www.google.com/searchbyimage?image_url={}'.format(url)
    response = requests.get(searchUrl, allow_redirects=False)
    print("first response")
    print(response.text)
    fetchUrl = response.headers['Location']
    print("fetch")
    print(fetchUrl)
    response = requests.get(fetchUrl)
    print("second response")
    print(response.text)

    # if numResults:
    #     await send(message.channel, 'Other instance(s) of this image have been found on the internet.\nThey can be found here: {}'.format(numResults, response.url))
    # else:
    #     await client.add_reaction(message, '\u2611')
    
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
                    print(imageUrl)
                    await findDuplicates(imageUrl, message)

@client.event
async def on_ready():
    print('Logged in!')

with open('../TOKEN') as tokenFile:
    TOKEN = tokenFile.readline()

client.run(TOKEN)