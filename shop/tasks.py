from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_order_email_task(email, order_id, total_price, items):
    try:
        logger.info(f"Запуск задачи отправки письма для заказа #{order_id} на email {email}")

        items_with_total = [
            {
                "product": item["product"],
                "quantity": item["quantity"],
                "price": item["price"],
                "total": item["quantity"] * item["price"]
            }
            for item in items
        ]

        logger.info(f"Детали заказа #{order_id}: {items_with_total}")

        html_content = render_to_string('order_email.html', {
            'order_id': order_id,
            'total_price': total_price,
            'items': items_with_total
        })

        subject = f"Ваш заказ #{order_id} успешно создан"
        text_content = (
            f"Ваш заказ #{order_id} был успешно создан и оплачен.\n"
            f"Общая сумма: {total_price} руб.\n"
        )

        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        logger.info(f"Письмо для заказа #{order_id} успешно отправлено на {email}")

    except Exception as e:
        logger.error(f"Ошибка при отправке письма для заказа #{order_id} на email {email}: {str(e)}")
        raise e
