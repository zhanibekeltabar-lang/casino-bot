import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID", 0))

MIN_BET = 1
MAX_BET = 10**18          # іс жүзінде шексіз
START_BALANCE = 1000
