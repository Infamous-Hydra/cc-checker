import logging
import random
import re

import aiohttp
import requests
import asyncio
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from bs4 import BeautifulSoup as bs

from db import db, mongo_client  # Importing the necessary database modules
from functions import *
from karma import *


@dp.message(Command("start"))
async def helpstr(message: types.Message):
    btn_owner = types.InlineKeyboardButton(text="Owner", url="https://t.me/O_oKarma")
    btn_commands = types.InlineKeyboardButton(text="Commands", callback_data="commands")
    btn_channel = types.InlineKeyboardButton(
        text="Channel", url="https://t.me/ProjectCodeX"
    )

    keyboard_markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [btn_owner, btn_commands],  # Top row
            [btn_channel],  # Bottom row
        ]
    )

    FIRST = message.from_user.first_name
    MSG = f"Hello {FIRST}."
    await message.answer_video(
        video=VIDEO_URL, caption=MSG, reply_markup=keyboard_markup
    )

    # Update or insert user information into MongoDB
    await db.users.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"user_id": message.from_user.id}},
        upsert=True,
    )


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    total_users = await db.users.count_documents({})
    await message.reply(f"Total users: {total_users}")


@dp.callback_query(lambda query: query.data == "commands")
async def process_commands(callback_query: types.CallbackQuery):
    btn_back = types.InlineKeyboardButton(text="Back", callback_data="back")

    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard=[[btn_back]])

    commands_info = """
/start
/gen
/stats
/bin
/info
/iban
/rand
"""

    await bot.edit_message_caption(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        caption=commands_info,
        reply_markup=keyboard_markup,
        parse_mode="HTML",
    )


@dp.callback_query(lambda query: query.data == "back")
async def process_back(callback_query: types.CallbackQuery):
    btn_owner = types.InlineKeyboardButton(text="Owner", url="https://t.me/O_oKarma")
    btn_commands = types.InlineKeyboardButton(text="Commands", callback_data="commands")
    btn_channel = types.InlineKeyboardButton(
        text="Channel", url="https://t.me/ProjectCodeX"
    )

    keyboard_markup = types.InlineKeyboardMarkup(
        inline_keyboard=[[btn_owner, btn_commands], [btn_channel]]
    )

    FIRST = callback_query.message.from_user.first_name
    MSG = f"Hello {FIRST}."

    await bot.edit_message_caption(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        caption=MSG,
        reply_markup=keyboard_markup,
        parse_mode="HTML",
    )


@dp.message(Command("info"))
async def info(message: types.Message):
    user_id = (
        message.reply_to_message.from_user.id
        if message.reply_to_message
        else message.from_user.id
    )
    is_bot = (
        message.reply_to_message.from_user.is_bot
        if message.reply_to_message
        else message.from_user.is_bot
    )
    username = (
        message.reply_to_message.from_user.username
        if message.reply_to_message
        else message.from_user.username
    )
    first = (
        message.reply_to_message.from_user.first_name
        if message.reply_to_message
        else message.from_user.first_name
    )

    await message.reply(
        f"""
═════════╕
<b>USER INFO</b>
<b>USER ID:</b> <code>{user_id}</code>
<b>USERNAME:</b> @{username}
<b>FIRSTNAME:</b> {first}
<b>BOT:</b> {is_bot}
╘═════════"""
    )


@dp.message(Command("bin"))
async def binio(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")  # Change to send_chat_action
    ID = message.from_user.id
    FIRST = message.from_user.first_name
    BIN = message.text[len("/bin ") :]

    if len(BIN) < 6:
        return await message.reply("Send bin. Ex: /bin number")

    r = requests.get(f"https://bins.ws/search?bins={BIN[:6]}").text
    soup = bs(r, features="html.parser")
    k = soup.find("div", {"class": "page"})

    if k:  # Ensure the element was found
        INFO = f"""
{ k.text[62:] }
SENDER: <a href="tg://user?id={ID}">{FIRST}</a>
"""
        await message.reply(INFO)
    else:
        await message.reply("No information found for this BIN.")


@dp.message(Command("gen"))
async def generate_card(message: types.Message):
    try:
        msg_text = message.text
        card_details = (
            msg_text.split()[1] if len(msg_text.split()) > 1 else "407544|xx|xx|xxx"
        )
        card_parts = card_details.split("|")

        cc = card_parts[0]
        mon = card_parts[1] if len(card_parts) > 1 else "xx"
        year = card_parts[2] if len(card_parts) > 2 else "xxxx"
        cvv = card_parts[3] if len(card_parts) > 3 else "xxx"
        amou = card_parts[4] if len(card_parts) > 4 else "10"

        cards = []
        for _ in range(int(amou)):
            bin_part = cc[:6]
            remaining_digits = 16 - len(bin_part)
            ccrem = "".join(random.choices("0123456789", k=remaining_digits))
            monthdigit = (
                str(random.randint(1, 12)).zfill(2) if mon in ["xx", "x"] else mon
            )
            yeardigit = (
                str(random.randint(2023, 2029)) if year in ["xxxx", "xx"] else year
            )
            cvvdigit = (
                str(random.randint(100, 9999))
                if cvv in ["x", "", "xx", "xxx"] and cc.startswith("3")
                else (
                    cvv
                    if cvv not in ["x", "", "xx", "xxx"]
                    else str(random.randint(100, 999))
                )
            )

            ccgen = f"{bin_part}{ccrem}"
            cards.append(f"{ccgen}|{monthdigit}|{yeardigit}|{cvvdigit}")

        card_response = "\n".join(cards)

        response = (
            f"<b>• 𝗖𝗖 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗢𝗥 𝄵</b>\n"
            f"• 𝗕𝗜𝗡 ⇾ <code>{bin_part}</code>\n"
            f"• 𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ <code>{amou}</code>\n\n"
            f"<code>{card_response}</code>\n"
            f"• 𝗚𝗘𝗡 𝗕𝗬 ‌: @{message.from_user.username}\n"
        )

        await bot.send_message(message.chat.id, response, parse_mode=ParseMode.HTML)

    except Exception as e:
        logging.error(e)
        await message.reply(
            f"Error: {str(e)}\nMake sure your input format is: /gen 407544|xx|xx|xxx"
        )


@dp.message(Command("iban"))
async def handle_random_iban(message: types.Message):
    if message.text.startswith(("/iban", "!iban", ".iban")):
        chat_id = message.chat.id
        await bot.send_chat_action(chat_id, "typing")

        async with aiohttp.ClientSession() as session:
            url = "https://random-data-api.com/api/bank/random_bank"

            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    iban = data.get("iban", "")
                    account_number = data.get("account_number", "")
                    bank_name = data.get("bank_name", "")
                    routing_number = data.get("routing_number", "")
                    swift_bic = data.get("swift_bic", "")

                    response_text = (
                        f"═════ 『 † 』════\n"
                        f"• 𝗜𝗯𝗮𝗻 ⇾ <code>{iban}</code>\n"
                        f"• 𝗔𝗰𝗰𝗼𝘂𝗻𝘁 𝗡𝗼 ⇾ <code>{account_number}</code>\n"
                        f"• 𝗕𝗮𝗻𝗸 ⇾ <code>{bank_name}</code>\n"
                        f"• 𝗥𝗼𝘂𝘁𝗶𝗻𝗴 𝗡𝗼 ⇾ <code>{routing_number}</code>\n"
                        f"• 𝗦𝘄𝗶𝗳𝘁/𝗕𝗜𝗖 ⇾ <code>{swift_bic}</code>\n"
                        f"═════ 『 † 』════"
                    )

                    await message.reply(response_text, parse_mode="HTML")
                else:
                    await message.reply("Failed to fetch IBAN information.")


@dp.message(Command("rand"))
async def send_random_user(message: types.Message):
    command_parts = message.text.split()
    nat = command_parts[1] if len(command_parts) > 1 else None
    random_user = await fetch_random_user(nat)
    user_info = random_user["results"][0]

    try:
        first = user_info["name"]["first"]
        last = user_info["name"]["last"]
        email = user_info["email"].replace("example.com", "yahoo.com").upper()
        street = (
            user_info["location"]["street"]["name"]
            if isinstance(user_info["location"]["street"], dict)
            else user_info["location"]["street"]
        )
        city = user_info["location"]["city"]
        state = user_info["location"]["state"]
        state_abbr = get_state_abbr(state)
        phone = re.sub(r"\D", "", user_info["phone"])
        cell = re.sub(r"\D", "", user_info["cell"])
        zip_code = user_info["location"]["postcode"]
        username = user_info["login"]["username"]
        password = user_info["login"]["password"]
        gender = user_info["gender"]
        ssn = user_info["id"]["value"] if user_info["id"]["value"] else "null"
        dob = user_info["dob"]["date"]
        salt = user_info["login"]["salt"]
        country = user_info["nat"]

        response = (
            f"<b>═════ 『 † 』════\n"
            f"•• ADDRESS GENERATOR\n"
            f"• FIRST NAME: <code>{first}</code>\n"
            f"• LAST NAME: <code>{last}</code>\n"
            f"• ADDRESS: <code>{street}</code>\n"
            f"• CITY: <code>{city}</code>\n"
            f"• STATE: <code>{state}</code>-<code>{state_abbr}</code>\n"
            f"• ZIP: <code>{zip_code}</code>\n"
            f"• COUNTRY: <code>{country}</code>\n"
            f"• SSN: <code>{ssn}</code>\n"
            f"• DOB: <code>{dob}</code>\n"
            f"• GENDER: <code>{gender}</code>\n"
            f"----------------------------------------\n"
            f"EMAIL: <code>{email}</code>\n"
            f"PHONE: <code>{phone}</code>\n"
            f"CELL: <code>{cell}</code>\n"
            f"USERNAME: <code>{username}</code>\n"
            f"PASSWORD: <code>{salt}{password}</code></b>"
        )

        await bot.send_message(message.chat.id, response, parse_mode=ParseMode.HTML)
    except KeyError as e:
        await bot.send_message(
            message.chat.id, f"Error parsing data: missing field {e}"
        )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    await mongo_client.admin.command("ismaster")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
