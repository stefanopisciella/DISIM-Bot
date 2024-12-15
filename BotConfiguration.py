from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
)

import configuration_file as conf


class BotConfiguration:
    def __init__(self, token):
        self.token = token
        self.user_selections = {}
        self.first_level_options = ["DISIM", "ADSU"]
        self.second_level_options = {
            "DISIM": {"Annunci agli Studenti": True, "Didattica": True},
            "ADSU": {"News": True, "In Evidenza": True},
        }


    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message with first-level buttons."""
        chat_id = update.effective_chat.id
        self.user_selections[chat_id] = self.second_level_options.copy()
        await self.send_first_level_buttons(update, context, chat_id)

    async def send_first_level_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
        """Send the first-level buttons."""
        buttons = [
            [InlineKeyboardButton(option, callback_data=f"first:{option}")]
            for option in self.first_level_options
        ]
        buttons.append([InlineKeyboardButton("Salva 💾", callback_data="save_all")])

        reply_markup = InlineKeyboardMarkup(buttons)
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "Seleziona il sito per gestire i tuoi tag di interesse:", reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "Seleziona il sito per gestire i tuoi tag di interesse:", reply_markup=reply_markup
            )

    async def send_second_level_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, group: str) -> None:
        """Send the second-level (checkbox) buttons."""
        buttons = [
            [InlineKeyboardButton(f"{'✅' if selected else '❌'} {option}", callback_data=f"second:{group}:{option}")]
            for option, selected in self.user_selections[chat_id][group].items()
        ]
        buttons.append([InlineKeyboardButton("<< Indietro", callback_data="back")])

        reply_markup = InlineKeyboardMarkup(buttons)
        await update.callback_query.edit_message_text(
            f"Seleziona i tuoi tag di interesse per il sito {group}:", reply_markup=reply_markup
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button clicks."""
        query = update.callback_query
        await query.answer()

        chat_id = query.message.chat.id
        data = query.data

        if data.startswith("first:"):
            group = data.split(":")[1]
            await self.send_second_level_buttons(update, context, chat_id, group)

        elif data.startswith("second:"):
            _, group, option = data.split(":")
            self.user_selections[chat_id][group][option] = not self.user_selections[chat_id][group][option]
            await self.send_second_level_buttons(update, context, chat_id, group)

        elif data == "save_all":
            result = []
            for group, options in self.user_selections[chat_id].items():
                selected_options = [option for option, selected in options.items() if selected]
                result.append(f"{group}: {', '.join(selected_options) or 'None'}")
            await query.edit_message_text(
                f"Hai salvato i seguenti tag di interesse:\n" + "\n".join(result)
            )

        elif data == "back":
            await self.send_first_level_buttons(update, context, chat_id)

    def run(self):
        """Start the bot."""
        application = ApplicationBuilder().token(self.token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.button_callback))

        application.run_polling()

if __name__ == "__main__":
    bot = BotConfiguration(conf.TELEGRAM_BOT_TOKEN)
    bot.run()
