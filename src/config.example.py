# Tokens
BOT_TOKEN = # Bale Bot Token

# API Tokens
SL_TOKEN = # Needed if you want to use utils.dl_scrnsht

# Bale UIDs
CHNL_UID = # The main chat UID in which you receive forwarded messages
DATAS_UID = # The chat which the bot uses as tunnel to receieve datas from API

# The list of channels that the bot would forward message from
CHANNELS = {
  # Fromat: <CHANNEL_USERNAME>:<COUNT> (count is the number of messages it fetches from API each time, maximum is 100 (API limit)
  # For e.g.:
  "jadivarlog":5,
  # Now it would fetch the last 5 messages of 'jadivarlog' each time
}
