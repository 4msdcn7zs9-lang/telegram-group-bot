import os
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
GROUP_ID = int(os.getenv("GROUP_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

passed_users = set()


class Survey(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()


@dp.message(Command("chatid"))
async def chatid(message: Message):
    await message.answer(f"ID этой группы:\n{message.chat.id}")


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    if message.from_user.id in passed_users:
        await message.answer("Вы уже проходили опрос.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да, всем сердцем ❤️", callback_data="q1_1")],
            [InlineKeyboardButton(text="Хочу верить ✨", callback_data="q1_2")]
        ]
    )

    await message.answer(
        "Вопрос 1.\nВеришь ли ты в настоящую любовь?",
        reply_markup=keyboard
    )

    await state.set_state(Survey.q1)


@dp.callback_query(Survey.q1)
async def question1(callback: CallbackQuery, state: FSMContext):
    answers = {
        "q1_1": "Да, всем сердцем ❤️",
        "q1_2": "Хочу верить ✨"
    }

    answer1 = answers.get(callback.data)
    await state.update_data(answer1=answer1)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Глубина и близость 🤍", callback_data="q2_1")],
            [InlineKeyboardButton(text="Страсть и вдохновение 🔥", callback_data="q2_2")]
        ]
    )

    await callback.message.edit_text(
        "Вопрос 2.\nЧто для тебя важнее в отношениях?",
        reply_markup=keyboard
    )

    await state.set_state(Survey.q2)
    await callback.answer()


@dp.callback_query(Survey.q2)
async def question2(callback: CallbackQuery, state: FSMContext):
    answers = {
        "q2_1": "Глубина и близость 🤍",
        "q2_2": "Страсть и вдохновение 🔥"
    }

    answer2 = answers.get(callback.data)
    await state.update_data(answer2=answer2)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да, я открыта 🌹", callback_data="q3_1")],
            [InlineKeyboardButton(text="Учусь этому 💫", callback_data="q3_2")]
        ]
    )

    await callback.message.edit_text(
        "Вопрос 3.\nГотова ли ты открываться новым чувствам?",
        reply_markup=keyboard
    )

    await state.set_state(Survey.q3)
    await callback.answer()


@dp.callback_query(Survey.q3)
async def question3(callback: CallbackQuery, state: FSMContext):
    answers = {
        "q3_1": "Да, я открыта 🌹",
        "q3_2": "Учусь этому 💫"
    }

    answer3 = answers.get(callback.data)
    data = await state.get_data()

    answer1 = data.get("answer1")
    answer2 = data.get("answer2")

    user = callback.from_user
    username = f"@{user.username}" if user.username else "нет username"

    report = (
        "🌹 Новая заявка в группу\n\n"
        f"Имя: {user.full_name}\n"
        f"Username: {username}\n"
        f"ID: {user.id}\n\n"
        f"Вопрос 1: Веришь ли ты в настоящую любовь?\n"
        f"Ответ: {answer1}\n\n"
        f"Вопрос 2: Что для тебя важнее в отношениях?\n"
        f"Ответ: {answer2}\n\n"
        f"Вопрос 3: Готова ли ты открываться новым чувствам?\n"
        f"Ответ: {answer3}"
    )

    await bot.send_message(OWNER_ID, report)

    invite = await bot.create_chat_invite_link(
        chat_id=GROUP_ID,
        name=f"invite_{user.id}",
        member_limit=1
    )

    await callback.message.edit_text(
        "🌹 Добро пожаловать в пространство любви и трансформации.\n\n"
        f"Твоя одноразовая ссылка для входа:\n{invite.invite_link}"
    )

    passed_users.add(user.id)

    await state.clear()
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
