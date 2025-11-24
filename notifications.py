import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests
from app.core.config import settings


class NotificationService:
    @staticmethod
    def send_booking_confirmation(user, training, booking):
        """Отправить подтверждение записи"""
        subject = "Подтверждение записи на тренировку"
        message = f"""
        Здравствуйте, {user.first_name}!

        Вы успешно записаны на тренировку:
        Тренер: {training.trainer.user.first_name} {training.trainer.user.last_name}
        Время: {training.start_time.strftime('%d.%m.%Y %H:%M')}
        Тип: {'Индивидуальная' if training.type == 'individual' else 'Групповая'}

        Статус записи: {booking.status}
        """

        NotificationService._send_email(user.email, subject, message)

    @staticmethod
    def send_booking_cancellation(user, training):
        """Отправить уведомление об отмене записи"""
        subject = "Отмена записи на тренировку"
        message = f"""
        Здравствуйте, {user.first_name}!

        Ваша запись на тренировку отменена:
        Тренер: {training.trainer.user.first_name} {training.trainer.user.last_name}
        Время: {training.start_time.strftime('%d.%m.%Y %H:%M')}
        """

        NotificationService._send_email(user.email, subject, message)

    @staticmethod
    def _send_email(to_email: str, subject: str, message: str):
        """Отправить email"""
        try:
            if not to_email:
                return

            msg = MimeMultipart()
            msg['From'] = settings.SMTP_FROM
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MimeText(message, 'plain', 'utf-8'))

            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Ошибка отправки email: {e}")