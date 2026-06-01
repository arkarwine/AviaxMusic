# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import types

from anony import app, config, lang
from anony.core.lang import lang_codes


class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton

    def cancel_dl(self, text) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, callback_data=f"cancel_dl")]])

    def controls(
        self,
        chat_id: int,
        status: str = None,
        timer: str = None,
        remove: bool = False,
    ) -> types.InlineKeyboardMarkup:
        keyboard = []
        if status:
            keyboard.append(
                [self.ikb(text=status, callback_data=f"controls status {chat_id}")]
            )
        elif timer:
            keyboard.append(
                [self.ikb(text=timer, callback_data=f"controls status {chat_id}")]
            )

        if not remove:
            keyboard.append(
                [
                    self.ikb(text="▷", callback_data=f"controls resume {chat_id}"),
                    self.ikb(text="II", callback_data=f"controls pause {chat_id}"),
                    self.ikb(text="⥁", callback_data=f"controls replay {chat_id}"),
                    self.ikb(text="‣‣I", callback_data=f"controls skip {chat_id}"),
                    self.ikb(text="▢", callback_data=f"controls stop {chat_id}"),
                ]
            )
        return self.ikm(keyboard)

    def help_markup(
        self, _lang: dict, back: bool = False
    ) -> types.InlineKeyboardMarkup:
        if back:
            rows = [
                [
                    self.ikb(text=_lang["back"], callback_data="help back"),
                    self.ikb(text=_lang["close"], callback_data="help close"),
                ]
            ]
        else:
            cbs = ["admins", "auth", "blist", "lang", "ping", "play", "queue", "stats", "sudo"]
            buttons = [
                self.ikb(text=_lang[f"help_{i}"], callback_data=f"help {cb}")
                for i, cb in enumerate(cbs)
            ]
            rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]

        return self.ikm(rows)

    def lang_markup(self, _lang: str) -> types.InlineKeyboardMarkup:
        langs = lang.get_languages()

        buttons = [
            self.ikb(
                text=f"{name} ({code}) {'✔️' if code == _lang else ''}",
                callback_data=f"lang_change {code}",
            )
            for code, name in langs.items()
        ]
        rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
        return self.ikm(rows)

    def ping_markup(self, text: str) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, url=config.SUPPORT_CHAT)]])

    def play_queued(
        self, chat_id: int, item_id: str, _text: str
    ) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(
                        text=_text, callback_data=f"controls force {chat_id} {item_id}"
                    )
                ]
            ]
        )

    def queue_markup(
        self, chat_id: int, _text: str, playing: bool
    ) -> types.InlineKeyboardMarkup:
        _action = "pause" if playing else "resume"
        return self.ikm(
            [[self.ikb(text=_text, callback_data=f"controls {_action} {chat_id} q")]]
        )

    def settings_markup(
        self, lang: dict, admin_only: bool, cmd_delete: bool, language: str, chat_id: int
    ) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(
                        text=lang["play_mode"] + " ➜",
                        callback_data="settings",
                    ),
                    self.ikb(text=admin_only, callback_data="settings play"),
                ],
                [
                    self.ikb(
                        text=lang["cmd_delete"] + " ➜",
                        callback_data="settings",
                    ),
                    self.ikb(text=cmd_delete, callback_data="settings delete"),
                ],
                [
                    self.ikb(
                        text=lang["language"] + " ➜",
                        callback_data="settings",
                    ),
                    self.ikb(text=lang_codes[language], callback_data="language"),
                ],
            ]
        )

    def bot_settings_text(self, cfg) -> str:
        def fmt(val, boolean: bool = False) -> str:
            if boolean:
                return "ON" if val else "OFF"
            return str(val)

        return (
            "<b>Bot Configuration</b>\n"
            f"AUTO_LEAVE: {fmt(cfg.AUTO_LEAVE, True)}\n"
            f"AUTO_END: {fmt(cfg.AUTO_END, True)}\n"
            f"THUMB_GEN: {fmt(cfg.THUMB_GEN, True)}\n"
            f"VIDEO_PLAY: {fmt(cfg.VIDEO_PLAY, True)}\n"
            f"LANG_CODE: {fmt(cfg.LANG_CODE)}\n"
            f"DURATION_LIMIT: {fmt(cfg.DURATION_LIMIT // 60)} min\n"
            f"QUEUE_LIMIT: {fmt(cfg.QUEUE_LIMIT)}\n"
            f"PLAYLIST_LIMIT: {fmt(cfg.PLAYLIST_LIMIT)}\n"
            f"SUPPORT_CHANNEL: {fmt(cfg.SUPPORT_CHANNEL)}\n"
            f"SUPPORT_CHAT: {fmt(cfg.SUPPORT_CHAT)}\n"
            f"DEFAULT_THUMB: {fmt(cfg.DEFAULT_THUMB)}\n"
            f"PING_IMG: {fmt(cfg.PING_IMG)}\n"
            f"START_IMG: {fmt(cfg.START_IMG)}"
        )

    def bot_settings_markup(self, cfg) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(
                        text=f"AUTO_LEAVE: {'ON' if cfg.AUTO_LEAVE else 'OFF'}",
                        callback_data="botsettings toggle AUTO_LEAVE",
                    ),
                    self.ikb(
                        text=f"AUTO_END: {'ON' if cfg.AUTO_END else 'OFF'}",
                        callback_data="botsettings toggle AUTO_END",
                    ),
                ],
                [
                    self.ikb(
                        text=f"THUMB_GEN: {'ON' if cfg.THUMB_GEN else 'OFF'}",
                        callback_data="botsettings toggle THUMB_GEN",
                    ),
                    self.ikb(
                        text=f"VIDEO_PLAY: {'ON' if cfg.VIDEO_PLAY else 'OFF'}",
                        callback_data="botsettings toggle VIDEO_PLAY",
                    ),
                ],
                [
                    self.ikb(
                        text=f"LANG: {cfg.LANG_CODE}",
                        callback_data="botsettings edit LANG_CODE",
                    ),
                    self.ikb(
                        text=f"DUR: {cfg.DURATION_LIMIT // 60}m",
                        callback_data="botsettings edit DURATION_LIMIT",
                    ),
                ],
                [
                    self.ikb(
                        text=f"QUEUE: {cfg.QUEUE_LIMIT}",
                        callback_data="botsettings edit QUEUE_LIMIT",
                    ),
                    self.ikb(
                        text=f"PLAYLIST: {cfg.PLAYLIST_LIMIT}",
                        callback_data="botsettings edit PLAYLIST_LIMIT",
                    ),
                ],
                [
                    self.ikb(
                        text="SUPPORT CHANNEL",
                        callback_data="botsettings edit SUPPORT_CHANNEL",
                    ),
                    self.ikb(
                        text="SUPPORT CHAT",
                        callback_data="botsettings edit SUPPORT_CHAT",
                    ),
                ],
                [
                    self.ikb(
                        text="DEFAULT THUMB",
                        callback_data="botsettings edit DEFAULT_THUMB",
                    ),
                    self.ikb(
                        text="PING IMG",
                        callback_data="botsettings edit PING_IMG",
                    ),
                ],
                [
                    self.ikb(
                        text="START IMG",
                        callback_data="botsettings edit START_IMG",
                    )
                ],
                [
                    self.ikb(text="Close", callback_data="botsettings close"),
                ],
            ]
        )

    def start_key(
        self, lang: dict, private: bool = False
    ) -> types.InlineKeyboardMarkup:
        rows = [
            [
                self.ikb(
                    text=lang["add_me"],
                    url=f"https://t.me/{app.username}?startgroup=true",
                )
            ],
            [self.ikb(text=lang["help"], callback_data="help")],
            [
                self.ikb(text=lang["support"], url=config.SUPPORT_CHAT),
                self.ikb(text=lang["channel"], url=config.SUPPORT_CHANNEL),
            ],
        ]
        if private:
            rows += [
                [
                    self.ikb(
                        text=lang["owner"],
                        url=f"tg://user?id={config.OWNER_ID}",
                    )
                ]
            ]
        else:
            rows += [[self.ikb(text=lang["language"], callback_data="language")]]
        return self.ikm(rows)

    def yt_key(self, link: str) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(text="❐", copy_text=link),
                    self.ikb(text="Youtube", url=link),
                ],
            ]
        )
