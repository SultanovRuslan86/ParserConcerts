# Пробный сервис через телегамм-бота
import asyncio
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types

from dotenv import load_dotenv
import os


load_dotenv()


BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Создаем переменную для хранения состояния пользователя (уведомления включены или выключены)
user_states = {}


def parse_concert_info(concert_name):
    url = "https://ticketon.kz/concerts"
    response = requests.get(url)
    concert_info = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        concert_blocks = soup.find_all("div", class_="list-item block--bordered")

        for block in concert_blocks:
            title = block.find("span", class_="list-item__event").text.strip()
            if concert_name.lower() in title.lower():
                date = block.find("time").text.strip()
                location = block.find("a", class_="list-item__place").text.strip()
                concert_info.append(f"Название концерта: {title}\nДата концерта: {date}\nМесто проведения: {location}")

    return concert_info


async def check_concerts():
    while True:
        await asyncio.sleep(86400)  # проверка раз в сутки (86400 секунд) можно изменить

        for user_id, state in user_states.items():
            if state:
                concert_name = state.get('concert_name')
                concert_info = parse_concert_info(concert_name)

                if not concert_info:
                    message = "В ближайшее время данный концерт не планируется, мониторинг продолжается"
                else:
                    message = "\n\n".join(concert_info)

                await bot.send_message(chat_id=CHAT_ID, text=message)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Найти концерт"))
    keyboard.add(types.KeyboardButton("Получать уведомление"))

    await message.reply("Привет! Выберите действие:", reply_markup=keyboard)


@dp.message_handler()
async def process_message(message: types.Message):
    if message.text == "Найти концерт":
        await message.reply("Введите название концерта, чтобы найти информацию о событиях.")
    elif message.text == "Получать уведомление":
        user_id = message.from_user.id
        user_states[user_id] = {'concert_name': None}
        await message.reply("Уведомления включены. Введите название концерта для отслеживания.")
    else:
        concert_name = message.text
        concert_info = parse_concert_info(concert_name)

        if not concert_info:
            await message.reply("Концерт с таким названием не найден. Мы будем продолжать мониторинг и уведомлять Вас раз в сутки!")
        else:
            for info in concert_info:
                await message.reply(info)


@dp.message_handler()
async def handle_concert_request(message: types.Message):
    user_id = message.from_user.id
    user_state = user_states.get(user_id, {})
    concert_name = message.text

    if user_state.get('concert_name') is None:
        # Если у пользователя нет названия концерта, значит это запрос на поиск концерта
        concert_info = parse_concert_info(concert_name)
        if not concert_info:
            await message.reply("Концерт с таким названием не найден. Мы будем продолжать мониторинг.")
        else:
            for info in concert_info:
                await message.reply(info)
    else:
        # Если у пользователя уже есть название концерта в состоянии, значит это запрос на включение уведомлений
        user_state['concert_name'] = concert_name
        user_states[user_id] = user_state
        await check_concerts(user_id, concert_name)


async def main():
    # Создаем задачу для мониторинга концертов
    # asyncio.create_task(check_concerts())

    # Запускаем бота
    await asyncio.gather(dp.start_polling(dp),
    check_concerts()
                         )


if __name__ == '__main__':
    asyncio.run(main())












