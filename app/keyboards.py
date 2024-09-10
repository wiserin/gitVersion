from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                            InlineKeyboardMarkup, InlineKeyboardButton)


main = [
    [KeyboardButton(text='Мои подписки'),
     KeyboardButton(text='Добавить канал')]
]
main_kb = ReplyKeyboardMarkup(keyboard=main,
                              resize_keyboard=True)

async def sub_generator(data):
    kb = []
    for i in data:
        kb.append([InlineKeyboardButton(text=i, callback_data=f'sub_{i}')])
    kb.append([InlineKeyboardButton(text='Отмена', callback_data=f'sub_cancel')])
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def media_info_kb(ids):
    kb = []
    if len(ids) == 1:
        kb.append([InlineKeyboardButton(text='1', callback_data=f'minfo_{str(ids[0])}')])

    elif len(ids) > 1 and len(ids) < 11:
        if len(ids) % 2 == 0:
            count = 0 
            for i in range(0, int(len(ids)/2)):
                lst = []
                for k in range(0, 2):
                    lst.append(InlineKeyboardButton(text=str(count+1), callback_data=f'minfo_{str(ids[count])}'))
                    count+=1
                    
                kb.append(lst)

        else:
            count = 0 
            for i in range(0, int((len(ids)-1)/2)):
                lst = []
                for k in range(0, 2):
                    lst.append(InlineKeyboardButton(text=str(count+1), callback_data=f'minfo_{str(ids[count])}'))
                    count+=1
                kb.append(lst)
            kb.append([InlineKeyboardButton(text=str(count+1), callback_data=f'minfo_{str(ids[-1])}')])
    
    elif len(ids) > 10 and len(ids) <=25:
        if len(ids) % 5 == 0:
            count = 0 
            for i in range(0, int(len(ids)/5)):
                lst = []
                for k in range(0, 5):
                    lst.append(InlineKeyboardButton(text=str(count+1), callback_data=f'minfo_{str(ids[count])}'))
                    count+=1
                    
                kb.append(lst)
        else:
            count = 0 
            for i in range(0, int((len(ids) - len(ids) % 5)/5)):
                lst = []
                for k in range(0, 5):
                    lst.append(InlineKeyboardButton(text=str(count+1), callback_data=f'minfo_{str(ids[count])}'))
                    count+=1
                    
                kb.append(lst)

            last = []
            for k in range(0, len(ids)%5):
                last.append(InlineKeyboardButton(text=str(count+1), callback_data=f'minfo_{str(ids[count])}'))
                count+=1
            kb.append(last)

    return InlineKeyboardMarkup(inline_keyboard=kb)

async def private_media_info_kb(id):
    kb = [[InlineKeyboardButton(text='Отписаться', callback_data=f'unsub_{str(id)}')]]
    return InlineKeyboardMarkup(inline_keyboard=kb)