from email.message import EmailMessage

import aiosmtplib

from app.config import settings
from app.logger import logger
from app.repositories.redisRepository import RedisRepository
from app.utils.helpers import create_email_verification_token


class EmailService:
    def __init__(self, redis_repository: RedisRepository):
        self.redis_repository = redis_repository
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_sender = settings.SMTP_SENDER
        self.smtp_password = settings.SMTP_PASSWORD
        self.service_host = "localhost"  # убрать в переменные окружения !!!
        self.service_port = "8000"

    async def send_email(self, recipient_email: str, subject: str, body: str) -> None:
        """Универсальный метод отправки писем"""
        message = EmailMessage()
        message["From"] = self.smtp_sender
        message["To"] = recipient_email
        message["Subject"] = subject
        message.set_content(body)

        await aiosmtplib.send(
            message,
            hostname=self.smtp_host,
            port=self.smtp_port,
            username=self.smtp_sender,
            password=self.smtp_password,
            use_tls=True
        )
        logger.info(f"Email sent to {recipient_email} with subject: {subject}")

    async def send_email_verification(self, recipient_email: str, token: str) -> None:
        """Отправка письма для верификации email"""
        verification_link = f"http://{self.service_host}:{self.service_port}/verify-email?email={recipient_email}&token={token}"
        body = f"""
        Hello!

        To confirm your email, please follow the link:
        {verification_link}

        If you did not request confirmation, just ignore this letter.

        Thank you,
        Basket.log team.
        """
        await self.send_email(recipient_email, "Email Verification", body)

    async def send_password_change_notification(self, email: str):
        """Отправка уведомления о смене пароля"""
        body = "Your password has been changed. If this was not you, please contact support immediately."
        await self.send_email(email, "Password Changed", body)

    async def generate_email_verification_token(self, email: str) -> str:
        verification_token = create_email_verification_token()
        await self.redis_repository.set_value(key=email,
                                              value=verification_token,
                                              ttl=int(settings.VERIFICATION_TOKEN_EXPIRE_TIME_MINUTES) * 60)
        return verification_token

    async def verify_email_verification_token(self, email: str, token: str) -> bool:
        stored_token = await self.redis_repository.get_value(email)
        if stored_token == token:
            await self.redis_repository.delete_key(email)
            return True
        return False
