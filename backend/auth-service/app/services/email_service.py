from email.message import EmailMessage

import aiosmtplib

from app.config import settings
from app.repositories.redisRepository import RedisRepository
from app.utils.helpers import create_email_verification__token


class EmailService:
    def __init__(self, redis_repository: RedisRepository):
        self.redis_repository= redis_repository
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_sender = settings.SMTP_SENDER
        self.smtp_password = settings.SMTP_PASSWORD
        self.service_host = "localhost"  # убрать в переменные окружения !!!
        self.service_port = "8000"

    async def send_email_verification(self, recipient_email: str, token: str) -> None:
        verification_link = f"http://{self.service_host}:{self.service_port}/verify-email?email={recipient_email}&token={token}"

        message = EmailMessage()
        message["From"] = self.smtp_sender
        message["To"] = recipient_email
        message["Subject"] = "Email Verification"
        message.set_content(f"""
        Hello!

        To confirm your email, please follow the link:
        {verification_link}

        If you did not request confirmation, just ignore this letter.

        Thank you,
        Basket.log team.
        """)

        try:
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_sender,
                password=self.smtp_password,
                use_tls=True  # TLS для безопасного соединения
            )
            print("отправлено")
        except Exception as e:  # залогировать, ДОБАВИТЬ КАСТОМ ОШИБКУ!!!
            print(f"Ошибка при отправке письма: {e}")

    async def generate_email_verification_token(self, email: str) -> str:
        verification_token = create_email_verification__token()
        await self.redis_repository.set_value(key=email,
                                              value=verification_token,
                                              ttl=settings.VERIFICATION_TOKEN_EXPIRE_TIME_MINUTES)
        return verification_token

    async def verify_email_verification_token(self, email: str, token: str) -> bool:
        stored_token = await self.redis_repository.get_value(email)
        if stored_token == token:
            await self.redis_repository.delete_key(email)
            return True
        return False
