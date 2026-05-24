import requests
import json
import os
from utils import send_doc, dl_doc


def fetch_json(url: str, bot_token: str, tunnel_uid: int, retries=10) -> json:
#    if not url.startswith("https://") or not url.startswith("http://"):
#        raise Exception("Protocol is needed")
#        return False

    bad_js_res = json.dumps({"success": False})

    bale_url = f"https://tapi.bale.ai/bot{bot_token}"

    try:
        bl_res, file_id = send_doc(url, url, tunnel_uid)

        if not bl_res:
            raise Exception(e)

    except Exception as e:
        return bad_js_res

    print("Uploaded data to Bale successfull!")

    print("Making a directory (api_results) for the result to save")
    os.makedirs("api_results", exist_ok=True)

    print("Getting the file download link from Bale . . .")

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

    print(getFile_res.json())

    file_path = getFile_res.json()["result"]["file_path"]
    dl_link = f"https://tapi.bale.ai/file/bot{bot_token}/{file_path}"

    print("Got the download link successfully:", dl_link)

    try:
        dl_res = requests.get(
            dl_link,
            timeout=15
        )
        dl_res.raise_for_status()

    except Exception as e:
        raise Exception("Got exception while downloading the file:", e)
        return bad_js_res

    return json.dumps(dl_res.content)
