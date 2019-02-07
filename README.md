# CopyBot

CopyBot is a discord bot written in python, with the help of discord.py. 
The bot scans channels that it can see for images and links to images, and runs reverse image searches on them.

Currently, there's only support for google and tineye, but more apis may be added in the future.
If any of the reverse image searches come back with results, CopyBot will post a message in the corresponding discord channel
notifying users of the result(s), including shortened links to the searches.

The indended use-case for CopyBot is scanning "creative" or "art" channels on discord for potentially stolen
or plaigarized artwork.
The links / messages sent by CopyBot shouldn't be interpreted as accusatory - they exist only to promote diligentness in 
ensuring all of the art posted in such discord channels is unique, and belongs to the person who posted it.
