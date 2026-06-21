import discord
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ========== 权限检查函数 ==========
def is_admin(interaction: discord.Interaction) -> bool:
    """检查用户是否有管理员权限"""
    return interaction.user.guild_permissions.administrator

def is_admin_ctx(ctx) -> bool:
    """文本命令的权限检查"""
    return ctx.author.guild_permissions.administrator


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'✅ 机器人已上线：{bot.user.name}')
    print('使用 /joincall 让我进入你所在的频道')
    print('使用 /joincall channel:name 进入指定频道')
    print('使用 /leavecall 让我离开')
    print('使用 /status 查看我在哪')
    print('⚠️ 只有管理员可以使用加入和离开命令')


# ========== 加入命令（斜杠版）- 仅管理员 ==========
@bot.tree.command(name='joincall', description='进入你所在的语音频道，或指定一个频道')
@app_commands.describe(channel='要进入的语音频道（可选）')
async def slash_join(interaction: discord.Interaction, 频道: discord.VoiceChannel = None):
    # 权限检查：非管理员拒绝
    if not is_admin(interaction):
        await interaction.response.send_message(
            "❌ 你没有权限使用此命令！仅管理员可以使用 /joincall",
            ephemeral=True
        )
        return

    # 如果没有指定频道 → 进入用户当前所在的频道
    if 频道 is None:
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ 你不在语音频道里！请先进入一个语音频道，或指定一个频道。",
                ephemeral=True
            )
            return
        target = interaction.user.voice.channel
    else:
        target = channel

    # 如果机器人已经在这个频道里
    if interaction.guild.voice_client and interaction.guild.voice_client.channel == target:
        await interaction.response.send_message(f"ℹ️ 我已经在 {target.name} 里了")
        return

    # 如果在其他频道，先断开
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()

    await target.connect()
    await interaction.response.send_message(f"✅ 已加入 {target.name}")


# ========== 离开命令（斜杠版）- 仅管理员 ==========
@bot.tree.command(name='leavecall', description='让我离开语音频道')
async def slash_leave(interaction: discord.Interaction):
    # 权限检查：非管理员拒绝
    if not is_admin(interaction):
        await interaction.response.send_message(
            "❌ 你没有权限使用此命令！仅管理员可以使用 /leavecall",
            ephemeral=True
        )
        return

    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 已离开语音频道")
    else:
        await interaction.response.send_message("❌ 我不在语音频道里", ephemeral=True)


# ========== 状态命令（斜杠版）- 所有人可用 ==========
@bot.tree.command(name='status', description='查看我在哪个语音频道')
async def slash_status(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_connected():
        channel = interaction.guild.voice_client.channel
        member_count = len(channel.members)
        await interaction.response.send_message(f"📢 我在 **{channel.name}**（共 {member_count} 人）")
    else:
        await interaction.response.send_message("📢 我不在语音频道里，使用 `/joincall` 让我进去")


# ========== 备选：文本命令 - 仅管理员 ==========
@bot.command()
async def 加入(ctx, *, target: discord.VoiceChannel = None):
    # 权限检查
    if not is_admin_ctx(ctx):
        await ctx.send("❌ 你没有权限使用此命令！仅管理员可以使用 `/joincall`")
        return

    if target is None:
        if not ctx.author.voice:
            await ctx.send("❌ 你不在语音频道里！")
            return
        target = ctx.author.voice.channel

    if ctx.voice_client and ctx.voice_client.channel == target:
        await ctx.send(f"ℹ️ 我已经在 {target.name} 里了")
        return

    if ctx.voice_client:
        await ctx.voice_client.disconnect()

    await target.connect()
    await ctx.send(f"✅ 已加入 {target.name}")

@bot.command()
async def 离开(ctx):
    # 权限检查
    if not is_admin_ctx(ctx):
        await ctx.send("❌ 你没有权限使用此命令！仅管理员可以使用 `/leavecall`")
        return

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 已离开")
    else:
        await ctx.send("❌ 我不在语音频道里")

@bot.command()
async def 状态(ctx):
    # 状态命令所有人可用，不加权限限制
    if ctx.voice_client and ctx.voice_client.is_connected():
        channel = ctx.voice_client.channel
        await ctx.send(f"📢 我在 **{channel.name}**")
    else:
        await ctx.send("📢 我不在语音频道里")


keep_alive()
bot.run(os.getenv("TOKEN"))
