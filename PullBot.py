import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from model.MenuItem import MenuItem as MenuItemModel

from website_scrapers.DISIMwebsiteScraper import DISIMwebsiteScraper

class PullBot:
    def __init__(self, token):
        self.application = Application.builder().token(token).build()

        self.menu_item_model = MenuItemModel()

        # Handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_first_level_menu(update, context)

    async def send_first_level_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        first_level_menu_items = self.menu_item_model.get_all_first_level_menu_items()

        buttons = []
        for first_level_menu_item in first_level_menu_items:
            first_level_menu_item_name = first_level_menu_item.get_name()
            first_level_menu_item_id = first_level_menu_item.get_menu_item_id()

            buttons.append([InlineKeyboardButton(first_level_menu_item_name, callback_data=f'{first_level_menu_item_name}:{first_level_menu_item_id}')])

        reply_markup = InlineKeyboardMarkup(buttons)
        if update.callback_query:
            # user interacted by selecting one of the inline buttons ==> to respond appropriately, the Bot edits the
            # existing message (to update its content or keyboard) rather than sending a new message.
            await update.callback_query.edit_message_text(
                "Seleziona una delle seguenti sezioni di Didattica", reply_markup=reply_markup
            )
        else:
            # here is handled the case in which the user interacts with user by sending it a message ==> the Bot sends
            # a new message
            await update.message.reply_text(
                "Seleziona una delle seguenti sezioni di Didattica", reply_markup=reply_markup
            )

    async def send_second_level_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, selected_first_level_menu_item_id, selected_first_level_menu_item_name):
        second_level_menu_items = self.menu_item_model.get_menu_items_by_parent_id(selected_first_level_menu_item_id)

        buttons = []
        for second_level_menu_item in second_level_menu_items:
            buttons.append([InlineKeyboardButton(second_level_menu_item.get_name(), url=second_level_menu_item.get_link())])

        back_button = [InlineKeyboardButton("<< Indietro", callback_data="back")]
        buttons.append(back_button)

        reply_markup = InlineKeyboardMarkup(buttons)
        await update.callback_query.edit_message_text(selected_first_level_menu_item_name, reply_markup=reply_markup)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query  # extracts the button click event from the user's interaction
        await query.answer()  # acknowledges the button click to Telegram

        data = query.data  # retrieves the value associated with the clicked button.

        if data == "back":
            await self.send_first_level_menu(update, context)
        else:
            selected_first_level_menu_item_name = data.split(":")[0]
            selected_first_level_menu_item_id = data.split(":")[1]

            await self.send_second_level_menu(update, context, selected_first_level_menu_item_id, selected_first_level_menu_item_name)

    @staticmethod
    async def scrape_menu_items():
        # scrape the menu items from the DISIM website every 24 yours
        while True:
            print("Executing scraping of menu items")
            disim_website_scraper = DISIMwebsiteScraper()
            disim_website_scraper.get_menu_items()

            await asyncio.sleep(86400)  # sleep for 24 hours

    async def run(self):
        """Run the bot."""
        print("Bot is running...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

        await self.scrape_menu_items()

if __name__ == "__main__":
    TOKEN = "7300897795:AAEaYIJRhV0YpitB8ZTkhinn7F0SB5GxTDw"
    bot = PullBot(TOKEN)
    asyncio.run(bot.run())