import time
import logging

from celery import shared_task
from django.utils import timezone

from .models import Payout, StatusChoice, PaymentMethodChoice


logger = logging.getLogger(__name__)


@shared_task
def process_payout_task(payout_uid):
    try:
        payout = Payout.objects.get(pk=payout_uid)
    except Payout.DoesNotExist:
        logger.error(f"Заявка с id={payout_uid} не найдена")
        return
    logger.info(
        f"Начата обработка заявки {payout.payout_uid} "
        f"({payout.amount} {payout.currency})"
    )
    payout.status = StatusChoice.PROCESSING
    payout.save(update_fields=["status", "updated_at"])
    time.sleep(5)  # имитация обработки
    if payout.amount <= 0:
        payout.status = StatusChoice.REJECTED
        payout.save(update_fields=["status", "updated_at"])
        logger.warning(f"Заявка {payout.payout_uid} провалена (сумма <= 0)")
        return
    if payout.method == PaymentMethodChoice.BANK_TRANSFER:
        if not payout.account_number or len(payout.account_number) != 20:
            payout.status = StatusChoice.REJECTED
            payout.save(update_fields=["status", "updated_at"])
            logger.warning(
                f"Заявка {payout.payout_uid} отклонена: некорректный счёт"
            )
            return
    elif payout.method == PaymentMethodChoice.CARD_TRANSFER:
        if not payout.card_number or len(payout.card_number) != 16:
            payout.status = StatusChoice.REJECTED
            payout.save(update_fields=["status", "updated_at"])
            logger.warning(
                f"Заявка {payout.payout_uid} отклонена: некорректный номер"
            )
            return
    payout.status = StatusChoice.COMPLETED
    payout.updated_at = timezone.now()
    payout.save(update_fields=["status", "updated_at"])
    logger.info(f"Заявка {payout.payout_uid} успешно обработана")
    return payout.status
