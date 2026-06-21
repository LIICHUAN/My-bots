import discord
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents) # 前缀保留，但主要用斜杠
        self.synced = False # 用来标记是否已同步命令

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            # 将命令同步到当前服务器（这样会立刻生效）
            guild = discord.Object(id=YOUR_GUILD_ID) # 重要：替换成你的服务器ID
            await self.tree.sync(guild=guild)
            self.synced = True
            print(f'✅ 机器人已上线：{self.user.name}')
            print('请使用 /joincall 和 /leavecall 命令')

bot = MyBot()

# 定义一个“加入”的斜杠命令
@bot.tree.command(name='joincall', description='让我进入你所在的语音频道', guild=discord.Object(id=YOUR_GUILD_ID))
async def slash_join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ 你不在语音频道里")
        return
    channel = interaction.user.voice.channel
    await channel.connect()
    await interaction.response.send_message(f"✅ 已加入 {channel.name}")

# 定义一个“离开”的斜杠命令
@bot.tree.command(name='leavecall', description='让我离开语音频道', guild=discord.Object(id=YOUR_GUILD_ID))
async def slash_leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 已离开")
    else:
        await interaction.response.send_message("❌ 我不在语音频道里")

# 如果想保留 !加入 作为备选，可以保留原来的代码，互不冲突

keep_alive()
bot.run(os.getenv("TOKEN"))
