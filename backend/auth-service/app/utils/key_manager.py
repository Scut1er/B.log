import os
import re
import subprocess
from typing import Optional


class KeyManager:
    KEYS_FILE = ".env.keys"

    def __init__(self):
        self.keys = self._load_keys()

    def _load_keys(self):
        """Загружает ключи из KEYS_FILE"""
        keys = {}
        if os.path.exists(self.KEYS_FILE):
            with open(self.KEYS_FILE, "r") as f:
                content = f.read()
            # Учитываем многострочные ключи
            pattern = re.compile(r'(\w+)=(".*?")', re.DOTALL)
            keys = {key: value.strip('"') for key, value in pattern.findall(content)}
        return keys

    def get_key(self, key_name: str) -> Optional[str]:
        """Возвращает ключ по имени"""
        return self.keys.get(key_name)

    def get_access_public_keys(self):
        """Возвращает текущий + предыдущий публичный ключ для ACCESS-токена"""
        return self.get_key("ACCESS_PUBLIC_KEY"), self.get_key("PREVIOUS_ACCESS_PUBLIC_KEY")

    def get_access_private_key(self):
        """Возвращает приватный ключ для ACCESS-токена"""
        return self.get_key("ACCESS_PRIVATE_KEY")

    def get_refresh_public_keys(self):
        """Возвращает текущий + предыдущий публичный ключ для REFRESH-токена"""
        return self.get_key("REFRESH_PUBLIC_KEY"), self.get_key("PREVIOUS_REFRESH_PUBLIC_KEY")

    def get_refresh_private_key(self):
        """Возвращает приватный ключ для REFRESH-токена"""
        return self.get_key("REFRESH_PRIVATE_KEY")

    def rotate_keys(self):
        """Ротация ключей: ACCESS и REFRESH"""
        existing_keys = self.keys

        # Сохраняем предыдущие публичные ключи
        old_access_public = existing_keys.get("ACCESS_PUBLIC_KEY", "")
        old_refresh_public = existing_keys.get("REFRESH_PUBLIC_KEY", "")

        # Генерируем новые ключи
        new_access_private, new_access_public = self.generate_es256_keys()
        new_refresh_private, new_refresh_public = self.generate_es256_keys()

        # Обновляем файл .env.keys
        with open(self.KEYS_FILE, "w") as f:
            f.write(
                f'ACCESS_PRIVATE_KEY="{new_access_private}"\n'
                f'ACCESS_PUBLIC_KEY="{new_access_public}"\n'
                f'PREVIOUS_ACCESS_PUBLIC_KEY="{old_access_public}"\n'
                f'REFRESH_PRIVATE_KEY="{new_refresh_private}"\n'
                f'REFRESH_PUBLIC_KEY="{new_refresh_public}"\n'
                f'PREVIOUS_REFRESH_PUBLIC_KEY="{old_refresh_public}"\n'
            )

        print("🔑 Ключи обновлены и сохранены в .env.keys!")

    @staticmethod
    def generate_es256_keys():
        """Генерация пары ES256 ключей"""
        private_key = subprocess.run(
            ["openssl", "ecparam", "-name", "prime256v1", "-genkey", "-noout"],
            capture_output=True, text=True
        ).stdout.strip()

        public_key = subprocess.run(
            ["openssl", "ec", "-pubout"],
            input=private_key, capture_output=True, text=True
        ).stdout.strip()

        return private_key, public_key
