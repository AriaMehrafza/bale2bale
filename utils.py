import requests
import json
import config


BALE_URL= f"https://tapi.bale.ai/bot{config.BOT_TOKEN}"
CID = config.DATAS_UID

def gen_url(usr_name, limit=1) -> str:
    return f"http://tg.i-c-a.su/json/{usr_name}?limit={limit}"


def send_doc(url, caption=None, chat_id=CID):
    """ Upload a document using direct-link to Bale """
    payload = {
        "chat_id": chat_id,
        "document": url,
        "caption": caption,
    }

    try:
        res = requests.post(
            f"{BALE_URL}/sendDocument",
            json=payload,
            timeout=25,
        )
        
        if res.status_code != 200:
            raise Exception(f"Bad Status: {res.status_code} | {res.text}")

        js_res = json.dumps(res.json(), indent=4)
        file_id = res.json()['result']['document']['file_id'].strip()

        print("\nResult: ", res.status_code)
        print("\n\nDetails: ", js_res)
        return True, file_id
    except Exception as e:
        print("Got error while sending document: ", e)
        return False


def dl_doc(file_id, path, file_name):
    """ Download a document using File ID from Bale """
    payload = {
        "file_id": file_id
    }
    
    try:
        res = requests.post(
            f"{BALE_URL}/getFile",
            json=payload,
        )

        print("\nfile_id: ", file_id)
        print("\npayload: ", payload)

        if res.status_code != 200:
            raise Exception(f"Bad Status: {res.status_code} | {res.text}")

        print(json.dumps(res.json(), indent=4))
    except Exception as e:
        print("Got Error While Downloading the File: ", e)
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
        print("Got error during downloading the file: ", e)
        return False

    with open(f"{path}/{file_name}", "wb") as f:
        f.write(dl_res.content)

    return True

def dl_scrnsht(url, chat_id=CID):
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
            f"{BALE_URL}/sendDocument",
            json=payload,
        )

        if res.status_code != 200:
            raise Exception(f"{res.status_code}:\n{res.text}")
    except Exception as e:
        print("Got exception while sending screenshot to Bale: ", e)
        return False

    print("Successfully sent screenshot in Bale")
    print(json.dumps(res.json(), indent=4))