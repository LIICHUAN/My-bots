import discord
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()  # 全局同步（不加guild参数）
    print(f'✅ 机器人已上线：{bot.user.name}')
    print('等待 Discord 全局同步（最多1小时），之后 /加入 可用')

# 全局斜杠命令（去掉 guild 参数）
@bot.tree.command(name='joincall', description='让我进入你所在的语音频道')
async def slash_join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ 你不在语音频道里")
        return
    channel = interaction.user.voice.channel
    await channel.connect()
    await interaction.response.send_message(f"✅ 已加入 {channel.name}")

@bot.tree.command(name='leavecall', description='让我离开语音频道')
async def slash_leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 已离开")
    else:
        await interaction.response.send_message("❌ 我不在语音频道里")

# 保留 !加入 和 !离开 作为备选（前面的代码里已经写过了）
# ... 这里保留你原来 !加入 和 !离开 的代码 ...

keep_alive()
bot.run(os.getenv("TOKEN"))
