# bale2bale

Minimal Telegram → Bale forwarder bot.

The bot fetches Telegram channels data **through Bale** using [tg.i-c-a.su](https://tg.i-c-a.su) and forwards new posts directly into a Bale channel/group.

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AriaMehrafza/bale2bale.git
cd bale2bale
```

2. Make a virtual enviroment:
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

This project is licensed uner MIT License
