import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError

import configuration_file as conf


class BroadcastBot:
    # START singleton design pattern
    _instance = None

    def __new__(cls, token):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._instance.token = token

            # START set logging
            logging.basicConfig(
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=logging.INFO
            )
            cls._instance.logger = logging.getLogger(__name__)
            # END set logging

        return cls._instance
    # END singleton design pattern






    async def send_message(self, bot, user_id, message_text):
        try:
            await bot.send_message(chat_id=user_id, text=message_text)
            self.logger.info(f"Message sent to user {user_id}")
        except TelegramError as e:
            self.logger.error(f"Failed to send message to user {user_id}: {e}")


    async def send_messages(self, user_ids, message_text):
        bot = Bot(token=self.token)
        tasks = [self.send_message(bot, user_id, message_text) for user_id in user_ids]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    # List of user IDs to send the message to
    USER_IDS = [53428135]  # Replace with actual user IDs

    # The message you want to broadcast
    MESSAGE_TEXT = "Hello4321! This is a broadcast message from your bot."

    send_filtered_announcement = BroadcastBot(conf.TELEGRAM_BOT_TOKEN)

    # Run the async function
    asyncio.run(send_filtered_announcement.send_messages(user_ids=USER_IDS, message_text=MESSAGE_TEXT))
