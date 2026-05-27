import json
from datetime import datetime

import requests

from . import config


BOT_URL = f"https://tapi.bale.ai/bot{config.BOT_TOKEN}"
CID = config.TUN_UID

def now():
    """
    Return current local time formatted for logs.
    Example: 2026-05-10 | 12:34:56
    """
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    return f"{date} | {time}"


def _log(msg):
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

def gen_url(usr_name, limit=1) -> str:
    return f"http://tg.i-c-a.su/json/{usr_name}?limit={limit}"


def send_msg(text, chat_id, verbose=True):
    """ Sends a text message to a specific Bale chat """
    log = _log

    if not verbose:
        log = lambda *args, **kwargs: None

    res = requests.post(
        f"{BOT_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
        },
        timeout=10,
    )

    res.raise_for_status()

    log(f"Sent Message to Bale: {res.status_code}")
    return res


def send_doc(url, caption=None, chat_id=CID, verbose=True):
    """ Upload a document using direct-link to Bale """
    log = _log

    if not verbose:
        log = lambda *args, **kwargs: None

    payload = {
        "chat_id": chat_id,
        "document": url,
        "caption": caption,
    }

    log(f"Payload: {payload}")

    try:
        res = requests.post(
            f"{BOT_URL}/sendDocument",
            json=payload,
            timeout=25,
        )
        
        res.raise_for_status()

        js_res = json.dumps(res.json(), indent=4)
        file_id = res.json()['result']['document']['file_id'].strip()

        log(f"Result: {res.status_code}")
        log(f"Details: {js_res}")
        return file_id

    except Exception as e:
        log(f"Got error while uploading document to Bale: {e}")
        raise


def dl_doc(file_id, path, file_name, verbose=True):
    """ Download a document using File ID from Bale """
    log = _log

    if not verbose:
        log = lambda *args, **kwargs: None

    payload = {
        "file_id": file_id
    }
    
    try:
        res = requests.post(
            f"{BOT_URL}/getFile",
            json=payload,
        )

        log("\nfile_id: ", file_id)
        log("\npayload: ", payload)

        res.raise_for_status()

        log(json.dumps(res.json(), indent=4))

    except Exception as e:
        log(f"Got Error While Downloading the File: {e}")
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
        log(f"Got error while downloading the file: {e}")
        return False

    with open(f"{path}/{file_name}", "wb") as f:
        f.write(dl_res.content)

    return True


def dl_scrnsht(url, chat_id=CID, verbose=True):
    log = _log

    if not verbose:
        log = lambda *args, **kwargs: None

    # For more information visit: screenshotlayer.com
    api_url = f"http://api.screenshotlayer.com/api/capture?access_key={config.SL_TOKEN}&url={url}&fullpage=1"

    # Ask Bale API to Upload the screenshot
    payload = {
        "chat_id": chat_id,
        "document": api_url,
        "caption": f"اسکرین شات از: {url}"
    }

    try:
        res = requests.get(
            f"{BOT_URL}/sendDocument",
            json=payload,
        )
        res.raise_for_status()

    except Exception as e:
        log(f"Got exception while sending screenshot to Bale: {e}")
        return False

    log("Successfully sent screenshot in Bale")
    log(json.dumps(res.json(), indent=4))
