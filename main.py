''' Imports '''
#############################################################################
import discord
from webserver import keep_alive
import os
from discord.ext import commands
from discord import FFmpegPCMAudio
import requests
import json
import youtube_dl
from math import floor




''' Bot Startup Events '''
#############################################################################
intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = "=", intents = intents, help_command = None)

class colour:
  white = 0xffffff
  black = 0x000000
  red = 0xff7878
  orange = 0xf7c481
  yellow = 0xffeb8a
  green = 0xceff8a
  aqua = 0xabf7bf
  light_blue = 0xadf7f1
  blue = 0xa7dafa
  violet = 0xa7b1fa
  magenta = 0xc1a1f7
  pink = 0xefb1fa
  red_pink = 0xffb3c9

@client.event
async def on_ready():
  print("Yoko 요코 is ready!")
  print ("-------------------")
  game = discord.Game("with Yakult")
  await client.change_presence(activity=game)




''' Help Command '''
#############################################################################
@client.command()
async def help(ctx):
  em = discord.Embed(title = "Help [=]", description = "Use =help <command> for extended information on a command.", color = colour.white)
  em.add_field(name = "🎵 Music 🎵", value = "Play\nStop\nLeave\nQueue\nSkip\nPause\nUnpause\nMove\nDuration\nClear")
  em.add_field(name = "Miscellaneous", value = "Quote\nTest")
  await ctx.send(embed = em)

@help.command()
async def play(ctx):
  em = discord.Embed(title = "")




''' Miscellaneous '''
#############################################################################
@client.command()
async def quote(ctx):
  url = "https://quotes15.p.rapidapi.com/quotes/random/"
  headers = {
      'x-rapidapi-key': "1d637c2c66msh77cac6d05221b56p1e511ajsndc31cf065f0c",
      'x-rapidapi-host': "quotes15.p.rapidapi.com"
      }
  response = requests.request("GET", url, headers=headers)
  quote_content = json.loads(response.text)["content"]
  await ctx.send(quote_content)

@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.send("This is a invalid command.")
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send("This command is missing an argument.")

@client.command()
async def test(ctx):
  await ctx.send("Test works")




''' Music '''
#############################################################################
ydl_opts = {
    "format": "bestaudio/best",
    "postprocessors": [{
      "key": "FFmpegExtractAudio",
      "preferredcodec": "mp3",
      "preferredquality": "192"
    }],
    }

queue_links=[]

def convert_time(secs):
    seconds = secs%60
    minutes = floor(secs/60)
    hours = floor(minutes/60)
    minutes = minutes%60
    return f"This song is {hours} hrs/hr {minutes} mins/min and {seconds} secs/sec!"

def queue_update(ctx):
  queue_links.pop(0)
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    meta = ydl.extract_info(queue_links[0], download=False)
    URL = meta['formats'][0]['url']
    source = FFmpegPCMAudio(URL, before_options= '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
    ctx.send(f":musical_note: Now playing {meta['title']} by {meta['uploader']}. :musical_note:")
    ctx.voice_client.play(source, after=lambda x=None: queue_update(ctx))

@client.command()
async def play(ctx, link:str):
  if ctx.author.voice:
    if not ctx.voice_client:

      channel = ctx.message.author.voice.channel
      voice = await channel.connect()
      with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(link, download=False)


      ##if 'entries' in meta:
        ##for i in meta['entries']:
          ##URL = i['formats'][0]['url']     
          ##print(i)
          ##player = FFmpegPCMAudio(URL, before_options= '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
          ##queue_links.append(i)
          ##voice.play(player, after = lambda x=None: queue_update(ctx))
          ##await ctx.send(f"🎵 Now playing {meta['title']} by {meta['uploader']}. 🎵")


      if not queue_links:
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
          meta = ydl.extract_info(link, download=False)
          URL = meta['formats'][0]['url']
          source = FFmpegPCMAudio(URL, before_options= '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
        await ctx.send(f"🎵 Now playing {meta['title']} by {meta['uploader']}. 🎵")
        queue_links.append(link)
        voice.play(source, after=lambda x=None: queue_update(ctx))

      elif queue_links:
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        url = queue_links[0]
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
          meta = ydl.extract_info(url, download=False)
          URL = meta['formats'][0]['url']
        source = FFmpegPCMAudio(URL, before_options= '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
        await ctx.send(f"🎵 Now playing {meta['title']} by {meta['uploader']}. 🎵")
        queue_links.append(link)
        voice.play(source, after=lambda x=None: queue_update(ctx))

    elif ctx.voice_client:

      if ctx.voice_client.is_playing():
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
          meta = ydl.extract_info(link, download=False)
        await ctx.send(f"Added {meta['title']} by {meta['uploader']} to queue!")
        queue_links.append(link)
      
      elif not ctx.voice_client.is_playing():
        if queue_links:
          url = queue_links[0]
          with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(url, download=False)
            URL = meta['formats'][0]['url']
          source = FFmpegPCMAudio(URL, before_options= '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
          await ctx.send(f"🎵 Now playing {meta['title']} by {meta['uploader']}. 🎵")
          ctx.voice_client.play(source, after=lambda x=None: queue_update(ctx))
          meta = ydl.extract_info(link, download=False)
          await ctx.send(f"Added {meta['title']} by {meta['uploader']} to queue!")
          queue_links.append(link)
        elif not queue_links:
          with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(link, download=False)
            URL = meta['formats'][0]['url']
          source = FFmpegPCMAudio(URL, before_options= '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
          await ctx.send(f"🎵 Now playing {meta['title']} by {meta['uploader']}. 🎵")
          queue_links.append(link)
          ctx.voice_client.play(source, after=lambda x=None: queue_update(ctx))
  else:
    await ctx.send("You are not in a voice channel. Join a voice channel before using this command.")

@client.command()
async def skip(ctx):
  abcdefg = ""
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    meta = ydl.extract_info(queue_links[0], download=False)
    abcdefg = {meta['title']}
    gfedcba = {meta['uploader']}
    queue_links.pop(0)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
      meta = ydl.extract_info(queue_links[0], download=False)
      URL = meta['formats'][0]['url']
    await ctx.send(f"{meta['title']} by {meta['uploader']} was skipped to {abcdefg} by {gfedcba}!")
    source = FFmpegPCMAudio(URL, before_options= '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
    ctx.voice_client.stop()
    queue_links.append(queue_links[0])
    ctx.voice_client.play(source, after=lambda x=None: queue_update(ctx))
    

@client.command()
async def queue(ctx):
  await ctx.send(queue_links)

@client.command()
async def clear(ctx):
  queue_links.clear()

@client.command()
async def duration(ctx):
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    meta = ydl.extract_info(queue_links[0], download=False)
    secs = (meta['duration'])
  await ctx.send(convert_time(secs))

@client.command()
async def move(ctx):
  await ctx.voice_client.move_to(ctx.message.author.voice.channel)

@client.command()
async def pause(ctx):
  if ctx.voice_client:
    ctx.voice_client.pause()
  else:
    await ctx.send("I am not in a voice channel. Add me to a voice channel to use this command.")

@client.command()
async def unpause(ctx):
  if ctx.voice_client:
    if ctx.voice_client.is_paused():
      ctx.voice_client.resume()
    else:
      await ctx.send("I am not currently paused. You can use this command once I am paused.")
  else:
    await ctx.send("I am not in a voice channel. Add me to a voice channel to use this command.")

@client.command()
async def stop(ctx):
  if ctx.voice_client.is_playing():
    ctx.voice_client.stop()
  elif not ctx.voice_client:
    await ctx.send("I am not in a voice channel. Add me to a voice channel to use this command.")
  elif ctx.voice_client and not ctx.voice_client.is_playing():
    await ctx.send("I am not playing anything.")

@client.command(pass_context = True)
async def leave(ctx):
  if ctx.voice_client:
    await ctx.voice_client.disconnect()
  else:
    await ctx.send("I am not in a voice channel. Add me to a voice channel to use this command.")


keep_alive()
client.run(os.environ['TOKEN'])