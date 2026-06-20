import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True   
intents.voice_states = True     

bot = commands.Bot(command_prefix='/', intents=intents)
@bot.event
async def on_ready():
    print(f'✅ 机器人已上线：{bot.user.name}')
    print('输入 /joincall 让我进入语音频道')

@bot.command()
async def joincall(ctx):
    if not ctx.author.voice:
        await ctx.send("❌ 你不在语音频道里")
        return
    channel = ctx.author.voice.channel
    await channel.connect()
    await ctx.send(f"✅ 已加入 {channel.name}")

@bot.command()
async def leavecall(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 已离开")
    else:
        await ctx.send("❌ 我不在语音频道里")

keep_alive()
bot.run(os.getenv("TOKEN"))
