# NOTE:
# As Bale is recently unstable in downloading documents
# from direct-link (specially from foreign servers),
# if you have a SOCKS proxy (V2ray for e.g.),
# you can use it instead of Bale-tunnel by modifying the
# 'fetch_via_proxy' function on line 431 
# and replacing the 'fetch_via_bale' on line 583
# with 'fetch_via_proxy' :)

import time
import re
import os
import requests
import json
from html import unescape
from datetime import datetime
import config
import utils
import jalali


# Format: <CHANNEL_USERNAME>: <NUMBER_OF_MESSAGES>
channels = config.CHANNELS

CHNL_CID = config.CHNL_UID
BOT_URL = f"https://tapi.bale.ai/bot{config.BOT_TOKEN}"

def now():
    """
    Return current local time formatted for logs.
    Example: 2026-05-10 | 12:34:56
    """
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    return f"{date} | {time}"


def log(msg):
    """
    Prints logged format.

    For example:
        [2026-05-21 | 18:39:20] Making needed directories . . .
    """
    print(f"[{now()}] {msg}")


def make_dirs():
    """ Make needed directories """
    os.makedirs("datas/", exist_ok=True)
    os.makedirs("datas/last_ids/", exist_ok=True)
    os.makedirs("datas/api_results/", exist_ok=True)


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
    """ Convert Gregorian dates to Persian readable timestamps """

    if isinstance(raw_date, int):
        g = datetime.fromtimestamp(raw_date)
        return jalali.Gregorian(
            g.year, g.month, g.day
        ).persian_string() + f" | {g.strftime('%H:%M')}"

    if isinstance(raw_date, str):
        try:
            g = datetime.fromisoformat(raw_date.replace("Z", ""))
            p_date = jalali.Gregorian(
                g.year, g.month, g.day
            ).persian_string()
            return f"{p_date} | {g.strftime('%H:%M')}"
        except:
            return raw_date

    return "unknown time"


def retry_req(func, max_retries=5, delay=2, backoff=1.5):
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
            log(f"Retry {attempt}/{max_retries} failed: {e}")

            if attempt >= max_retries:
                log("Max retries reached, GIVING UP!")
                return None

            delay *= backoff
            log(f"Sleeping {delay} seconds before retry . . .")
            time.sleep(delay)


def send_msg(text, chat_id=CHNL_CID):
    """ Sends a text message to a specific Bale chat """
    def do_req():
        print("")
        log("Sending message to Bale...")
        print("------- BEGIN MESSAGE -------")
        print(text)
        print("-------- END MESSAGE --------")
        print("")
    
        res = requests.post(
            f"{BOT_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
            },
            timeout=10,
        )

        if res.status_code != 200:
            raise Exception(f"Bad status sending message: {res.status_code} | {res.text}\n")

        log(f"Sent Message to Bale: {res.status_code}")
        return res

    return retry_req(do_req)


def send_photo(photo_url, caption, chat_id=CHNL_CID):
    """ Sends a photo with caption to a specific Bale chat """
    def do_req():
        print("")
        log("Sending PHOTO to Bale . . .")
        print("------- CAPTION -------")
        print(caption)
        print("-----------------------")

        res = requests.post(
            f"{BOT_URL}/sendPhoto",
            json={
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": caption,
            },
            timeout=15,
        )

        if res.status_code == 413:
            log("Photo is larger than Bale limit")
            return send_msg(caption)

        elif res.status_code != 200:
            raise Exception(f"Bad status: {res.status_code} | {res.text}")

        log(f"Bale Photo OK: {res.status_code}")
        return res

    return retry_req(do_req)


def send_video(video_url, caption, chat_id=CHNL_CID):
    """ Sends a video with caption to a specific Bale chat """
    def do_req():
        print("")
        log("Sending VIDEO to Bale . . .")
        print("------ CAPTION ------")
        print(caption)
        print("---------------------")

        res = requests.post(
            f"{BOT_URL}/sendVideo",
            json={
                "chat_id": chat_id,
                "video": video_url,
                "caption": caption,
            },
            timeout=25
        )
        if res.status_code == 413:
            log("Video is larger than Bale limit")
            return send_msg(caption)

        elif res.status_code != 200:
            raise Exception(f"Bad status: {res.status_code} | {res.text}")

        log(f"Bale Video OK: {res.status_code}")
        return res

    return retry_req(do_req)


def send_audio(audio_url, caption, chat_id=CHNL_CID):
    """ Sends an audio file with caption to a specific Bale chat """
    def do_req():
        print("")
        log("Sending AUDIO to Bale . . .")
        print("------ CAPTION ------")
        print(caption)
        print("---------------------")

        res = requests.post(
            f"{BOT_URL}/sendAudio",
            json={
                "chat_id": chat_id,
                "audio": audio_url,
                "caption": caption,
            },
            timeout=15
        )

        if res.status_code == 413:
            log("Audio is larger than Bale limit")
            return send_msg(caption)

        elif res.status_code != 200:
            raise Exception(f"Bad status: {res.status_code} | {res.text}")

        log(f"Bale Audio OK: {res.status_code}")
        return res

    return retry_req(do_req)


def get_doc(file_id, path, file_name):
    """ Download a document using File ID from Bale """
    payload = {
        "file_id": file_id
    }
    
    try:
        res = requests.post(
            f"{BOT_URL}/getFile",
            json=payload,
        )

        print("\nfile_id: ", file_id)
        print("\npayload: ", payload)

        if res.status_code != 200:
            raise Exception(f"Bad Status: {res.status_code} | {res.text}")
            return False

    except Exception as e:
        log(f"Got error while getting the download link: {e}")
        return False

    file_path = res.json()['result']['file_path']

    try:
        dl_res = requests.get(
            f"https://tapi.bale.ai/file/bot{config.BOT_TOKEN}/{file_path}",
            timeout=15
        )

        if dl_res.status_code != 200:
            raise Exception(f"Bad Status: {res.status_code} | {res.text}")
    except Exception as e:
        log("Got error while downloading the file: ")
        return False

    with open(f"{path}/{file_name}", "wb") as f:
        f.write(dl_res.content)

    return True


def send_doc(url, caption=None, chat_id=CHNL_CID):
    """ Upload a document using direct-link to Bale """
    def do_req():
        payload = {
            "chat_id": chat_id,
            "document": url,
            "caption": caption,
        }

        try:
            res = requests.post(
                f"{BOT_URL}/sendDocument",
                json=payload,
                timeout=25,
            )
            
            if res.status_code == 413:
                log("Document is larger than Bale limit")
            elif res.status_code != 200:
                raise Exception(f"Bad Status: {res.status_code} | {res.text}")

            js_res = json.dumps(res.json(), indent=4)
            file_id = res.json()['result']['document']['file_id'].strip()

            print("\nResult: ", res.status_code)
            print("\n\nDetails: ", js_res)
            return True, file_id

        except Exception as e:
            log(f"Got error while uploading the document: {e}\n")
            return False, None
    
    return retry_req(do_req)


def parse_message(entry, channel_name, channel_username):
    """ Parses raw Telegram API message data into a clean text """
    msg_text = clean_html(entry.get("message", ""))

    media = entry.get("media")

    if msg_text == "" and not media:
        return None, None, None

    parts = [msg_text]

    msg_id = entry.get("id")

    media_type = "text"
    media_url = None

    if media:
        if media.get("_") == "messageMediaPhoto":
            media_type = "photo"
            media_url = build_media_url(channel_username, msg_id)

        elif media.get("_") == "messageMediaWebPage":
            webpage = media.get("webpage", {})
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

            elif is_video or (mime and mime.startswith("video")):
                media_type = "video"

            else:
                media_type = "document"

            media_url = build_media_url(channel_username, msg_id)

    time_str = format_time(entry.get("date")).replace("-", "/")

    parts.append("\n———")
    parts.append(f"🆔 {channel_name}")
    parts.append(f"⏰ {time_str}")

    caption = "\n".join([p for p in parts if p.strip()])

    final_text = "\n".join([p for p in parts if p.strip()])

    log("Parsed Message Preview:")
    print(final_text)
    print("--------------------------------------------------")

    return media_type, (media_url if media_type != "text" else None), caption


def load_last_ids(channel):
    """
    Loads recently forwarded Telegram message IDs for a channel.

    Used to avoid duplicate forwarding after restarts.
    """
    path = f"datas/last_ids/{channel}.txt"
    if os.path.exists(path):
        try:
            return [int(x) for x in open(path).read().strip().split()]
        except:
            return []
    return []


def save_last_ids(channel, last_ids, limit):
    """ Saves the last 5 sent message's IDs to their last_id file """
    with open(f"datas/last_ids/{channel}.txt", "w") as f:
        f.write(" ".join(map(str, last_ids[-limit:])))


def fetch_via_bale(channel: str, limit: int, retries=5) -> json:
    """ Fetchs Telegram messages using the API from Bale """
    log("Fetching messages through Bale")

    url = f"https://tg.i-c-a.su/json/{channel}?limit={limit}"
    
    while retries:
        time.sleep(5)

        retries -= 1
        try:
            log(f"Fetching {channel} via BALE!: {url}")
            try:
                send_res, file_id = send_doc(url)

                if not send_res:
                    continue

            except Exception as e:
                raise Exception(e)
                continue

            if get_doc(file_id, "datas/api_results", f"{channel}.json"):
                print("\n✅ Successfully downloaded file to local\n")

                with open(f"datas/api_results/{channel}.json", "r") as f:
                    try:
                        return json.load(f)
                    except json.JSONDecodeError:
                        return None

        except Exception as e:
            log(f"❌ Error fetching {channel}: {e}\n")
            time.sleep(10)

    if retries == -1:
        return None


def fetch_via_proxy(channel: str, limit: int, retries=5) -> json:
    """
    Fetchs Telegram messages using SOCKS proxy.
    (usable if you have a SOCKS proxy which can fetch from the API)
    """
    log("Fetching messages through Proxy")

    proxies = {
        # Add your SOCKS proxy here.
        # For e.g. if the proxy is running on localhost port 1080:
        "http": "socks5h://127.0.0.1:1080",
        "https": "socks5h://127.0.0.1:1080"
    }
 
    url = f"https://tg.i-c-a.su/json/{channel}?limit={limit}"
   
    while retries:
        try:
            res = requests.get(url, proxies=proxies)
            
            if res.status_code != 200:
                raise Exception(f"Status code: {res.status_code} | Details: {res.text}")

            return res.json()

        except Exception as e:
            log(f"❌ Error fetching {channel}: {e}\n")
            time.sleep(10)

        retries -= 1

    if retries == 0:
        return {}


def pin_msg(msg_id, chat_id=CHNL_CID):
    """ Pins a message in a chat (currently unused) """
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
        log(f"Got error while pinning message: {e}")
        return

    return res


def unpin_msg(msg_id, chat_id=CHNL_CID):
    """ Unpins a message in a chat (currently unused) """
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
        log(f"Got error while un-pinning message: {e}")
        return

    return res


def update_chnl_desc(chat_id):
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

    log("List ready. Sending the request to Bale . . .")

    try:
        res = requests.post(
            f"{BOT_URL}/setChatDescription",
            json=payload,
        )
        print(json.dumps(res.json(), indent=4)) 

    except Exception as e:
        log("Got error while editting list: ", e)
        return

    print("🆗 DONE!\n")


def main():
    print("\n============================================================")
    log("Bale Telegram Forwarder Bot Running")
    print("============================================================\n")

    log("Making needed directories . . .")
    make_dirs()
    log("Directories done!")

    last_ids = {ch: load_last_ids(ch) for ch in channels.keys()}

    while True:
        for channel, limit in channels.items():
            print(f"\n[{now()}] Checking channel: {channel}\n")

            data = fetch_via_bale(channel, limit)

            if not data:
                log("Empty fetch result")
                continue

            channel_name = data.get("chats", [{}])[0].get("title", channel)
            messages = data.get("messages", [])

            log(f"Total fetched from {channel}: {len(messages)}")

            if not messages:
                log(f"No messages in channel {channel}.")
                continue

            messages.sort(key=lambda x: x.get("id", 0))

            seen_ids = set(last_ids[channel])
            new_msgs = [m for m in messages if m.get("id", 0) not in seen_ids]

            log(f"New messages: {len(new_msgs)}")

            for entry in new_msgs:
                msg_id = entry.get("id")
                log(f"➜ Processing message ID {msg_id}\n")

                media_type, file_url, caption = parse_message(entry, channel_name, channel)
                log(f"MEDIA TYPE IS: {media_type}")

                result = None
                if media_type == "photo":
                    result = send_photo(file_url, caption)
                elif media_type == "video":
                    result = send_video(file_url, caption)
                elif media_type == "audio":
                    result = send_audio(file_url, caption)
                elif media_type == "document":
                    result = send_doc(file_url, caption)
                elif media_type == "text":
                    result = send_msg(caption)

                if result:
                    log(f"Sent message {msg_id}")
                    last_ids[channel].append(msg_id)
                    last_ids[channel] = last_ids[channel][-limit:]
                    save_last_ids(channel, last_ids[channel], limit)
                else:
                    log(f"Failed to send message {msg_id} after retries, SKIPPED!")

                time.sleep(3)
                
        # NOTE:
        # The below function, updates the channel/group description with
        # the supported channels list and the last Telegram check time.
        # Uncomment only if you're sending the messages in a group/channel.

        # log("--- Updating Channels UPDT in Bale ------")
        # update_chnl_list(CHNL_CID)

        sleep_time = 180
        print(f"\n\n[{now()}] Sleeping for {sleep_time / 60} minutes . . .")
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
