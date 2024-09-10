from bs4 import BeautifulSoup
import requests
import re
from app.database import requests as db
from app.parse import telegram_parser as tg_parser

# парсер Телеграм

async def parser(url: str):
    if url.startswith('https://t.me'):
        return await tg_parser(url)
    
