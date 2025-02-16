import os
import re
import subprocess

KEYS_FILE = ".env.keys"


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


def load_existing_keys():
    """Загружаем текущие ключи из файла .env.keys"""
    keys = {}
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "r") as f:
            content = f.read()

        # Регулярное выражение для извлечения ключей (учитываем многострочные значения)
        pattern = re.compile(r'(\w+)=(".*?")', re.DOTALL)
        keys = {key: value.strip('"') for key, value in pattern.findall(content)}

    return keys


def rotate_keys():
    """Ротация ключей: ACCESS, REFRESH и VERIFICATION_SECRET_KEY"""
    existing_keys = load_existing_keys()

    # Сохраняем предыдущие ключи
    old_access_private = existing_keys.get("ACCESS_PRIVATE_KEY", "")
    old_access_public = existing_keys.get("ACCESS_PUBLIC_KEY", "")
    old_refresh_private = existing_keys.get("REFRESH_PRIVATE_KEY", "")
    old_refresh_public = existing_keys.get("REFRESH_PUBLIC_KEY", "")
    old_verification_secret = existing_keys.get("VERIFICATION_SECRET_KEY", "")

    # Генерируем новые ключи
    new_access_private, new_access_public = generate_es256_keys()
    new_refresh_private, new_refresh_public = generate_es256_keys()

    # Генерируем новый секретный ключ для токенов верификации
    new_verification_secret = subprocess.run(
        ["openssl", "rand", "-hex", "32"],
        capture_output=True, text=True
    ).stdout.strip()

    # Обновляем файл .env.keys
    with open(KEYS_FILE, "w") as f:
        f.write(
            f'ACCESS_PRIVATE_KEY="{new_access_private}"\n'
            f'ACCESS_PUBLIC_KEY="{new_access_public}"\n'
            f'PREVIOUS_ACCESS_PRIVATE_KEY="{old_access_private}"\n'
            f'PREVIOUS_ACCESS_PUBLIC_KEY="{old_access_public}"\n'
            f'REFRESH_PRIVATE_KEY="{new_refresh_private}"\n'
            f'REFRESH_PUBLIC_KEY="{new_refresh_public}"\n'
            f'PREVIOUS_REFRESH_PRIVATE_KEY="{old_refresh_private}"\n'
            f'PREVIOUS_REFRESH_PUBLIC_KEY="{old_refresh_public}"\n'
            f'VERIFICATION_SECRET_KEY="{new_verification_secret}"\n'
            f'PREVIOUS_VERIFICATION_SECRET_KEY="{old_verification_secret}"\n'
        )

    print("🔑 Ключи обновлены и сохранены в .env.keys!")


if __name__ == "__main__":
    rotate_keys()
