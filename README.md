# bale2bale

Minimal Telegram → Bale forwarder bot designed for "Melli Internet" situations where Bale servers still have access to the international network.

The bot fetches Telegram channels data **through Bale** using [tg.i-c-a.su](https://tg.i-c-a.su) and sends new posts directly into a Bale channel/group.

---

## Installation

### First Steps on Bale
0. If you don't have a channel/group in which you want the bot forward the messages, make one.
1. Make a new channel/group in Bale. This channel/group is gonna be the tunnel for bot to receive messages data from API.
2. Make a bot using [BotFather](https://ble.ir/BotFather) bot in Bale. Save the Token somewhere safe.

NOTE: You'll need the UID of the two channels/groups you've made. In order to find the UID of a chat, open the chat in Bale Web version. In the URL of the page you'll see this format:
```web.bale.ai/chat?uid=<UID>```.
Copy the UID from here.

### Linux

1. Clone the repository:

```bash
git clone https://github.com/AriaMehrafza/bale2bale.git
cd bale2bale
```

2. Create a virtual enviroment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Setup the configurations:

```bash
chmod +x setup.sh
./setup.sh
```

The setup file installs requirements using pip, then inputs the config data from user.

### Windows

1. Clone the repository:

```powershell
git clone https://github.com/AriaMehrafza/bale2bale.git
cd bale2bale
```

2. Create virtual environment and activate it:

```powershell
python -m venv venv
venv\Scripts\activate
```

3. Run setup:

```powershell
setup.bat
```

The batch setup script installs requirements and generates `config.py`.

---

## Running

Simply run:

```bash
python3 main.py
```

---

## Disclaimer

This project is provided for educational and legitimate use only. The author is not responsible for any misuse or legal consequences arising from the use of this project.

---

## License

This project is licensed under MIT License.
