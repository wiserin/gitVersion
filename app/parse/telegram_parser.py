from bs4 import BeautifulSoup
import requests
import re
from app.database import requests as db

# парсер Телеграм
    
async def tg_parser(url: str):
    """
    Парсит страницу Телеграм и извлекает текст, фото и видео из последнего сообщения.
    Если объект не существует, удаляет его из базы данных.
    """
    html = await request(url)
    text = await parse(html)

    # удаление несуществующего объекта
    if text == 'Delete':
        # await db.delete_newsmaker(url)
        return {'text': f'Ошибка при получении текста.\nURL:{url}',
                'photo': False,
                'video': False}

    new = Telegram_news(text)

    new_text = new.get_text()
    new_photo = new.get_photo()
    new_video = new.get_video()

    return {'text': new_text,
            'photo': new_photo,
            'video': new_video}

# получение html
async def request(url: str):
    """
    Выполняет HTTP-запрос к указанному URL и возвращает HTML-код страницы.
    """
    r = requests.get(url)
    html = r.text
    return html

# получение последней новости
async def parse(html_: str):
    """
    Парсит HTML-код и извлекает последний пост из Телеграм-канала.
    Возвращает объект BeautifulSoup или 'Delete', если постов нет.
    """
    try:
        soup = BeautifulSoup(html_, "html.parser")
        text = str(soup.find_all('div', attrs={'class': 'tgme_widget_message_wrap'})[-1])
        new_soup = BeautifulSoup(text, "html.parser")
        return new_soup
    except IndexError:
        return 'Delete'

# обработка новостей
class Telegram_news():
    """
    Класс для обработки и извлечения данных из последнего сообщения Телеграм-канала.
    """
    cleaner_for_photo = r"url\('([^']+)'\)"
    cleaner = re.compile(r'<.*?>')
    ALLOWED_TAGS = ['b', 'i', 'u', 'a']
    ALLOWED_ATTRIBUTES = {'a': ['href']}

    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def clean_html(self, text):
        """
        Функция для очистки HTML и сохранения разрешенных тегов, заменяя <br> на \n.
        """
        soup = BeautifulSoup(text, 'html.parser')
        
        # Заменяем <br> на \n
        for br in soup.find_all("br"):
            br.replace_with("\n")

        for tag in soup.findAll(True):
            if tag.name not in self.ALLOWED_TAGS:
                tag.unwrap()
            else:
                # Сохранение разрешенных атрибутов
                attrs = {attr: tag[attr] for attr in tag.attrs if attr in self.ALLOWED_ATTRIBUTES.get(tag.name, [])}
                tag.attrs = attrs
        
        return str(soup)

    def get_text(self):
        """
        Извлекает текст сообщения из HTML.
        Возвращает очищенный текст или False в случае ошибки.
        """
        try:
            text = str(self.soup.find_all('div', attrs={'class': 'tgme_widget_message_text js-message_text'})[0])
            clean_text = self.clean_html(text)
            return clean_text
        except Exception as e:
            print(f"An error occurred while getting text: {e}") if not IndexError else ''
            return False

    def get_video(self):
        """
        Извлекает ссылки на видео из сообщения.
        Возвращает список ссылок или False в случае ошибки.
        """
        try:
            videos = []
            video_tags = self.soup.find_all('video', attrs={'class': 'tgme_widget_message_video'})
        
            for video in video_tags:
                src = video.get('src')
                if src:
                    videos.append(src)
            
            return videos if videos else False
        except Exception as e:
            print(f"An error occurred while getting videos: {e}")
            return False

    def get_photo(self):
        """
        Извлекает ссылки на фотографии из сообщения.
        Возвращает список ссылок или False в случае ошибки.
        """
        try:
            text = str(self.soup.find_all('a', attrs={'class': 'tgme_widget_message_photo_wrap'}))
            matches = re.findall(self.cleaner_for_photo, text)
            return matches if matches else False
        except Exception as e:
            print(f"An error occurred while getting photos: {e}")
            return False
        
    def get_channel_name(self):
        """
        Извлекает название канала из HTML.
        Возвращает название канала или False в случае ошибки.
        """
        try:
            text = str(self.soup.find_all('div', attrs={'class': 'tgme_channel_info_header_title'})[0])
            clean_text = re.sub(self.cleaner, '', text)
            return clean_text
        except Exception as e:
            print(f"An error occurred while getting channel name: {e}")
            return False

# получение имени канала
async def get_channel_name(link: str):
    """
    Извлекает название канала по указанному URL.
    """
    html = await request(link)
    soup = BeautifulSoup(html, 'html.parser')
    page = Telegram_news(soup)
    name = page.get_channel_name()
    return name