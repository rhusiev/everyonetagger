"""EveryoneTagger bot to tag everyone in a group."""
import logging
import os

import telebot  # type: ignore
import yaml

from db import Database

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Load the database
CHATS_FILE = os.path.dirname(os.path.abspath("requirements.txt")) + "/data/chats.yml"
if not os.path.exists(CHATS_FILE):
    with open(CHATS_FILE, "w") as f:
        f.write(yaml.safe_dump({}))
        logging.info(f"No DB found, created empty DB at {CHATS_FILE}")
db = Database(path=CHATS_FILE)
logging.info(f"Loaded DB from {CHATS_FILE}")


class EveryoneTaggerBot:
    """The EveryoneTagger bot with its methods for handling messages."""

    def __init__(self, bot: telebot.TeleBot) -> None:
        self.bot = bot

    def reply(self, message: telebot.types.Message, text: str) -> None:
        """Reply to a message.

        Handle the exception if the message is deleted.

        Args:
            message: The message object.
            text: The text to reply with.
        """
        try:
            self.bot.reply_to(
                message,
                text=text,
            )
        except telebot.apihelper.ApiTelegramException:
            logging.error(
                f"Failed to reply to message {message.message_id} in \
{message.chat.id}({message.chat.title}). Message was probably deleted."
            )

    def handle_new_message(self, message: telebot.types.Message) -> None:
        """Handle a new message.

        Args:
            message: The message object.
        """
        if message.chat.type == "private":
            return
        chat_id = message.chat.id
        chat_title = message.chat.title
        member = message.from_user
        member_id = member.id
        member_name = member.full_name
        member_username = member.username
        if member_username is not None:
            member_name += f" (@{member_username})"
        else:
            member_name = f'<a href="tg://user?id={member_id}">{member_name}</a>'
        if not db.exists_chat(chat_id):
            db.add_chat(chat_id)
            logging.info(
                f"First message in {chat_id}({chat_title}), creating members set."
            )
        if not db.exists_user(chat_id, member_id):
            db.add_user(chat_id, member_id)
            logging.info(
                f"First message from '{member_name}'. \
Added to {chat_id}({chat_title}) members set."
            )

    def start_command(self, message: telebot.types.Message) -> None:
        """Send a message when the command /start is issued.

        Args:
            message: The message object.
        """
        self.handle_new_message(message)
        if message.chat.type == "private":
            self.reply(
                message,
                text="""Hi! Add me to a group and I'll be able to tag everyone in it

Telegram does not allow bots to just see all the members of a chat, but I'll check \
the messages and update my group members knowledge as I see them

/help for more info""",
            )
            return
        self.reply(
            message,
            text="""Hi! I'll tag everyone in this group

Telegram does not allow bots to just see all the members of a chat, but I'll check the \
messages and update my group members knowledge as I see them

/help for more info""",
        )

    def all_command(self, message: telebot.types.Message) -> None:
        """Tag everyone in the group.

        Args:
            message: The message object.
        """
        logging.info(
            f"Received /all command from {message.from_user.full_name} in \
{message.chat.id}({message.chat.title})."
        )
        self.handle_new_message(message)
        if message.chat.type == "private":
            return
        # If adminonly is set, only admins can use the command
        if db.get_adminonly(message.chat.id) and self.bot.get_chat_member(
            message.chat.id, message.from_user.id
        ).status not in ("administrator", "creator"):
            self.reply(
                message,
                text="Only admins can use this command",
            )
            return
        chat_id = message.chat.id
        chat_title = message.chat.title
        if not db.exists_chat(chat_id) or len(db.get_users(chat_id)) == 0:
            self.reply(
                message,
                text=f"""No members found for '{chat_title}'

Send a message to this group to add yourself to the members list
/help for more info""",
            )
            return
        members = db.get_users(chat_id)
        members_str = ""
        for member_id in members:
            if db.get_ignoreme(chat_id, member_id):
                continue
            try:
                member = self.bot.get_chat_member(chat_id, member_id)
            except telebot.apihelper.ApiTelegramException:
                logging.error(
                    f"Failed to get member {member_id} in {chat_id}({chat_title})"
                )
                continue
            member_username = member.user.username
            if member_username is not None:
                member_name = f"@{member_username}"
            else:
                member_name = member.user.full_name
                member_name = f'<a href="tg://user?id={member_id}">{member_name}</a>'
            members_str += f"{member_name}\n"
        self.reply(
            message,
            text=f"Tagging everyone:\n\n{members_str}",
            parse_mode="HTML",
        )

    def new_chat_members(self, message: telebot.types.Message) -> None:
        """Handle new chat members.

        Args:
            message: The message object.
        """
        logging.info(
            f"Received new chat members in {message.chat.id}({message.chat.title})."
        )
        self.handle_new_message(message)
        if message.chat.type == "private":
            return
        chat_id = message.chat.id
        chat_title = message.chat.title
        new_members = message.new_chat_members
        new_members_str = ""
        for member in new_members:
            member_id = member.id
            member_name = member.full_name
            member_username = member.username
            if member_username is not None:
                member_name += f" (@{member_username})"
            else:
                member_name = f'<a href="tg://user?id={member_id}">{member_name}</a>'
            if not db.exists_user(chat_id, member_id):
                db.add_user(chat_id, member_id)
                logging.info(
                    f"New member '{member_name}' in {chat_id}({chat_title}). \
Added to members set."
                )
            new_members_str += f"{member_name}\n"

    def left_chat_member(self, message: telebot.types.Message) -> None:
        """Handle left chat member.

        Args:
            message: The message object.
        """
        logging.info(
            f"Received left chat member in {message.chat.id}({message.chat.title})."
        )
        self.handle_new_message(message)
        if message.chat.type == "private":
            return
        chat_id = message.chat.id
        chat_title = message.chat.title
        member = message.left_chat_member
        member_id = member.id
        member_name = member.full_name
        member_username = member.username
        if member_username is not None:
            member_name += f" (@{member_username})"
        else:
            member_name = f'<a href="tg://user?id={member_id}">{member_name}</a>'
        if db.exists_user(chat_id, member_id):
            db.remove_user(chat_id, member_id)
            logging.info(
                f"Member '{member_name}' left {chat_id}({chat_title}). \
Removed from members set."
            )

    def help_command(self, message: telebot.types.Message) -> None:
        """Send a message when the command /help is issued.

        Args:
            message: The message object.
        """
        self.handle_new_message(message)
        if message.chat.type == "private":
            text = "Hi! Add me to a group and I'll be able to tag everyone in it\n\n"
        else:
            text = "Hi! I'm a bot that can tag everyone in a group\n\n"
        text += """/all - to tag everyone in this group
/adminonly - toggle tagging only when admins asks
/ignoreme - toggle tagging yourself

Telegram does not allow bots to just see all the members of a chat, but I'll check \
the messages and update my group members knowledge as I see them

Source code: <a href="https://gitlab.com/57d/everyonetagger">GitLab</a>
"""
        self.reply(
            message,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

    def adminonly_command(self, message: telebot.types.Message) -> None:
        """Toggle adminonly mode.

        Args:
            message: The message object.
        """
        logging.info(
            f"Received /adminonly command from {message.from_user.full_name} in \
{message.chat.id}({message.chat.title})."
        )
        self.handle_new_message(message)
        if message.chat.type == "private":
            return
        chat_id = message.chat.id
        chat_title = message.chat.title
        state = "enabled" if db.toggle_adminonly(chat_id) else "disabled"
        logging.info(f"Adminonly mode {state} in {chat_id}({chat_title}).")
        self.reply(
            message,
            text=f"Adminonly mode is now {state}",
        )

    def ignoreme_command(self, message: telebot.types.Message) -> None:
        """Toggle ignoreme mode.

        Args:
            message: The message object.
        """
        logging.info(
            f"Received /ignoreme command from {message.from_user.full_name} in \
{message.chat.id}({message.chat.title})."
        )
        self.handle_new_message(message)
        if message.chat.type == "private":
            return
        chat_id = message.chat.id
        chat_title = message.chat.title
        state = (
            "enabled"
            if db.toggle_ignoreme(chat_id, message.from_user.id)
            else "disabled"
        )
        logging.info(
            f"Ignoreme mode {state} for {message.from_user.full_name} in \
{chat_id}({chat_title})."
        )
        self.reply(
            message,
            text=f"Ignoreme mode is now {state} for you",
        )
