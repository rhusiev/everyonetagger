"""A database interface to yml for bot."""
from __future__ import annotations

import logging
import os

import yaml

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


class Database:
    """A database interface to yml.

    Args:
        path: path to the database file
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self._data = self._load()

    def _load(self) -> dict:
        """Load the database.

        Returns:
            database
        """
        if not os.path.exists(self.path):
            logging.info("Database not found, creating new one.")
            with open(self.path, "w") as f:
                f.write("")
            return {}
        with open(self.path, "r") as f:
            return yaml.safe_load(f)

    def _save(self) -> None:
        """Save the database."""
        with open(self.path, "w") as f:
            yaml.safe_dump(self._data, f)

    def add_chat(self, chat_id: int) -> None:
        """Add a chat to the database.

        Args:
            chat_id: id of the chat
        """
        if self.exists_chat(chat_id):
            return
        self._data[chat_id] = {"users": []}
        self._data[chat_id]["adminonly"] = False
        self._data[chat_id]["ignore"] = []
        self._save()

    def add_user(self, chat_id: int, user_id: int) -> None:
        """Add a user to the chat.

        Args:
            chat_id: id of the chat
            user_id: id of the user
        """
        if not self.exists_chat(chat_id):
            self.add_chat(chat_id)
        if self.exists_user(chat_id, user_id):
            return
        self._data[chat_id]["users"].append(user_id)
        self._save()

    def remove_user(self, chat_id: int, user_id: int) -> None:
        """Remove a user from the chat.

        Args:
            chat_id: id of the chat
            user_id: id of the user
        """
        if not self.exists_chat(chat_id):
            return
        if not self.exists_user(chat_id, user_id):
            return
        self._data[chat_id]["users"].remove(user_id)
        self._save()

    def get_users(self, chat_id: int) -> list:
        """Get users from the chat.

        Args:
            chat_id: id of the chat

        Returns:
            list of users
        """
        if not self.exists_chat(chat_id):
            return []
        return self._data[chat_id]["users"]

    def get_chats(self) -> list:
        """Get all chats.

        Returns:
            list of chats
        """
        return list(self._data.keys())

    def remove_chat(self, chat_id: int) -> None:
        """Remove a chat from the database.

        Args:
            chat_id: id of the chat
        """
        if not self.exists_chat(chat_id):
            return
        del self._data[chat_id]
        self._save()

    def exists_chat(self, chat_id: int) -> bool:
        """Check if a chat exists.

        Args:
            chat_id: id of the chat

        Returns:
            True if chat exists, False otherwise
        """
        return chat_id in self._data

    def exists_user(self, chat_id: int, user_id: int) -> bool:
        """Check if a user exists in the chat.

        Args:
            chat_id: id of the chat
            user_id: id of the user

        Returns:
            True if user exists, False otherwise
        """
        if not self.exists_chat(chat_id):
            return False
        return user_id in self._data[chat_id]["users"]

    def toggle_adminonly(self, chat_id: int) -> bool:
        """Toggle adminonly mode.

        Args:
            chat_id: id of the chat

        Returns:
            True if adminonly is now enabled, False otherwise
        """
        if not self.exists_chat(chat_id):
            self.add_chat(chat_id)
        adminonly = self._data[chat_id].get("adminonly", False)
        self._data[chat_id]["adminonly"] = not adminonly
        self._save()
        return not adminonly

    def get_adminonly(self, chat_id: int) -> bool:
        """Get adminonly mode.

        Args:
            chat_id: id of the chat

        Returns:
            True if adminonly is enabled, False otherwise
        """
        if not self.exists_chat(chat_id):
            return False
        return self._data[chat_id].get("adminonly", False)

    def toggle_ignoreme(self, chat_id: int, user_id: int) -> bool:
        """Toggle ignoreme mode.

        Args:
            chat_id: id of the chat
            user_id: id of the user

        Returns:
            True if ignoreme is now enabled, False otherwise
        """
        if not self.exists_chat(chat_id):
            self.add_chat(chat_id)
        if user_id not in self._data[chat_id]["ignore"]:
            self._data[chat_id]["ignore"].append(user_id)
            self._save()
            return True
        self._data[chat_id]["ignore"].remove(user_id)
        self._save()
        return False

    def get_ignoreme(self, chat_id: int, user_id: int) -> bool:
        """Get ignoreme mode.

        Args:
            chat_id: id of the chat
            user_id: id of the user

        Returns:
            True if ignoreme is enabled, False otherwise
        """
        if not self.exists_chat(chat_id):
            return False
        return user_id in self._data[chat_id]["ignore"]
