import time
import json
import os

import asyncio
import aiohttp
import requests

from . import config
from .main import (
    clean_html,
    format_time,
    send_msg,
    send_photo,
    send_video,
    send_audio,
    send_doc,
    parse_message,
    fetch_via_bale,
    fetch_via_proxy,
    APIFetchError,
)


bale_url = f"https://tapi.bale.ai/bot{config.BOT_TOKEN}"
offset = 0

request_queue = asyncio.Queue()

ADMIN_UID = config.ADMIN_UID
LOGS_CHNL = config.LOGS_CHNL

async def handle_channel(chat_id: int, channel: str, limit=5, retries=4) -> None:
    non_public = set()
    if os.path.exists("datas/not-public.txt"):
        with open("datas/not-public.txt", "r") as f:
            non_public = {line.strip() for line in f}

    if channel in non_public:
        await asyncio.to_thread(
            send_msg,
            f"این کانال وجود ندارد و یا عمومی نیست!",
            chat_id
        )

        return

    data = await asyncio.to_thread(
        fetch_via_bale,
        channel, limit, retries
    )

    if not data:
        # TODO: Remove this message as it's unnecessary for the user.
        await asyncio.to_thread(
            send_msg,
            f"در حال حاضر بله مالیده و پس از"
            f" {retries} "
            f"تلاش، ارتباط برقرار نشد!",
            chat_id
        )

        await asyncio.to_thread(
            send_msg,
            f"در تلاش مجدد برای دریافت پیام ها...",
            chat_id
        )

        try:
            data = await asyncio.to_thread(
                fetch_via_proxy,
                channel, limit
            )
        
        except APIFetchError as e:
            await asyncio.to_thread(
                send_msg,
                f"هنگام دریافت پیام ها، ارور زیر رخ داد:\n"
                f"کد ارور: {e.status_code}\n"
                f"جزئیات: {e.msg}\n",
                chat_id
            )

            if e.status_code == "403" or e.msg == "CHANNEL_PRIVATE" or e.msg == "This is not a public channel":
                with open("datas/not-public.txt", "a") as f:
                    f.append(f"\n{channel}")

            return

        except Exception as e:
            await asyncio.to_thread(
                send_msg,
                f"به دلیل ارور زیر پیام ها دریافت نشد:\n"
                f"{e}",
                chat_id
            )

            return

        
    await asyncio.to_thread(
        send_msg,
        ("پیام ها با موفقیت دریافت شد، درحال ارسال پیام ها"),
        chat_id
    )

    channel_name = data.get("chats", [{}])[0].get("title", channel)

    messages = data.get("messages", [])

    messages.sort(key=lambda x: x.get("id", 0))

    msgs = [m for m in messages]

    cnt = 1
    for entry in msgs:
        msg_id = entry.get("id")

        media_type, payload, caption = parse_message(entry, channel_name, channel)

        caption += f"\n💾 {cnt}/{limit}"
        cnt += 1

        result = None
        if media_type == "photo" and payload:
            result = await asyncio.to_thread(
                send_photo,
                payload, caption, chat_id
            )

        elif media_type == "video" and payload:
            result = await asyncio.to_thread(
                send_video,
                payload, caption, chat_id
            )

        elif media_type == "audio" and payload:
            result = await asyncio.to_thread(
                send_audio,
                payload, caption, chat_id
            )

        elif media_type == "text" and caption:
            result = await asyncio.to_thread(
                send_msg,
                caption, chat_id
            )

        elif media_type == "document" and payload:
            result = await asyncio.to_thread(
                send_doc,
                payload, caption, chat_id
            )

        if not result:
            await asyncio.to_thread(
                send_msg,
                "در حال حاضر بله مالید و پس از 5 تلاش، پیام ارسال نشد!",
                chat_id
            )

        await asyncio.sleep(0.3)


async def queue_worker() -> None:
    while True:
        chat_id, channel_username, limit = await request_queue.get()

        try:
            print(f"Processing: {channel_username} (limit={limit})")

            rec_msg = (
                f"درحال دریافت"
                f" {limit} "
                f"پیام آخر کانال"
                f" {channel_username}"
                f"\n(ممکن است کمی زمان بر باشد)"
            )

            await asyncio.to_thread(
                send_msg,
                rec_msg,
                chat_id
            )

            await handle_channel(
                chat_id,
                channel_username,
                limit
            )

        except Exception as e:
            print("Queue worker error:", e)
        
        finally:
            request_queue.task_done()


async def main() -> None:
    offset = 0

    async with aiohttp.ClientSession() as session:
        for _ in range(1):
            asyncio.create_task(queue_worker())

        while True:
            payload = {
                "offset": offset,
                "timeout": 30,
            }

            try:
                async with session.post(
                    f"{bale_url}/getUpdates",
                    json=payload
                ) as res:
                    if res.status != 200:
                        raise Exception(
                            f"Status code: {res.status}, text: {res.text}"
                        )

                    data = await res.json()

                if data.get("result"):
                    for update in data["result"]:
                        offset = update["update_id"] + 1

                        is_private = False
                        if update["message"]["chat"]["type"] == "private":
                            is_private = True

                        msg = update.get("message") or update.get("edited_message")
                        if not msg:
                            continue

                        user = msg.get("from", {})
                        username = user.get("username")
                        name = (
                            user.get("first_name", "")
                            + " "
                            + user.get("last_name", "")
                        ).strip()

                        msg_text = msg.get("text", "")

                        if username:
                            user_tag = f"@{username}"
                        else:
                            user_tag = "(no username)"

                        chat_id = msg["chat"]["id"]
                        if chat_id != ADMIN_UID:
                            print("Recieved a message from non-admin:", chat_id)
                            print("Text:", msg_text, '\n')

                            await asyncio.to_thread(
                                send_msg,
                                f"Bot Recieved a message: {user_tag} | {name} | {chat_id}\n"
                                f"Content:\n{msg_text}",
                                LOGS_CHNL
                            )

                        if msg_text.strip() == "/start":
                            if not is_private:
                                continue

                            help_msg = (
                                "نحوه استفاده:\n"
                                "/get <CHANNEL_USERNAME> <LIMIT>\n\n"
                                "<CHANNEL_USERNAME>: یوزرنیم چنل موردنظر\n"
                                "<COUNT> (اختیاری): تعداد پیام دریافتی\n\n"
                                "برای مثال، دستور:\n"
                                "/get jadivarlog 5\n"
                                "5 پیام آخر کانال jadivarlog در تلگرام را دریافت میکند.\n\n"
                                "(درصورت عدم تعیین مقدار count، به طور پیش فرض 5 پیام آخر ارسال میشود)"
                            )

                            await asyncio.to_thread(
                                send_msg,
                                help_msg,
                                chat_id
                            )

                            continue

                        if msg_text.strip().startswith("/get"):
                            chnl_data = msg_text.strip()[5:]

                            br = -1
                            for i in range(0, len(chnl_data) - 1):
                                if chnl_data[i] == ' ':
                                    br = i

                            limit = int(5)
                            if br == -1:
                                channel_username = chnl_data
                            else:
                                channel_username = chnl_data[:br]
                                limit = chnl_data[br+1:]

                            try:
                                limit = int(limit)
                            except ValueError:
                                await asyncio.to_thread(
                                    send_msg,
                                    "لیمیت باید عدد باشد",
                                    chat_id
                                )

                            if limit <= 0:
                                await asyncio.to_thread(
                                    send_msg,
                                    "مقدار limit غیرمجاز است",
                                    chat_id
                                )
                                continue

                            if channel_username.startswith("@"):
                                channel_username = channel_username[1:]
                                                        
                            if len(channel_username) == 0:
                                await asyncio.to_thread(
                                    send_msg,
                                    "یوزرنیم درست نمی باشد",
                                    chat_id
                                )
                                continue

                            await asyncio.to_thread(
                                send_msg,
                                f"درخواست شما در صف قرار گرفت.\n"
                                f"تعداد درخواست های منتظر در صف: {request_queue.qsize()+1}",
                                chat_id
                            )

                            await request_queue.put(
                                (
                                    chat_id,
                                    channel_username,
                                    limit
                                )
                            )

            except Exception as e:
                print("Got exception while working (in worker): ", e)
                await asyncio.sleep(2)
                continue

            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())