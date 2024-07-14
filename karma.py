import logging
import os
import random
import string

import requests
import yaml
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Configure logging
logging.basicConfig(level=logging.INFO)

# USE YOUR ROTATING PROXY API IN DICT FORMAT http://user:pass@providerhost:port
proxies = {
    "http": "http://qnuomzzl-rotate:4i44gnayqk7c@p.webshare.io:80/",
    "https": "http://qnuomzzl-rotate:4i44gnayqk7c@p.webshare.io:80/",
}

session = requests.Session()

# Random DATA
letters = string.ascii_lowercase
First = "".join(random.choice(letters) for _ in range(6))
Last = "".join(random.choice(letters) for _ in range(6))
PWD = "".join(random.choice(letters) for _ in range(10))
Name = f"{First}+{Last}"
Email = f"{First}.{Last}@gmail.com"
UA = "Mozilla/5.0 (X11; Linux i686; rv:102.0) Gecko/20100101 Firefox/102.0"

CONFIG = yaml.load(open("config.yml", "r"), Loader=yaml.SafeLoader)
TOKEN = os.getenv("TOKEN", CONFIG["token"])
OWNER = int(os.getenv("OWNER", CONFIG["owner"]))
MONGO_URI = os.getenv("MONGO_URI", CONFIG["mongo"])
# Define the video URL
VIDEO_URL = "https://telegra.ph/file/6f0eed03464e9a95d7253.mp4"

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
