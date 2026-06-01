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
            [InlineKeyboardButton(text="Да", callback_data="q1_1")],
            [InlineKeyboardButton(text="Конечно", callback_data="q1_2")]
        ]
    )

    await message.answer(
        "Вопрос 1.\nТы готова идти в глубину?",
        reply_markup=keyboard
    )

    await state.set_state(Survey.q1)


@dp.callback_query(Survey.q1)
async def question1(callback: CallbackQuery, state: FSMContext):
    answers = {
        "q1_1": "Да",
        "q1_2": "Конечно"
    }

    answer1 = answers.get(callback.data)
    await state.update_data(answer1=answer1)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="q2_1")],
            [InlineKeyboardButton(text="Придется", callback_data="q2_2")]
        ]
    )

    await callback.message.edit_text(
        "Вопрос 2.\nТы готова служить любви?",
        reply_markup=keyboard
    )

    await state.set_state(Survey.q2)
    await callback.answer()


@dp.callback_query(Survey.q2)
async def question2(callback: CallbackQuery, state: FSMContext):
    answers = {
        "q2_1": "Да",
        "q2_2": "Придется"
    }

    answer2 = answers.get(callback.data)
    data = await state.get_data()
    answer1 = data.get("answer1")

    user = callback.from_user
    username = f"@{user.username}" if user.username else "нет username"

    report = (
        "🌹 Новая заявка в группу\n\n"
        f"Имя: {user.full_name}\n"
        f"Username: {username}\n"
        f"ID: {user.id}\n\n"
        f"Вопрос 1: Ты готова идти в глубину?\n"
        f"Ответ: {answer1}\n\n"
        f"Вопрос 2: Ты готова служить любви?\n"
        f"Ответ: {answer2}"
    )

    await bot.send_message(OWNER_ID, report)

    invite = await bot.create_chat_invite_link(
        chat_id=GROUP_ID,
        name=f"invite_{user.id}",
        member_limit=1
    )

    await callback.message.edit_text(
        "Опрос пройден 🌹\n\n"
        f"Ваша одноразовая ссылка для входа в группу:\n{invite.invite_link}"
    )

    passed_users.add(user.id)
    await state.clear()
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
