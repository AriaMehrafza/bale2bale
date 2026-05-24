# Tokens
# Bale Bot Token
BOT_TOKEN = "123456789:abcdIuZmK5qNEm2A1BhUaAg7MPJv1O9KCcBQB2ro"


# API Tokens
# Needed if you want to use utils.dl_scrnsht. You can get an API key from 'screenshotlayer.com'.
# SL_TOKEN =


# Bale UIDs
# The main chat UID in which you receive forwarded messages.
CHNL_UID = 0123456789

# The chat which the bot uses as tunnel to receieve datas from API.
TUN_UID = 0123456789


# The list of channels that the bot would forward message from
CHANNELS = {
  # Fromat: <CHANNEL_USERNAME>:<COUNT> (count is the number of messages it fetches from API each time, maximum is 100 (API limit)).
  # For e.g.:
  "jadivarlog":5,
  # Now it would fetch the last 5 messages of 't.me/jadivarlog' each time.
}
