from yookassa import Configuration, Payment
import uuid
from app.core.config import settings

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


class YooKassaService:
    @staticmethod
    def create_payment(amount: float, description: str, return_url: str):
        """Создать платеж в ЮKassa"""
        idempotence_key = str(uuid.uuid4())

        payment = Payment.create({
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description
        }, idempotence_key)

        return {
            "id": payment.id,
            "status": payment.status,
            "confirmation_url": payment.confirmation.confirmation_url
        }

    @staticmethod
    def check_payment_status(payment_id: str):
        """Проверить статус платежа"""
        payment = Payment.find_one(payment_id)
        return payment.status