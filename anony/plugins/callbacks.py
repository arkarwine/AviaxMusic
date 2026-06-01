# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import re

from pyrogram import errors, filters, types

from anony import anon, app, config, db, lang, queue, tg, yt
from anony.helpers import admin_check, buttons, can_manage_vc

pending_settings: dict[int, dict[str, int]] = {}


@app.on_callback_query(filters.regex("cancel_dl") & ~app.bl_users)
@lang.language()
async def cancel_dl(_, query: types.CallbackQuery):
    await query.answer()
    await tg.cancel(query)


@app.on_callback_query(filters.regex("controls") & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _controls(_, query: types.CallbackQuery):
    args = query.data.split()
    action, chat_id = args[1], int(args[2])
    qaction = len(args) == 4
    user = query.from_user.mention

    if not await db.get_call(chat_id):
        try:
            return await query.answer(query.lang["not_playing"], show_alert=True)
        except errors.QueryIdInvalid:
            try:
                await query.message.delete()
            except Exception:
                pass
            return

    if action == "status":
        return await query.answer()
    await query.answer(query.lang["processing"], show_alert=True)

    if action == "pause":
        if not await db.playing(chat_id):
            return await query.answer(
                query.lang["play_already_paused"], show_alert=True
            )
        await anon.pause(chat_id)
        if qaction:
            return await query.edit_message_reply_markup(
                reply_markup=buttons.queue_markup(chat_id, query.lang["paused"], False)
            )
        status = query.lang["paused"]
        reply = query.lang["play_paused"].format(user)

    elif action == "resume":
        if await db.playing(chat_id):
            return await query.answer(query.lang["play_not_paused"], show_alert=True)
        await anon.resume(chat_id)
        if qaction:
            return await query.edit_message_reply_markup(
                reply_markup=buttons.queue_markup(chat_id, query.lang["playing"], True)
            )
        reply = query.lang["play_resumed"].format(user)

    elif action == "skip":
        await anon.play_next(chat_id)
        status = query.lang["skipped"]
        reply = query.lang["play_skipped"].format(user)

    elif action == "force":
        pos, media = queue.check_item(chat_id, args[3])
        if not media or pos == -1:
            return await query.edit_message_text(query.lang["play_expired"])

        m_id = queue.get_current(chat_id).message_id
        queue.force_add(chat_id, media, remove=pos)
        try:
            await app.delete_messages(
                chat_id=chat_id, message_ids=[m_id, media.message_id], revoke=True
            )
            media.message_id = None
        except Exception:
            pass

        msg = await app.send_message(chat_id=chat_id, text=query.lang["play_next"])
        if not media.file_path:
            media.file_path = await yt.download(media.id, video=media.video)
        media.message_id = msg.id
        return await anon.play_media(chat_id, msg, media)

    elif action == "replay":
        media = queue.get_current(chat_id)
        media.user = user
        await anon.replay(chat_id)
        status = query.lang["replayed"]
        reply = query.lang["play_replayed"].format(user)

    elif action == "stop":
        await anon.stop(chat_id)
        status = query.lang["stopped"]
        reply = query.lang["play_stopped"].format(user)

    try:
        if action in ["skip", "replay", "stop"]:
            await query.message.reply_text(reply, quote=False)
            await query.message.delete()
        else:
            mtext = re.sub(
                r"\n\n<blockquote>.*?</blockquote>",
                "",
                query.message.caption.html or query.message.text.html,
                flags=re.DOTALL,
            )
            keyboard = buttons.controls(
                chat_id, status=status if action != "resume" else None
            )
        await query.edit_message_text(
            f"{mtext}\n\n<blockquote>{reply}</blockquote>", reply_markup=keyboard
        )
    except Exception:
        pass


@app.on_callback_query(filters.regex("help") & ~app.bl_users)
@lang.language()
async def _help(_, query: types.CallbackQuery):
    data = query.data.split()
    if len(data) == 1:
        return await query.answer(url=f"https://t.me/{app.username}?start=help")

    if data[1] == "back":
        return await query.edit_message_text(
            text=query.lang["help_menu"], reply_markup=buttons.help_markup(query.lang)
        )
    elif data[1] == "close":
        try:
            await query.message.delete()
            return await query.message.reply_to_message.delete()
        except Exception:
            return

    await query.edit_message_text(
        text=query.lang[f"help_{data[1]}"],
        reply_markup=buttons.help_markup(query.lang, True),
    )


@app.on_callback_query(filters.regex(r"^settings") & ~app.bl_users)
@lang.language()
@admin_check
async def _settings_cb(_, query: types.CallbackQuery):
    cmd = query.data.split()
    if len(cmd) == 1:
        return await query.answer()
    await query.answer(query.lang["processing"], show_alert=True)

    chat_id = query.message.chat.id
    _admin = await db.get_play_mode(chat_id)
    _delete = await db.get_cmd_delete(chat_id)
    _language = await db.get_lang(chat_id)

    if cmd[1] == "delete":
        _delete = not _delete
        await db.set_cmd_delete(chat_id, _delete)
    elif cmd[1] == "play":
        await db.set_play_mode(chat_id, _admin)
        _admin = not _admin
    await query.edit_message_reply_markup(
        reply_markup=buttons.settings_markup(
            query.lang,
            _admin,
            _delete,
            _language,
            chat_id,
        )
    )


@app.on_callback_query(filters.regex(r"^botsettings") & ~app.bl_users)
@lang.language()
@admin_check
async def _bot_settings_cb(_, query: types.CallbackQuery):
    cmd = query.data.split()
    if len(cmd) == 1:
        return await query.answer()

    action = cmd[1]
    if action == "toggle":
        key = cmd[2]
        current = getattr(config, key, None)
        if current is None or not isinstance(current, bool):
            return await query.answer("Invalid setting.", show_alert=True)

        value = not current
        await db.set_setting(key, value)
        config.apply_settings({key: value})
        await query.answer(f"{key} set to {'ON' if value else 'OFF'}.", show_alert=True)
        return await query.edit_message_text(
            text=buttons.bot_settings_text(config),
            reply_markup=buttons.bot_settings_markup(config),
        )

    if action == "edit":
        key = cmd[2]
        pending_settings[query.from_user.id] = {
            "key": key,
            "chat_id": query.message.chat.id,
            "message_id": query.message.message_id,
        }
        await query.answer(
            f"Send the new value for {key} in reply to the prompt.",
            show_alert=True,
        )
        return await query.message.reply_text(
            f"Send the new value for <b>{key}</b> and reply to this message.\n\n"
            f"Current value: {getattr(config, key, 'None')}",
            reply_markup=types.ForceReply(selective=True),
        )

    if action == "close":
        await query.answer()
        return await query.message.delete()

    await query.answer()


@app.on_message(filters.private & filters.reply & ~app.bl_users)
@lang.language()
@admin_check
async def _bot_settings_value(_, message: types.Message):
    pending = pending_settings.pop(message.from_user.id, None)
    if not pending:
        return

    if not message.reply_to_message or message.reply_to_message.from_user.id != app.id:
        return

    key = pending["key"]
    raw = message.text or ""
    if not raw.strip():
        return await message.reply_text("Please send a valid value.")

    try:
        if key in {"AUTO_LEAVE", "AUTO_END", "THUMB_GEN", "VIDEO_PLAY"}:
            value = raw.lower() in {"true", "1", "yes", "on"}
        elif key == "LANG_CODE":
            raw = raw.lower()
            if raw not in lang.get_languages():
                return await message.reply_text(
                    "Invalid language code. Use a supported code like en, fr, de, etc."
                )
            value = raw
        elif key == "DURATION_LIMIT":
            value = int(raw)
            if value <= 0:
                raise ValueError
        elif key in {"QUEUE_LIMIT", "PLAYLIST_LIMIT"}:
            value = int(raw)
            if value <= 0:
                raise ValueError
        else:
            value = raw
    except ValueError:
        return await message.reply_text(
            "Invalid value. Please send a positive integer for this setting."
        )

    await db.set_setting(key, value)
    config.apply_settings({key: value})

    await message.reply_text(f"{key} updated to {value}.")
    try:
        await app.edit_message_text(
            chat_id=pending["chat_id"],
            message_id=pending["message_id"],
            text=buttons.bot_settings_text(config),
            reply_markup=buttons.bot_settings_markup(config),
        )
    except Exception:
        pass
