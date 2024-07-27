"""Run bot.py."""
import logging
import os

import telebot  # type: ignore

from bot import EveryoneTaggerBot

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    logging.error("TOKEN environment variable not set.")
    raise ValueError("TOKEN environment variable not set.")
logging.info("Loaded TOKEN from environment variable.")

bot = telebot.TeleBot(TOKEN)

everyone_tagger_bot = EveryoneTaggerBot(bot)

logging.info("Created bot.")


class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    """Class will check whether the user is admin or creator in group or not."""

    key = "is_chat_admin"

    @staticmethod
    def check(message: telebot.types.Message) -> bool:
        """Check if the user is admin or creator in group or not.

        Args:
            message: The message object.

        Returns:
            True if the user is admin or creator in group, False otherwise.
        """
        return bot.get_chat_member(message.chat.id, message.from_user.id).status in [
            "administrator",
            "creator",
        ]


bot.add_custom_filter(IsAdmin())


@bot.message_handler(commands=["start"])
def start_command(message: telebot.types.Message) -> None:
    """Send a message when the command /start is issued.

    Args:
        message: The message object.
    """
    everyone_tagger_bot.start_command(message)


@bot.message_handler(commands=["all"])
def all_command(message: telebot.types.Message) -> None:
    """Send a message when the command /all is issued.

    Args:
        message: The message object.
    """
    everyone_tagger_bot.all_command(message)


@bot.message_handler(content_types=["new_chat_members"])
def new_chat_members(message: telebot.types.Message) -> None:
    """Add a new member to the database when they join.

    Args:
        message: The message object.
    """
    everyone_tagger_bot.new_chat_members(message)


@bot.message_handler(content_types=["left_chat_member"])
def left_chat_member(message: telebot.types.Message) -> None:
    """Remove a member from the database when they leave.

    Args:
        message: The message object.
    """
    everyone_tagger_bot.left_chat_member(message)


@bot.message_handler(commands=["help"])
def help_command(message: telebot.types.Message) -> None:
    """Send a message when the command /help is issued.

    Args:
        message: The message object.
    """
    everyone_tagger_bot.help_command(message)


@bot.message_handler(commands=["adminonly"], is_chat_admin=True)
def adminonly_command(message: telebot.types.Message) -> None:
    """Send a message when the command /adminonly is issued.

    Args:
        message: The message object.
    """
    everyone_tagger_bot.adminonly_command(message)


@bot.message_handler(commands=["adminonly"], is_chat_admin=False)
def adminonly_command_not_admin(message: telebot.types.Message) -> None:
    """Send a message when the command /adminonly is issued by a non-admin.

    Args:
        message: The message object.
    """
    bot.reply_to(message, "Only admins can use this command.")


@bot.message_handler(commands=["ignoreme"])
def ignoreme_command(message: telebot.types.Message) -> None:
    """Send a message when the command /ignoreme is issued.

    Args:
        message: The message object.
    """
    everyone_tagger_bot.ignoreme_command(message)


@bot.message_handler(func=lambda _: True)
def handle_new_message(message: telebot.types.Message) -> None:
    """Handle a new message.

    Args:
        message: The message object.
    """
    everyone_tagger_bot.handle_new_message(message)


logging.info("Registered handlers.")
logging.info("Starting bot.")

bot.infinity_polling()
