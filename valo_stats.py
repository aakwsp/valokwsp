import os
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('VALO_API_KEY')
if not API_KEY:
    raise ValueError("val api key not found, check .env")

BASE_URL = os.getenv('VAL_API_BASE')


