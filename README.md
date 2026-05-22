# bale2bale

Minimal Telegram-to-Bale forwarder bot designed for "Melli Internet" situation when Bale servers still have access to the international network.

The bot fetches Telegram channels data through a Bale chat using [tg.i-c-a.su](https://tg.i-c-a.su), then sends new posts directly into a Bale channel.

---

## ❓ Installation

### First Steps on Bale
0. If you want forwarded messages to be sent into a group or channel, create one first. Otherwise, you can use your own UID in the following steps.
1. Create a new group or channel in Bale. This will act as the tunnel through which the bot receives message data from the API.
2. Make a bot using [BotFather](https://ble.ir/BotFather) bot in Bale. Save the Token somewhere safe.

NOTE: You'll need the UID of the two channels/groups you've made. In order to find the UID of a chat, open the chat in Bale Web version. In the URL of the page you'll see this format:
```web.bale.ai/chat?uid=<UID>```.
Copy the UID from here.


### Clone the repository:

```bash
git clone https://github.com/AriaMehrafza/bale2bale.git
cd bale2bale
```

If cloning doesn't work, you can download the zip from this [link](https://github.com/AriaMehrafza/bale2bale/archive/refs/heads/main.zip)

### 🐧 Linux
1. Create a virtual enviroment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Run setup:
```bash
chmod +x setup.sh
./setup.sh
```
The setup file installs requirements using pip, then inputs the config data from user.

### 🪟 Windows

1. Create a virtual environment and activate it:

```powershell
python -m venv venv
venv\Scripts\activate
```

2. Run setup:

```powershell
setup.bat
```

The setup file installs requirements using pip, then inputs the config data from user.

---

## 🚀 Running

Simply run:

```bash
python3 main.py
```

---

## ❌ Disclaimer

This project is provided for educational and legitimate use only. The author is not responsible for any misuse or legal consequences arising from the use of this project.

---

## ©️  License

This project is licensed under MIT License.

