# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import inspect
import re
from traceback import format_exc

from telethon import Button
from telethon.errors import QueryIdInvalidError
from telethon.events import CallbackQuery, InlineQuery, NewMessage
from telethon.tl.types import InputWebDocument

from .. import LOGS, asst, udB, ultroid_bot
from ..fns.admins import admin_check
from . import append_or_update, owner_and_sudos

OWNER = ultroid_bot.full_name

MSG = f"""
**Repthon - UserBot**
➖➖➖➖➖➖➖➖➖➖
**المالك**: [{OWNER}](tg://user?id={ultroid_bot.uid})
**المساعدة**: @Repthon_support
➖➖➖➖➖➖➖➖➖➖
"""

IN_BTTS = [
    [
        Button.url(
            "الريبو",
            url="https://github.com/rogerpq/Ultroid",
        ),
        Button.url("المساعدة", url="https://t.me/Repthon_support"),
    ]
]


# decorator for assistant


def asst_cmd(pattern=None, load=None, owner=False, **kwargs):
    """Decorator for assistant's command"""
    name = inspect.stack()[1].filename.split("/")[-1].replace(".py", "")
    kwargs["forwards"] = False

    def ult(func):
        if pattern:
            kwargs["pattern"] = re.compile(f"^/{pattern}")
        if owner:
            kwargs["from_users"] = owner_and_sudos
        asst.add_event_handler(func, NewMessage(**kwargs))
        if load is not None:
            append_or_update(load, func, name, kwargs)

    return ult


def callback(data=None, from_users=[], admins=False, owner=False, **kwargs):
    """أساسيات الانلاين"""
    if "me" in from_users:
        from_users.remove("me")
        from_users.append(ultroid_bot.uid)

    def ultr(func):
        async def wrapper(event):
            if admins and not await admin_check(event):
                return
            if from_users and event.sender_id not in from_users:
                return await event.answer("Not for You!", alert=True)
            if owner and event.sender_id not in owner_and_sudos():
                return await event.answer(f"This is {OWNER}'s bot!!")
            try:
                await func(event)
            except Exception as er:
                LOGS.exception(er)

        asst.add_event_handler(wrapper, CallbackQuery(data=data, **kwargs))

    return ultr


def in_pattern(pattern=None, owner=False, **kwargs):
    """Assistant's inline decorator."""

    def don(func):
        async def wrapper(event):
            if owner and event.sender_id not in owner_and_sudos():
                res = [
                    await event.builder.article(
                        title="سورس ريبثون",
                        url="https://t.me/Repthon",
                        description="(c) RepthonTeam",
                        text=MSG,
                        thumb=InputWebDocument(
                            "https://graph.org/file/b3e0cb631d36672092852.jpg",
                            0,
                            "image/jpeg",
                            [],
                        ),
                        buttons=IN_BTTS,
                    )
                ]
                return await event.answer(
                    res,
                    switch_pm=f"🤖: انا البوت الخاص ب {OWNER}",
                    switch_pm_param="start",
                )
            try:
                await func(event)
            except QueryIdInvalidError:
                pass
            except Exception as er:
                err = format_exc()

                def error_text():
                    return f"**#ERROR #INLINE**\n\nQuery: `{asst.me.username} {pattern}`\n\n**Traceback:**\n`{format_exc()}`"

                LOGS.exception(er)
                try:
                    await event.answer(
                        [
                            await event.builder.article(
                                title="Unhandled Exception has Occured!",
                                text=error_text(),
                                buttons=Button.url(
                                    "المساعدة", "https://t.me/Repthon_support"
                                ),
                            )
                        ]
                    )
                except QueryIdInvalidError:
                    LOGS.exception(err)
                except Exception as er:
                    LOGS.exception(er)
                    await asst.send_message(udB.get_key("LOG_CHANNEL"), error_text())

        asst.add_event_handler(wrapper, InlineQuery(pattern=pattern, **kwargs))

    return don
