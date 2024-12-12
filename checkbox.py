from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
)

# Store user checkbox states
USER_SELECTIONS = {}

# Options for the first level buttons
FIRST_LEVEL_OPTIONS = ["DISIM", "ADSU"]

# Options for the second level (simulated checkboxes)
SECOND_LEVEL_OPTIONS = {
    "DISIM": {"Option A": False, "Option B": False},
    "ADSU": {"Option X": False, "Option Y": False},
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with first-level buttons."""
    chat_id = update.effective_chat.id
    USER_SELECTIONS[chat_id] = SECOND_LEVEL_OPTIONS.copy()
    await send_first_level_buttons(update, context, chat_id)


async def send_first_level_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    """Send the first-level buttons."""
    # The keyboard is a list of rows, where each row is a list of buttons (hence `[[...]]`).
    buttons = []
    for option in FIRST_LEVEL_OPTIONS:
        buttons.append([InlineKeyboardButton(option, callback_data=f"first:{option}")])
    buttons.append([InlineKeyboardButton("Save All", callback_data="save_all")])

    reply_markup = InlineKeyboardMarkup(buttons)
    if update.callback_query:
        # "update.callback_query" is not None ==> user interacted with a button ==> don't create a new message but just reuse the current one
        await update.callback_query.edit_message_text(
            "Choose a group or save your selections:", reply_markup=reply_markup
        )
    else:
        # "update.callback_query" is None ==> user hasn't interacted with a button but through a regular message (for instance the "start" message) ==> create a new message and append to it the inline keyboard
        await update.message.reply_text(
            "Choose a group or save your selections:", reply_markup=reply_markup
        )


async def send_second_level_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int,
                                    group: str) -> None:
    """Send the second-level (checkbox) buttons."""
    buttons = []
    for option, selected in USER_SELECTIONS[chat_id][group].items():
        status = "✅" if selected else "❌"
        buttons.append(
            [InlineKeyboardButton(f"{status} {option}", callback_data=f"second:{group}:{option}")]
        )
    buttons.append([InlineKeyboardButton("Back", callback_data="back")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await update.callback_query.edit_message_text(  # reuse the current message
        f"Choose options for {group}:", reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()  # this command is required to tell Telegram that this bot has received and processed the click of the button

    chat_id = query.message.chat.id
    data = query.data

    if data.startswith("first:"):
        # Navigate to the second-level buttons
        group = data.split(":")[1]  # it could be DISIM or ADSU
        await send_second_level_buttons(update, context, chat_id, group)

    elif data.startswith("second:"):
        # Toggle checkbox selection
        _, group, option = data.split(":")
        USER_SELECTIONS[chat_id][group][option] = not USER_SELECTIONS[chat_id][group][option]
        await send_second_level_buttons(update, context, chat_id,
                                        group)  # show again the same checkbox items with updated icons according to user choices

    elif data == "save_all":
        # show (without send a new message) the selected options for all groups
        result = []
        for group, options in USER_SELECTIONS[chat_id].items():
            selected_options = []
            for option, selected in options.items():
                if selected:
                    selected_options.append(option)
            result.append(f"{group}: {', '.join(selected_options) or 'None'}")
        await query.edit_message_text(
            f"You saved the following selections:\n" + "\n".join(result)
        )

    elif data == "back":
        # Return to the first-level buttons
        await send_first_level_buttons(update, context, chat_id)


def main():
    """Start the bot."""
    application = ApplicationBuilder().token("7300897795:AAEaYIJRhV0YpitB8ZTkhinn7F0SB5GxTDw").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()


if __name__ == "__main__":
    main()
