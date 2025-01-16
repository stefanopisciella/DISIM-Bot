from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from model.MenuItem import MenuItem as MenuItemModel


class PullBot:
    def __init__(self, token):
        self.application = Application.builder().token(token).build()

        # Define menus
        self.sections = {
            "Section 1": [
                {"name": "Link 1-1", "url": "https://example.com/1-1"},
                {"name": "Link 1-2", "url": "https://example.com/1-2"}
            ],
            "Section 2": [
                {"name": "Link 2-1", "url": "https://example.com/2-1"},
                {"name": "Link 2-2", "url": "https://example.com/2-2"}
            ]
        }

        self.menu_item_model = MenuItemModel()

        # Handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_first_level_menu(update, context)


    async def send_first_level_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        first_level_menu_items = self.menu_item_model.get_all_first_level_menu_items()

        buttons = []
        for first_level_menu_item in first_level_menu_items:
            first_level_menu_item_name = first_level_menu_item.get_name()

            buttons.append([InlineKeyboardButton(first_level_menu_item_name, callback_data=first_level_menu_item_name)])

        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Didattica DISIM", reply_markup=reply_markup)


    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks."""
        query = update.callback_query
        await query.answer()

        if query.data in self.sections:  # First level menu clicked
            section_buttons = [
                [InlineKeyboardButton(item["name"], url=item["url"])] for item in self.sections[query.data]
            ]
            back_button = [InlineKeyboardButton("Back", callback_data="back")]
            reply_markup = InlineKeyboardMarkup(section_buttons + [back_button])
            await query.edit_message_text(f"Links in {query.data}:", reply_markup=reply_markup)

        elif query.data == "back":  # Back button clicked
            keyboard = [[InlineKeyboardButton(section, callback_data=section)] for section in self.sections.keys()]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Select a section:", reply_markup=reply_markup)

    def run(self):
        """Run the bot."""
        print("Bot is running...")
        self.application.run_polling()


if __name__ == "__main__":
    TOKEN = "7300897795:AAEaYIJRhV0YpitB8ZTkhinn7F0SB5GxTDw"
    bot = PullBot(TOKEN)
    bot.run()
