import asyncio
import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


# Даты ЕГЭ для разных предметов (с точностью до секунд)
EXAM_DATES = {
    "История": datetime.datetime(2025, 5, 23, 10, 0, 0),
    "Литература": datetime.datetime(2025, 5, 23, 10, 0, 0),
    "Химия": datetime.datetime(2025, 5, 23, 10, 0, 0),
    "Математика": datetime.datetime(2025, 5, 27, 10, 0, 0),  
    "Русский язык": datetime.datetime(2025, 5, 30, 10, 0, 0),  
    "Физика": datetime.datetime(2025, 6, 2, 10, 0, 0),
    "Обществознание": datetime.datetime(2025, 6, 2, 10, 0, 0),  
    "Биология": datetime.datetime(2025, 6, 5, 10, 0, 0),
    "География": datetime.datetime(2025, 6, 5, 10, 0, 0),
    "Английский язык (писменная часть)": datetime.datetime(2025, 6, 5, 10, 0, 0),  
    "Английский язык (устная часть, 1 день)": datetime.datetime(2025, 6, 10, 10, 0, 0),
    "Информатика (1 день)": datetime.datetime(2025, 6, 10, 10, 0, 0),
    "Английский язык (устная часть, 2 день)": datetime.datetime(2025, 6, 10, 10, 0, 0),
    "Информатика (2 день)": datetime.datetime(2025, 6, 10, 10, 0, 0),
}

# Список пользователей и их выбранных предметов
user_exams = {}

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Функция для расчета оставшегося времени до экзамена
def time_until_exam(exam_datetime):
    now = datetime.datetime.now()
    delta = exam_datetime - now
    if delta.total_seconds() <= 0:
        return "Экзамен уже прошел!"
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days} дней {hours} часов {minutes} минут {seconds} секунд"


def create_subject_keyboard():
    buttons = [KeyboardButton(text=subject) for subject in EXAM_DATES.keys()]
    keyboard = ReplyKeyboardMarkup(keyboard=[[button] for button in buttons], resize_keyboard=True, one_time_keyboard=True)
    return keyboard


def create_main_keyboard():
    add_button = KeyboardButton(text="Добавить предмет")
    keyboard = ReplyKeyboardMarkup(keyboard=[[add_button]], resize_keyboard=True)
    return keyboard


@dp.message(F.text.lower() == "/start")
async def start(message: Message):
    user_id = message.from_user.id
    if user_id not in user_exams:
        user_exams[user_id] = []  
    await message.reply(
        "Привет! Выберите интересующие вас предметы:",
        reply_markup=create_subject_keyboard()
    )


@dp.message(F.text.in_(EXAM_DATES.keys()))
async def select_subject(message: Message):
    user_id = message.from_user.id
    subject = message.text
    if subject not in user_exams[user_id]:
        user_exams[user_id].append(subject)
        await message.reply(f"Вы добавили предмет: {subject}.", reply_markup=create_main_keyboard())
    else:
        await message.reply(f"Предмет {subject} уже выбран.", reply_markup=create_main_keyboard())
    await show_selected_exams(message)


@dp.message(F.text.lower() == "добавить предмет")
async def add_subject(message: Message):
    await message.reply("Выберите предмет из списка:", reply_markup=create_subject_keyboard())


async def show_selected_exams(message: Message):
    user_id = message.from_user.id
    if not user_exams[user_id]:
        await message.reply("Вы пока не выбрали ни одного предмета.", reply_markup=create_main_keyboard())
    else:
        response = "Выбранные предметы:\n"
        for subject in user_exams[user_id]:
            time_left = time_until_exam(EXAM_DATES[subject])
            response += f"- {subject}: {time_left}\n"
        await message.reply(response, reply_markup=create_main_keyboard())


async def send_notification():
    for user_id, subjects in user_exams.items():
        if not subjects:
            continue
        message_text = "Уведомления о ваших экзаменах:\n"
        for subject in subjects:
            time_left = time_until_exam(EXAM_DATES[subject])
            message_text += f"- {subject}: {time_left}\n"
        try:
            await bot.send_message(chat_id=user_id, text=message_text)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")


async def scheduler():
    while True:
        current_time = datetime.datetime.now().time()
        if current_time.hour == 8 and current_time.minute == 0:  # Уведомление в 9:00
            await send_notification()
        await asyncio.sleep(60)  # Проверяем каждую минуту


async def main():
    asyncio.create_task(scheduler())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())