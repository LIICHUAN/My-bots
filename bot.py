import discord
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive
import os
import random       
import asyncio      
from datetime import datetime 

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ========== 权限检查函数 ==========
def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator

def is_admin_ctx(ctx) -> bool:
    return ctx.author.guild_permissions.administrator


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'✅ 机器人已上线：{bot.user.name}')
    print('使用 /joincall 让我进入你所在的频道')
    print('使用 /joincall channel:频道名 进入指定频道')
    print('使用 /leavecall 让我离开')
    print('使用 /status 查看我在哪')
    print('⚠️ 只有管理员可以使用加入和离开命令')


# ========== 加入命令（斜杠版）- 仅管理员 ==========
@bot.tree.command(name='joincall', description='进入你所在的语音频道，或指定一个频道')
@app_commands.describe(channel='要进入的语音频道（可选）')
async def slash_join(interaction: discord.Interaction, channel: discord.VoiceChannel = None):
    if not is_admin(interaction):
        await interaction.response.send_message(
            "❌ 你没有权限使用此命令！仅管理员可以使用 /joincall",
            ephemeral=True
        )
        return

    if channel is None:
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ 你不在语音频道里！请先进入一个语音频道，或指定一个频道。",
                ephemeral=True
            )
            return
        target = interaction.user.voice.channel
    else:
        target = channel

    if interaction.guild.voice_client and interaction.guild.voice_client.channel == target:
        await interaction.response.send_message(f"ℹ️ 我已经在 {target.name} 里了")
        return

    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()

    await target.connect()
    await interaction.response.send_message(f"✅ 已加入 {target.name}")


# ========== 离开命令（斜杠版）- 仅管理员 ==========
@bot.tree.command(name='leavecall', description='让我离开语音频道')
async def slash_leave(interaction: discord.Interaction):
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
    if not is_admin_ctx(ctx):
        await ctx.send("❌ 你没有权限使用此命令！仅管理员可以使用 `!加入`")
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
    if not is_admin_ctx(ctx):
        await ctx.send("❌ 你没有权限使用此命令！仅管理员可以使用 `!离开`")
        return

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 已离开")
    else:
        await ctx.send("❌ 我不在语音频道里")

@bot.command()
async def 状态(ctx):
    if ctx.voice_client and ctx.voice_client.is_connected():
        channel = ctx.voice_client.channel
        await ctx.send(f"📢 我在 **{channel.name}**")
    else:
        await ctx.send("📢 我不在语音频道里")


# ============================================================
#                    🎉 活跃气氛
# ============================================================

@bot.tree.command(name='cointoss', description='掷硬币决定正反面')
async def slash_coin(interaction: discord.Interaction):
    result = random.choice(["正面 🪙", "反面 🪙"])
    await interaction.response.send_message(f"掷硬币结果：**{result}**")


@bot.tree.command(name='drawlots', description='从多个选项中随机选一个')
@app_commands.describe(选项='用空格分隔的选项，如：火锅 烤肉 日料')
async def slash_pick(interaction: discord.Interaction, 选项: str):
    items = [item.strip() for item in 选项.split()]
    if len(items) < 2:
        await interaction.response.send_message("❌ 至少给两个选项！如：`/drawlots 火锅 烤肉`")
        return
    await interaction.response.send_message(f"🎯 我选：**{random.choice(items)}**")


# ============================================================
#                    ⏰ 提醒功能 /reminder（带语音开关）
# ============================================================

@bot.tree.command(name='reminder', description='设置一个定时提醒（可选择是否语音提醒）')
@app_commands.describe(
    time='如：10秒、5分钟、2小时',
    content='提醒的内容',
    voice='是否在语音频道播放提醒音效（默认开启）'
)
@app_commands.choices(voice=[
    discord.app_commands.Choice(name='开启（默认）', value='on'),
    discord.app_commands.Choice(name='关闭', value='off')
])
async def slash_remind(
    interaction: discord.Interaction, 
    time: str, 
    content: str,
    voice: str = 'on'
):
    try:
        if "秒" in time:
            seconds = int(time.replace("秒", ""))
        elif "分钟" in time or "分" in time:
            seconds = int(time.replace("分钟", "").replace("分", "")) * 60
        elif "小时" in time or "时" in time:
            seconds = int(time.replace("小时", "").replace("时", "")) * 3600
        else:
            seconds = int(time)
    except:
        await interaction.response.send_message("❌ 格式不对！如：`/reminder time:10分钟 content:开会`", ephemeral=True)
        return

    if seconds < 5:
        await interaction.response.send_message("❌ 至少 5 秒！", ephemeral=True)
        return
    if seconds > 86400:
        await interaction.response.send_message("❌ 最多 24 小时！", ephemeral=True)
        return

    # 显示是否开启语音
    voice_status = "🔊 开启" if voice == 'on' else "🔇 关闭"
    await interaction.response.send_message(f"⏰ 好的，我会在 **{time}** 后提醒你：{content}\n🔊 语音提醒：{voice_status}")

    # 等待指定时间
    await asyncio.sleep(seconds)

    # ========== 先发文字提醒 ==========
    await interaction.followup.send(f"⏰ {interaction.user.mention} 时间到！记得：{content}")

    # ========== 如果用户关闭了语音提醒，到此结束 ==========
    if voice == 'off':
        await interaction.followup.send("ℹ️ 语音提醒已关闭，只发了文字提醒～")
        return

    # ========== 语音提醒逻辑（用户开启了语音） ==========
    guild_id = interaction.guild.id
    user_voice = interaction.user.voice
    bot_voice = interaction.guild.voice_client

    # 情况一：机器人在频道，人在频道 → 播放提醒
    if bot_voice and bot_voice.is_connected() and user_voice and user_voice.channel:
        try:
            # 先停止静音循环
            if guild_id in silence_tasks:
                silence_tasks[guild_id].cancel()
                del silence_tasks[guild_id]
            
            await asyncio.sleep(0.5)
            
            # 播放提醒音效
            if os.path.exists('remind.mp3'):
                audio_source = discord.FFmpegPCMAudio('remind.mp3')
                bot_voice.play(audio_source)
                
                while bot_voice.is_playing():
                    await asyncio.sleep(0.5)
                
                await interaction.followup.send("🔔 语音提醒已播放！")
            else:
                await interaction.followup.send("⚠️ 提醒音效文件不存在，只发了文字提醒")
            
            # 恢复静音循环
            if bot_voice and bot_voice.is_connected():
                task = asyncio.create_task(play_silence_loop(bot_voice, guild_id))
                silence_tasks[guild_id] = task
                
        except Exception as e:
            print(f"语音提醒播放失败：{e}")
            await interaction.followup.send("⚠️ 语音提醒播放失败，但文字提醒已发送")
        return

    # 情况二：机器人在频道，人不在频道 → 显示人不在
    if bot_voice and bot_voice.is_connected() and not user_voice:
        await interaction.followup.send("ℹ️ 你不在语音频道里，无法播放语音提醒～")
        return

    # 情况三：机器人不在频道，人在频道 → 进去播放后退出（不切静音）
    if not bot_voice and user_voice and user_voice.channel:
        try:
            voice_channel = user_voice.channel
            voice_client = await voice_channel.connect()
            
            if os.path.exists('remind.mp3'):
                audio_source = discord.FFmpegPCMAudio('remind.mp3')
                voice_client.play(audio_source)
                
                while voice_client.is_playing():
                    await asyncio.sleep(0.5)
                
                await interaction.followup.send("🔔 语音提醒已播放！")
            else:
                await interaction.followup.send("⚠️ 提醒音效文件不存在，只发了文字提醒")
            
            # 播放完成后退出（不切静音）
            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()
                await interaction.followup.send("👋 播放完成，已离开语音频道")
                
        except Exception as e:
            print(f"语音提醒连接失败：{e}")
            await interaction.followup.send("⚠️ 无法连接到语音频道，只发了文字提醒")
        return

    # 情况四：机器人不在频道，人也不在频道
    if not bot_voice and not user_voice:
        await interaction.followup.send("ℹ️ 你不在语音频道里，无法播放语音提醒～")


# ============================================================
#                    🗳️ 投票功能 /poll 和 /polloptions
# ============================================================

@bot.tree.command(name='poll', description='发起一个简单投票（赞/踩/中立）')
@app_commands.describe(内容='投票的内容')
async def slash_poll(interaction: discord.Interaction, 内容: str):
    await interaction.response.send_message(
        f"📊 **{interaction.user.name} 发起投票：**\n{内容}\n\n👍 赞同 | 👎 反对 | 🤷 中立"
    )
    msg = await interaction.original_response()
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    await msg.add_reaction("🤷")


@bot.tree.command(name='polloptions', description='发起一个带选项的投票（2-9个选项）')
@app_commands.describe(问题='投票的问题', 选项='用空格分隔的选项，如：海边 山上 游乐园')
async def slash_poll_options(interaction: discord.Interaction, 问题: str, 选项: str):
    items = [item.strip() for item in 选项.split()]
    if len(items) < 2 or len(items) > 9:
        await interaction.response.send_message("❌ 请提供 2 到 9 个选项", ephemeral=True)
        return

    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    msg_text = f"📊 **{interaction.user.name} 发起投票：{问题}**\n\n"
    for i, opt in enumerate(items):
        msg_text += f"{emojis[i]} {opt}\n"

    await interaction.response.send_message(msg_text)
    msg = await interaction.original_response()
    for i in range(len(items)):
        await msg.add_reaction(emojis[i])


keep_alive()
bot.run(os.getenv("TOKEN"))
