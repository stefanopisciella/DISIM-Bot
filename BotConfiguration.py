from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
)

from model.Tag import Tag as TagModel

import configuration_file as conf


class BotConfiguration:
    # START constant strings
    RECIVE_COMUNICATIONS_FROM_THE_SITE = "Ricevi comunicazioni dal sito"
    NOT_RECIVE_COMUNICATIONS_FROM_THE_SITE = "Non ricevere comunicazioni dal sito"
    SELECT_THE_WEBSITE = "Seleziona il sito per gestire i tuoi tag di interesse:"
    # END constant strings

    # START emoticons
    NOTIFICATIONS_ICON = "🔔"
    NO_NOTIFICATIONS_ICON = "🔕"

    # END emoticons

    def __init__(self, token):
        self.token = token
        self.user_selections = {}
        self.first_level_options = ["DISIM", "ADSU"]

    def get_checkbox_options(self):
        second_level_options = {}
        for website in self.first_level_options:
            if website not in second_level_options:
                second_level_options[website] = {}  # initialize nested dictionary

            for tag in TagModel.get_tag_names_by_website(website):
                second_level_options[website][tag] = True

            second_level_options[website]["uninterested_website"] = False

        return second_level_options

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message with first-level buttons."""
        chat_id = update.effective_chat.id
        self.user_selections[chat_id] = self.get_checkbox_options()
        await self.send_first_level_buttons(update, context, chat_id)

    async def send_first_level_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
        """Send the first-level buttons."""
        buttons = []
        for option in self.first_level_options:
            buttons.append([InlineKeyboardButton(option, callback_data=f"first:{option}")])

        buttons.append([InlineKeyboardButton("Salva 💾", callback_data="save_all")])

        reply_markup = InlineKeyboardMarkup(buttons)
        if update.callback_query:
            await update.callback_query.edit_message_text(
                self.SELECT_THE_WEBSITE, reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                self.SELECT_THE_WEBSITE, reply_markup=reply_markup
            )

    async def send_second_level_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int,
                                        group: str) -> None:
        """Send the second-level (checkbox) buttons."""
        buttons = []

        if self.user_selections[chat_id][group]["uninterested_website"]:
            # user uninterested in the current website

            button_text = f"{self.NOT_RECIVE_COMUNICATIONS_FROM_THE_SITE} {group} {self.NO_NOTIFICATIONS_ICON}"
            buttons.append([InlineKeyboardButton(button_text, callback_data=f"second:{group}:uninterested_website")])
        else:
            # user interested in the current website

            button_text = f"{self.RECIVE_COMUNICATIONS_FROM_THE_SITE} {group} {self.NOTIFICATIONS_ICON}"
            buttons.append([InlineKeyboardButton(button_text, callback_data=f"second:{group}:uninterested_website")])

            # START add all buttons relative to tags
            for option, selected in self.user_selections[chat_id][group].items():
                if option != "uninterested_website":
                    button_text = f"{'✅' if selected else '❌'} {option}"
                    buttons.append([InlineKeyboardButton(button_text, callback_data=f"second:{group}:{option}")])
            # END add all buttons relative to tags

        buttons.append([InlineKeyboardButton("<< Indietro", callback_data="back")])  # add "turn back" button

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
                if self.user_selections[chat_id][group]["uninterested_website"]:
                    # user uninterested in the current website
                    result.append(f"{self.NOT_RECIVE_COMUNICATIONS_FROM_THE_SITE} {group} {self.NO_NOTIFICATIONS_ICON}")
                else:
                    # user interested in the current website

                    selected_options = []
                    for option, selected in options.items():
                        if option != "uninterested_website" and selected:
                            selected_options.append(option)

                    result.append(f"{group}: {', '.join(selected_options) or 'nessun tag selezionato'}")
            await query.edit_message_text(
                f"Riepilogo delle tue selezioni:\n\u2022 " + "\n\u2022 ".join(result)
            )

        elif data == "back":
            # user has selected the "turn back" button
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
