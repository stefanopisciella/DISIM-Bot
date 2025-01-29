import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from model.MenuItem import MenuItem as MenuItemModel

from model.Tag import Tag as TagModel
from model.User import User as UserModel
from model.UninterestedIn import UninterestedIn as UninterestedInModel
from model.UninterestedWebsite import UninterestedWebsite as UninterestedWebsiteModel

from website_scrapers.DISIMwebsiteScraper import DISIMwebsiteScraper

import configuration_file as conf


class PullBot:
    def __init__(self, token):
        self.application = Application.builder().token(token).build()

        self.menu_manager = MenuManager()
        self.user_preferences_manager = UserPreferencesManager()

        # START bot handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("personalizza", self.user_preferences_manager.personalizza_command_handler))
        self.application.add_handler(CommandHandler("link", self.menu_manager.link_command_handler))

        self.application.add_handler(CallbackQueryHandler(self.menu_manager.button_callback, pattern="^MenuManager:"))  # CallbackQueryHandler of MenuManager
        self.application.add_handler(CallbackQueryHandler(self.user_preferences_manager.button_callback, pattern="^UserPreferencesManager:"))  # CallbackQueryHandler of UserPreferencesManager
        self.application.add_handler(CallbackQueryHandler(self.button_callback))  # CallbackQueryHandler of PullBot
        # END bot handlers


    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton("🔗 Link utili", callback_data="MenuManager"),
                InlineKeyboardButton("🏷 I tuoi tag", callback_data="UserPreferencesManager")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Benvenuto in DISIM Bot:", reply_markup=reply_markup)  # send a message


    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query  # extracts the button click event from the user's interaction
        await query.answer()  # acknowledges the button click to Telegram

        data = query.data  # retrieves the value associated with the clicked button.

        if data == "MenuManager":
            await self.menu_manager.start(update, context)
        elif data == "UserPreferencesManager":
            await self.user_preferences_manager.start(update, context)


    async def run(self):
        """Run the bot."""
        print("Bot is running...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

        await self.menu_manager.scrape_menu_items()


class UserPreferencesManager:
    # START constant strings
    RECIVE_COMUNICATIONS_FROM_THE_SITE = "Ricevi comunicazioni dal sito"
    NOT_RECIVE_COMUNICATIONS_FROM_THE_SITE = "Non ricevere comunicazioni dal sito"
    SELECT_THE_WEBSITE = "Seleziona il sito per gestire i tuoi tag di interesse:"
    # END constant strings

    # START emoticons
    NOTIFICATIONS_ICON = "🔔"
    NO_NOTIFICATIONS_ICON = "🔕"
    # END emoticons

    # START singleton design pattern
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.user_selections = {}
        self.show_user_preferences_saved_in_db = {}

        self.first_level_options = ["DISIM", "ADSU"]

        # START instantiate model classes
        self.tag_model = TagModel()
        self.user_model = UserModel()
        self.uninterested_website_model = UninterestedWebsiteModel()
        self.uninterested_in_model = UninterestedInModel()
        # END instantiate model classes
    # END singleton design pattern


    def get_checkbox_options(self):
        second_level_options = {}
        for website in self.first_level_options:  # associate a dictionary to each website
            if website not in second_level_options:
                second_level_options[website] = {}  # initialize nested dictionary

            for tag in self.tag_model.get_tag_names_by_website(website):
                second_level_options[website][tag] = True  # by default a tag is considered of interest to the user

            second_level_options[website]["uninterested_website"] = False  # by default a website is considered of
            # interest to the user

        return second_level_options

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message with first-level buttons """
        chat_id = update.effective_chat.id

        self.user_selections[chat_id] = self.get_checkbox_options()
        self.show_user_preferences_saved_in_db[
            chat_id] = True  # by default the user should be shown his preferences saved in the DB so that he can be
        # shown the preferences he selected in the previous time

        await self.send_first_level_buttons(update, context)
        self.user_model.insert(chat_id)  # save user chat_id in DB

    async def send_first_level_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send the first-level buttons """
        buttons = []

        # START create first-level buttons
        for website in self.first_level_options:  # create a button for each website
            buttons.append([InlineKeyboardButton(website, callback_data=f"UserPreferencesManager:first:{website}")])

        buttons.append([InlineKeyboardButton("Salva 💾", callback_data="UserPreferencesManager:save_all")])  # create "save" button to save
        # all user preferences

        reply_markup = InlineKeyboardMarkup(buttons)
        # END create first-level buttons

        if update.callback_query:
            # user interacted by selecting one of the inline buttons ==> to respond appropriately, the Bot edits the
            # existing message (to update its content or keyboard) rather than sending a new message.
            await update.callback_query.edit_message_text(
                self.SELECT_THE_WEBSITE, reply_markup=reply_markup
            )
        else:
            # here is handled the case in which the user interacts with user by sending it a message ==> the Bot sends
            # a new message
            await update.message.reply_text(
                self.SELECT_THE_WEBSITE, reply_markup=reply_markup
            )

    async def send_second_level_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int,
                                        website: str) -> None:
        """Send the second-level (checkbox) buttons """
        buttons = []

        if self.user_selections[chat_id][website]["uninterested_website"]:
            # user uninterested in the current website

            # START creation of "don't receive communications from the current website" button
            button_text = f"{self.NOT_RECIVE_COMUNICATIONS_FROM_THE_SITE} {website} {self.NO_NOTIFICATIONS_ICON}"
            buttons.append([InlineKeyboardButton(button_text, callback_data=f"UserPreferencesManager:second:{website}:uninterested_website")])
            # END creation of "don't receive communications from the current website" button
        else:
            # user interested in the current website

            # START creation of "receive communications from the current website" button
            button_text = f"{self.RECIVE_COMUNICATIONS_FROM_THE_SITE} {website} {self.NOTIFICATIONS_ICON}"
            buttons.append([InlineKeyboardButton(button_text, callback_data=f"UserPreferencesManager:second:{website}:uninterested_website")])
            # START creation of "receive communications from the current website" button

            # START creation of all buttons relative to tags
            for option, selected in self.user_selections[chat_id][website].items():
                if option != "uninterested_website":
                    # the current option is a tag

                    button_text = f"{'✅' if selected else '❌'} {option}"
                    buttons.append([InlineKeyboardButton(button_text, callback_data=f"UserPreferencesManager:second:{website}:{option}")])
            # END creation of all buttons relative to tags

        buttons.append([InlineKeyboardButton("<< Indietro", callback_data="UserPreferencesManager:back")])  # add "turn back" button

        reply_markup = InlineKeyboardMarkup(buttons)
        await update.callback_query.edit_message_text(
            f"Seleziona i tuoi tag di interesse per il sito {website}:", reply_markup=reply_markup
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button selection """
        query = update.callback_query  # extracts the button click event from the user's interaction
        await query.answer()  # acknowledges the button click to Telegram

        data = query.data  # retrieves the value associated with the clicked button.

        chat_id = query.message.chat.id
        user_id = self.user_model.get_user_id_by_his_chat_id(chat_id)

        if data.startswith("UserPreferencesManager:first:"):
            website = data.split(":")[2]

            # START get user preferences from DB
            if user_id is not None and self.show_user_preferences_saved_in_db[chat_id] is True:  # if the DB does
                # not have updated user preferences, the user will be shown the updated ones that are present in RAM

                # current user already registered

                # START get user website preferences
                user_uninterested_websites = self.uninterested_website_model.get_user_uninterested_websites(user_id)
                for user_uninterested_website in user_uninterested_websites:
                    self.user_selections[chat_id][user_uninterested_website]["uninterested_website"] = True
                # END get user website preferences

                # START get user uninterested tags
                user_uninterested_tags = self.uninterested_in_model.get_user_uninterested_tags(user_id)
                for user_uninterested_tag in user_uninterested_tags:
                    name_of_user_uninterested_tag = user_uninterested_tag.get_name()
                    website_of_user_uninterested_tag = user_uninterested_tag.get_website()

                    self.user_selections[chat_id][website_of_user_uninterested_tag][
                        name_of_user_uninterested_tag] = False
                # END get user uninterested tags

            # END get user preferences from DB

            await self.send_second_level_buttons(update, context, chat_id, website)

        elif data.startswith("UserPreferencesManager:second:"):
            website = data.split(":")[2]
            option = data.split(":")[3]

            self.user_selections[chat_id][website][option] = not self.user_selections[chat_id][website][
                option]  # toggle the flag associated with the selected button

            self.show_user_preferences_saved_in_db[chat_id] = False  # a new user preference has been added ==> until it
            # is also saved in the database, do not show the user preferences stored in DB, as they may not be
            # up-to-date.

            await self.send_second_level_buttons(update, context, chat_id, website)

        elif data == "UserPreferencesManager:save_all":
            # START send to the user a summary of the options he selected
            summary_arr = []
            for website, options in self.user_selections[chat_id].items():
                if self.user_selections[chat_id][website]["uninterested_website"]:
                    # user uninterested in the current website
                    summary_arr.append(
                        f"{self.NOT_RECIVE_COMUNICATIONS_FROM_THE_SITE} {website} {self.NO_NOTIFICATIONS_ICON}")
                else:
                    # user interested in the current website

                    # START add user tags of interest to the summary
                    tags_of_interest = []
                    for option, selected in options.items():
                        if option != "uninterested_website" and selected:
                            tags_of_interest.append(option)

                    summary_arr.append(f"{website}: {', '.join(tags_of_interest) or 'nessun tag selezionato'}")
                    # START add user tags of interest to the summary

            await query.edit_message_text(
                f"Riepilogo delle tue selezioni:\n\u2022 " + "\n\u2022 ".join(summary_arr)
            )
            # END send to the user a summary of the options he selected

            # START save user preferences in DB
            self.uninterested_in_model.remove_uninterested_tags_by_user_id(user_id)
            self.uninterested_website_model.remove_uninterested_websites_by_user_id(user_id)

            for website, options in self.user_selections[chat_id].items():
                for option, selected in options.items():
                    if option == "uninterested_website":
                        # the current option is not a tag name
                        if selected:
                            # user uninterested in the current website
                            self.uninterested_website_model.insert(user_id, website)
                    else:
                        # the current option is a tag name
                        if not selected:
                            # user uninterested in the current tag

                            tag_id = self.tag_model.get_tag_id_by_name_and_website(option, website)
                            self.uninterested_in_model.insert(user_id, tag_id)

            self.show_user_preferences_saved_in_db[chat_id] = True  # all user preferences saved in DB are updated ==>
            # this flag can be toggled

            # END save user preferences in DB

        elif data == "UserPreferencesManager:back":
            # user has selected the "turn back" button
            await self.send_first_level_buttons(update, context)

    async def personalizza_command_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Manage the /personalizza command """
        chat_id = update.effective_chat.id

        self.user_selections[chat_id] = self.get_checkbox_options()
        self.show_user_preferences_saved_in_db[
            chat_id] = True  # by default the user should be shown his preferences saved in the DB so that he can be
        # shown the preferences he selected in the previous time

        await self.send_first_level_buttons(update, context)


class MenuManager:
    # START singleton design pattern
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.menu_item_model = MenuItemModel()
    # END singleton design pattern

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_first_level_menu(update, context)

    async def send_first_level_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        first_level_menu_items = self.menu_item_model.get_all_first_level_menu_items()

        buttons = []
        for first_level_menu_item in first_level_menu_items:
            first_level_menu_item_name = first_level_menu_item.get_name()
            first_level_menu_item_id = first_level_menu_item.get_menu_item_id()

            buttons.append([InlineKeyboardButton(first_level_menu_item_name, callback_data=f'MenuManager:{first_level_menu_item_name}:{first_level_menu_item_id}')])

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

        back_button = [InlineKeyboardButton("<< Indietro", callback_data="MenuManager:back")]
        buttons.append(back_button)

        reply_markup = InlineKeyboardMarkup(buttons)
        await update.callback_query.edit_message_text(selected_first_level_menu_item_name, reply_markup=reply_markup)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query  # extracts the button click event from the user's interaction
        await query.answer()  # acknowledges the button click to Telegram

        data = query.data  # retrieves the value associated with the clicked button.

        if data == "MenuManager:back":
            await self.send_first_level_menu(update, context)
        else:
            selected_first_level_menu_item_name = data.split(":")[1]
            selected_first_level_menu_item_id = data.split(":")[2]

            await self.send_second_level_menu(update, context, selected_first_level_menu_item_id, selected_first_level_menu_item_name)

    async def link_command_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self.send_first_level_menu(update, context)

    @staticmethod
    async def scrape_menu_items():
        # scrape the menu items from the DISIM website every 24 yours
        while True:
            print("Executing scraping of menu items")
            disim_website_scraper = DISIMwebsiteScraper()
            disim_website_scraper.get_menu_items()

            await asyncio.sleep(86400)  # sleep for 24 hours


if __name__ == "__main__":
    bot = PullBot(conf.TELEGRAM_BOT_TOKEN)
    asyncio.run(bot.run())