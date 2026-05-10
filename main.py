import time
import re
import os
import sys
import select
import requests
import json
from html import unescape
from datetime import datetime
import config
import utils


# Format: "channel_username": number of messages
channels = config.CHANNELS

CHNL_CID = config.CHNL_UID
BOT_URL = f"https://tapi.bale.ai/bot{config.BOT_TOKEN}"

def now():
    """
    Return current local time formatted for logs.
    Example: 2026-05-10 | 12:34:56
    """
    return datetime.now().strftime("%Y-%m-%d | %H:%M:%S")


def make_dirs():
    """ Make needed directories """
    os.makedirs("datas", exist_ok=True)
    os.makedirs("api_results", exist_ok=True)


def build_media_url(channel_uname: str, msg_id: int):
    """ Builds a downloadable media URL for a Telegram message """
    return f"https://tg.i-c-a.su/media/{channel_uname}/{msg_id}"


def clean_html(text: str):
    """ Converts recieved HTML format from API to clean text """
    if not text:
        return ""

    text = unescape(text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

    def repl(match):
        return match.group(1)

    text = re.sub(
        r'<a\s+href="([^"]+)".*?>.*?</a>',
        repl,
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n+", "\n", text).strip()

    return text


def clean_proxy(text: str):
    """
    (Made specailly for @ProxyMTProto.)
    Convert Telegram proxy information into a clickable proxy URL.
    """
    lines = ["", "", ""]
    cnt = 0
    for c in text:
        if cnt == 3:
            break

        if c == '\n':
            cnt += 1
            continue
        else:
            lines[cnt] += c

    server = lines[0][8:]
    port = lines[1][6:]
    secret = lines[2][8:]

    return f"https://t.me/proxy?server={server}&port={port}&secret={secret}"


def format_time(raw_date):
    """ Normalize Telegram date formats into readable timestamps """
    if isinstance(raw_date, int):
        return datetime.fromtimestamp(raw_date).strftime("%Y-%m-%d | %H:%M")

    if isinstance(raw_date, str):
        try:
            return datetime.fromisoformat(raw_date.replace("Z", "")).strftime(
                "%Y-%m-%d | %H:%M"
            )
        except:
            return raw_date

    return "unknown time"


def retry_req(func, max_retries=10, delay=2, backoff=1.5):
    """
    Execute a function with automatic retry handling.

    Primarily used for unstable Bale API requests.
    """
    attempt = 0

    while attempt < max_retries:
        try:
            return func()
        except Exception as e:
            attempt += 1
            print(f"[{now()}] Retry {attempt}/{max_retries} failed: {e}")

            if attempt >= max_retries:
                print(f"[{now()}] [-] Max retries reached, GIVING UP!")
                return None

            delay *= backoff
            print(f"[{now()}] [#] Sleeping {delay} seconds before retry . . .")
            time.sleep(delay)


def send_msg_to_bale(text, chat_id=CHNL_CID):
    """ Sends a text message to a specific Bale chat """
    def do_req():
        print("")
        print(f"[{now()}] Sending message to Bale...")
        print("------- BEGIN MESSAGE -------")
        print(text)
        print("-------- END MESSAGE --------")
        print("")
    
        r = requests.post(
            f"{BOT_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
            },
            timeout=10,
        )

        if r.status_code != 200:
            raise Exception(f"Bad status: {r.status_code} | {r.text}\n")
            print(f"Message is: {text}")

        print(f"[{now()}] Bale OK: {r.status_code}")
        return r

    return retry_req(do_req)


def send_photo_to_bale(photo_url, caption, chat_id=CHNL_CID):
    """ Sends a photo with caption to a specific Bale chat """
    def do_req():
        print("")
        print(f"[{now()}] Sending PHOTO to Bale . . .")
        print("------- CAPTION -------")
        print(caption)
        print("-----------------------")

        r = requests.post(
            f"{BOT_URL}/sendPhoto",
            json={
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": caption,
            },
            timeout=15,
        )

        if r.status_code != 200:
            raise Exception(f"Bad status: {r.status_code} | {r.text}")

        print(f"[{now()}] Bale Photo OK: {r.status_code}")
        return r

    return retry_req(do_req)


def send_video_to_bale(video_url, caption, chat_id=CHNL_CID):
    """ Sends a video with caption to a specific Bale chat """
    def do_req():
        print("")
        print(f"[{now()}] Sending VIDEO to Bale . . .")
        print("------ CAPTION ------")
        print(caption)
        print("---------------------")

        r = requests.post(
            f"{BOT_URL}/sendVideo",
            json={
                "chat_id": chat_id,
                "video": video_url,
                "caption": caption,
            },
            timeout=25
        )

        if r.status_code == 413:
            print(f"[{now()}] [-] Video is larger than Bale limit")
            return send_msg_to_bale(caption)

        elif r.status_code != 200:
            print(f"\n\nVideo URL: {video_url}\n\n")
            raise Exception(f"Bad status: {r.status_code} | {r.text}")

        print(f"[{now()}] Bale Video OK: {r.status_code}")
        return r

    return retry_req(do_req)


def send_audio_to_bale(audio_url, caption, chat_id=CHNL_CID):
    """ Sends an audio file with caption to a specific Bale chat """
    def do_req():
        print("")
        print(f"[{now()}] Sending AUDIO to Bale . . .")
        print("------ CAPTION ------")
        print(caption)
        print("---------------------")

        r = requests.post(
            f"{BOT_URL}/sendAudio",
            json={
                "chat_id": chat_id,
                "audio": audio_url,
                "caption": caption,
            },
            timeout=15
        )

        if r.status_code != 200:
            raise Exception(f"Bad status: {r.status_code} | {r.text}")

        print(f"[{now()}] Bale Audio OK: {r.status_code}")
        return r

    return retry_req(do_req)


def parse_message(entry, channel_name, channel_username):
    """ Parses raw Telegram API message data into a clean text """
    msg_text = clean_html(entry.get("message", ""))

    media = entry.get("media")

    if msg_text == "" and not media:
        return None, None, None

    parts = [msg_text]

    media = entry.get("media")
    msg_id = entry.get("id")

    media_type = "text"
    media_url = None

    if media:
        if media.get("_") == "messageMediaPhoto":
            media_type = "photo"
            media_url = build_media_url(channel_username, msg_id)

        elif media.get("_") == "messageMediaWebPage":
            webpage = media.get("webpage", {})
            if webpage.get("title"):
                parts.append(f"🌐 {webpage.get('title')}")
            if webpage.get("url"):
                parts.append(webpage.get("url"))

        elif media.get("_") == "messageMediaDocument":
            doc = media.get("document", {})
            mime = doc.get("mime_type", "")
            
            filename = None
            is_audio = False
            is_video = False

            for attr in doc.get("attributes", []):
                t = attr.get("_")

                if t == "documentAttributeFilename":
                    filename = attr.get("file_name")

                if t == "documentAttributeAudio":
                    is_audio = True

                if t == "documentAttributeVideo":
                    is_video = True

            if is_audio or (mime and mime.startswith("audio")):
                media_type = "audio"
                media_url = build_media_url(channel_username, msg_id)

            elif is_video or (mime and mime.startswith("video")):
                media_type = "video"
                media_url = build_media_url(channel_username, msg_id)

    time_str = format_time(entry.get("date"))

    parts.append("\n———")
    parts.append(f"🆔 {channel_name}")
    parts.append(f"⏰ {time_str}")

    caption = "\n".join([p for p in parts if p.strip()])

    final_text = "\n".join([p for p in parts if p.strip()])

    print(f"[{now()}] Parsed Message Preview:")
    print(final_text)
    print("--------------------------------------------------")

    return media_type, (media_url if media_type != "text" else caption), caption


def load_last_ids(channel):
    """
    Loads recently forwarded Telegram message IDs for a channel.

    Used to avoid duplicate forwarding after restarts.
    """
    path = f"datas/last_id_{channel}.txt"
    if os.path.exists(path):
        try:
            return [int(x) for x in open(path).read().strip().split()]
        except:
            return []
    return []


def save_last_ids(channel, last_ids, limit):
    """ Saves the last 5 sent message's IDs to their last_id file """
    with open(f"datas/last_id_{channel}.txt", "w") as f:
        f.write(" ".join(map(str, last_ids[-limit:])))


def fetch_telegram_from_bale(channel, limit) -> json:
    """ 
    Fetchs Telegram messages using the API from Bale 

    NOTE: Retries forever until succssful.
    """
    url = f"https://tg.i-c-a.su/json/{channel}?limit={limit}"
    
    while True:
        try:
            print(f"[{now()}] 🔵 Fetching {channel} via BALE!: {url}\n")
            try:
                _, file_id = utils.send_doc(url)
            except Exception as e:
                raise Exception(e)

            if utils.dl_doc(file_id, "api_results", f"{channel}.json"):
                print("\n✅ Successfully downloaded file to local\n")

                with open(f"api_results/{channel}.json", "r") as f:
                    return json.load(f)

        except Exception as e:
            print(f"[{now()}] ❌ Error fetching {channel}: {e}\n")
            time.sleep(10)


def pin_msg(msg_id, chat_id=CHNL_CID):
    """ Pins a message in a chat """
    payload = {
        "chat_id": chat_id,
        "message_id": msg_id,
    }

    try:
        res = requests.post(
            f"{BOT_URL}/pinChatMessage",
            json=payload,
            timeout=10,
        )
    except Exception as e:
        print("Got error while pinning message: ", e)
        return

    return res


def unpin_msg(msg_id, chat_id=CHNL_CID):
    """ Unpins a message in a chat """
    payload = {
        "chat_id": chat_id,
        "message_id": msg_id,
    }

    try:
        res = requests.post(
            f"{BOT_URL}/unPinChatMessage",
            json=payload,
            timeout=10,
        )
    except Exception as e:
        print(f"[{now()}] Got error while pinning message: ", e)
        return

    return res


def update_chnl_list(chat_id):
    """
    Update the channel description,
    containing the current supported channles
    and the last Telegram check time.
    """

    msg_lines = ["خودکار، قدرت گرفته از tg.i-c-a.su\n"]
    msg_lines.append(f"آخرین زمان به‌روزرسانی: {now()}\n")
    msg_lines.append("لیست کانال‌های پشتیبانی شده:")
    for key in channels:
        msg_lines.append(f"- t.me/{key}")

    text = "\n".join(msg_lines)

    payload = {
        "chat_id": chat_id,
        "description": text,
    }

    print(f"[{now()}] List ready. Sending the request to Bale . . .")

    try:
        res = requests.post(
            f"{BOT_URL}/setChatDescription",
            json=payload,
        )
        print(json.dumps(res.json(), indent=4)) 
    except Exception as e:
        print(f"[{now()}] Got error while editting list: ", e)
        return

    print("🆗 DONE!\n")


def main():
    print("\n============================================================")
    print(f"[{now()}] Bale Telegram Forwarder Bot Running")
    print("============================================================\n")

    print(f"[{now()}] Making needed directories . . .")
    make_dirs()
    print(f"[{now()}] Directories done!")

    last_ids = {ch: load_last_ids(ch) for ch in channels.keys()}

    while True:
        for channel, limit in channels.items():
            print(f"\n[{now()}] Checking channel: {channel}")

            data = fetch_telegram_from_bale(channel, limit)

            channel_name = data.get("chats", [{}])[0].get("title", channel)
            messages = data.get("messages", [])

            print(f"[{now()}] Total fetched from {channel}: {len(messages)}")

            if not messages:
                print(f"[{now()}]  No messages in channel {channel}.")
                continue

            messages.sort(key=lambda x: x.get("id", 0))

            seen_ids = set(last_ids[channel])
            new_msgs = [m for m in messages if m.get("id", 0) not in seen_ids]

            print(f"[{now()}] New messages: {len(new_msgs)}")

            for entry in new_msgs:
                msg_id = entry.get("id")
                print(f"[{now()}] ➜ Processing message ID {msg_id}\n")

                media_type, payload, caption = parse_message(entry, channel_name, channel)
                print(f"[{now()}] MEDIA TYPE IS: {media_type}")

                result = None
                if media_type == "photo" and payload:
                    result = send_photo_to_bale(payload, caption)
                elif media_type == "video" and payload:
                    result = send_video_to_bale(payload, caption)
                elif media_type == "audio" and payload:
                    result = send_audio_to_bale(payload, caption)
                elif media_type == "text" and payload:
                    result = send_msg_to_bale(payload)

                if result:
                    print(f"[{now()}] [+] Sent message {msg_id}")
                    last_ids[channel].append(msg_id)
                    last_ids[channel] = last_ids[channel][-limit:]
                    save_last_ids(channel, last_ids[channel], limit)
                else:
                    print(f"[{now()}] [-] Failed to send message {msg_id} after retries, SKIPPED!")

                time.sleep(3)
                
        print(f"[{now()}] --- Updating Channels UPDT in Bale ------")
        update_chnl_list(CHNL_CID)

        sleep_time = 180
        print(f"\n\n[{now()}] Sleeping for {sleep_time / 60} minutes . . .")
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
