from app.parse.telegram_parser import tg_parser

async def parser(url: str):
    if url.startswith('https://t.me'):
        return await tg_parser(url)