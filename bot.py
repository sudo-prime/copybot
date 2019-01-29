from pyshorteners import Shortener
from requests_futures.sessions import FuturesSession
import discord
import string
import json
import re

with open('../KEY') as apiKey:
    KEY = apiKey.readline()

TINEYE_LOCATION = 'https://www.tineye.com/search'
GOOGLE_LOCATION = 'https://www.google.com/searchbyimage?image_url={}'
LINK_SHORTENER_LOCATION = 'https://www.googleapis.com/urlshortener/v1/url?key={}'.format(KEY)
RESULT_REGEX = re.compile('\d{1,3}(,\d{3})*(\.\d+)? results?')
MATCHING_REGEX = re.compile('Pages that include matching images')
URL_REGEX = '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})'
PIC_EXT = ['.jpg','.png','.jpeg'] # If message 'endswith', it will considers it an attachment
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}

client = discord.Client()
shortener = Shortener('Tinyurl')
pending = {}

async def send(location, message):
    global client
    embed = discord.Embed(title="", description=message)
    await client.send_message(location, embed=embed)

def shorten(url):
    return shortener.short(url)
    
async def sendMessageIfResolved(imageUrl):
    print(pending[imageUrl])
    if (pending[imageUrl][tineye_result] != None and 
        pending[imageUrl][google_result] != None):
        # Both functions have resolved
        if (pending[imageUrl][tineye_result] or
            pending[imageUrl][google_result]):
            # At least one of the functions returned a result
            results = [pending[imageUrl][key] for key in pending[url] if pendingp[imageUrl][key]]
            await send(message.channel, 'Other instances of this image have been found on the internet.\nThey can be found here: \n{}'.format('\n'.join(results)))
        else:
            await client.add_reaction(message, '\u2611')
        pending.pop(imageUrl, None)

def googleHookFactory(imageUrl):
    async def responseHook(response, *args, **kwargs):
        print('goog came back')
        result = re.search(MATCHING_REGEX, response.text)
        if result: pending[imageUrl]['google_result'] = shorten(response.url)
        else: pending[imageUrl]['google_result'] = False
        await sendMessageIfResolved(imageUrl)
    return responseHook

def tineyeHookFactory(imageUrl):
    async def responseHook(response, *args, **kwargs):
        print('tin came back')
        lines = response.text.split('\n')
        for line in lines:
            if re.match(RESULT_REGEX, line):
                if int(re.sub('\D', '', line)):
                    pending[imageUrl]['tineye_result'] = shorten(response.url)
                    break
        if pending[imageUrl]['tineye_result'] == None:
            pending[imageUrl]['tineye_result'] = False
        await sendMessageIfResolved(imageUrl)
    return responseHook

tineyeSession = FuturesSession()
googleSession = FuturesSession()

async def findDuplicates(imageUrl, message):
    print('Performing reverse image search on ' + imageUrl + '...')
    # Tineye reverse image search
    # TODO: make a function that returns a handler function (to avoid passing params to hook function)
    tineyeSession.hooks['response'] = tineyeHookFactory(imageUrl)
    print(tineyeSession.hooks)
    tineyeSession.post(TINEYE_LOCATION, data={'url': imageUrl})
    
    # Google reverse image search
    # TODO: Maybe remove the allow_redirects
    googleSession.hooks['response'] = googleHookFactory(imageUrl)
    print(googleSession.hooks)
    googleSession.get(GOOGLE_LOCATION.format(imageUrl), allow_redirects=True, headers=HEADERS)

    pending[imageUrl] =  {
        'google_result': None,
        'tineye_result': None
    }
    print(pending)
    
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