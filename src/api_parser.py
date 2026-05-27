import json
import os

import requests

from .utils import(
    _log,
    now,
    send_doc,
    dl_doc
)

BASE_URL = f"https://tapi.bale.ai/bot"


def fetch_json(url: str, bot_token: str, tun_uid: int, verbose=True, retries=10) -> dict:
    """ Fetch a JSON file using Bale Tunnel """
    log = _log

    bale_url = f"{BASE_URL}{bot_token}"

    if not verbose:
        log = lambda *args, **kwargs: None

    # TODO: Replace with a class for better exception handling
    bad_js_res = json.dumps({"success": False})

    try:
        file_id = send_doc(url, url, tun_uid, verbose)

        if not file_id:
            raise Exception("File upload failed")

    except Exception as e:
        raise

    log("Uploaded data to Bale successfull!")

    log("Making a directory (api_results) for the result to save")
    os.makedirs("api_results", exist_ok=True)

    log("Getting the file download link from Bale . . .")

    try:
        getFile_payload = { "file_id": file_id }

        getFile_res = requests.post(
            f"{bale_url}/getFile",
            json=getFile_payload
        )
        getFile_res.raise_for_status()

    except Exception as e:
        raise Exception("Got exception while getting download link:", e)
        return bad_js_res

    log(getFile_res.json())

    file_path = getFile_res.json()["result"]["file_path"]
    dl_link = f"https://tapi.bale.ai/file/bot{bot_token}/{file_path}"

    log(f"Got the download link successfully: {dl_link}")

    try:
        dl_res = requests.get(
            dl_link,
            timeout=15
        )
        dl_res.raise_for_status()

    except Exception as e:
        raise Exception("Got exception while downloading the file:", e)
        return bad_js_res

    try:
        return json.loads(dl_res.text)

    except json.JSONDecodeError:
        return bad_js_res