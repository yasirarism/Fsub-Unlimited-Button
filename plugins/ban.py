# (©)Codexbotz
# Recode by @mrismanaziz
# t.me/SharingUserbot & t.me/Lunatic0de

import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from bot import Bot
from config import ADMINS
from database.sql import ban_user, get_banned_user, is_banned, unban_user


async def _notify_banned(client: Bot, user_id: int, reason: str | None = None):
    reason_text = f"\n<b>Alasan:</b> {reason}" if reason else ""
    text = (
        "⛔ <b>Anda telah diblokir dari bot ini.</b>"
        f"{reason_text}\nSilakan hubungi admin jika merasa ini keliru."
    )
    try:
        await client.send_message(user_id, text)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await client.send_message(user_id, text)


@Bot.on_message(filters.private, group=-1)
async def block_banned_users(client: Bot, message: Message):
    if not message.from_user:
        return
    if await is_banned(message.from_user.id):
        banned_info = await get_banned_user(message.from_user.id)
        reason = banned_info.reason if banned_info else None
        try:
            await _notify_banned(client, message.from_user.id, reason)
        except BaseException:
            pass
        message.stop_propagation()


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("ban"))
async def ban_user_command(client: Bot, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        reason = " ".join(message.command[1:]) if len(message.command) > 1 else None
    elif len(message.command) > 1:
        try:
            target = await client.get_users(message.command[1])
        except Exception:
            return await message.reply_text(
                "❌ <b>Pengguna tidak ditemukan.</b>"
            )
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else None
    else:
        return await message.reply_text(
            "❌ <b>Gunakan:</b> <code>/ban [user_id/username] [alasan]</code>"
        )

    await ban_user(
        target.id,
        f"@{target.username}" if target.username else None,
        reason,
    )
    await message.reply_text(
        f"✅ <b>Pengguna diblokir:</b> {target.mention}\n"
        f"<b>ID:</b> <code>{target.id}</code>"
    )

    try:
        await _notify_banned(client, target.id, reason)
    except BaseException:
        await message.reply_text(
            "⚠️ <b>Notifikasi ke user gagal dikirim.</b>"
        )


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("unban"))
async def unban_user_command(client: Bot, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target = await client.get_users(message.command[1])
        except Exception:
            return await message.reply_text(
                "❌ <b>Pengguna tidak ditemukan.</b>"
            )
    else:
        return await message.reply_text(
            "❌ <b>Gunakan:</b> <code>/unban [user_id/username]</code>"
        )

    await unban_user(target.id)
    await message.reply_text(
        f"✅ <b>Pengguna diaktifkan kembali:</b> {target.mention}\n"
        f"<b>ID:</b> <code>{target.id}</code>"
    )

    try:
        await client.send_message(
            target.id,
            "✅ <b>Blokir anda telah dicabut. Silakan gunakan bot kembali.</b>",
        )
    except BaseException:
        pass
