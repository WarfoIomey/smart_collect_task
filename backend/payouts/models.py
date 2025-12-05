from decimal import Decimal
import uuid

from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField

import payouts.constants as constants


class CurrencyChoice(models.TextChoices):
    RUB = 'RUB', 'Рубли (RUB)'
    USD = 'USD', 'Доллар США (USD)'
    EUR = 'EUR', 'Евро (EUR)'
    CNY = 'CNY', 'Юани (CNY)'


class StatusChoice(models.TextChoices):
    PENDING = 'pending', 'На рассмотрении'
    APPROVED = 'approved', 'Утверждена'
    PROCESSING = 'processing', 'В обработке'
    COMPLETED = 'completed', 'Выполнена'
    REJECTED = 'rejected', 'Отклонена'
    CANCELLED = 'cancelled', 'Отменена'


class PaymentMethodChoice(models.TextChoices):
    BANK_TRANSFER = 'bank', 'Банковский перевод'
    CARD_TRANSFER = 'card', 'Перевод на карту'


class Payout(models.Model):
    """Модель заявки на выплату."""

    payout_uid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="UUID заявки",
        primary_key=True
    )
    method = models.CharField(
        choices=PaymentMethodChoice.choices,
        verbose_name="Способ выплаты",
        help_text="Выберите способ выплаты",
    )
    amount = models.DecimalField(
        max_digits=constants.MAX_DIGITS_AMOUNT,
        decimal_places=constants.MAX_DECIMAL_PLACES,
        validators=[MinValueValidator(Decimal(constants.MIN_AMOUNT)),],
        verbose_name="Сумма выплаты",
        help_text="Cумма к выплаты"
    )
    currency = models.CharField(
        choices=CurrencyChoice.choices,
        default=CurrencyChoice.RUB,
        verbose_name="Валюта",
        help_text="Выберите тип валюты",
    )
    status = models.CharField(
        choices=StatusChoice.choices,
        default=StatusChoice.PENDING,
        verbose_name='Статус заявки',
    )
    bank_name = models.CharField(
        max_length=constants.MAX_BANK_NAME,
        verbose_name="Банк",
    )
    bank_bik = models.CharField(
        max_length=constants.MAX_BANK_BIK,
        verbose_name='БИК банка',
        help_text='Банковский идентификационный код',
        blank=True
    )
    card_number = models.CharField(
        max_length=constants.MAX_CARD_NUMBER,
        verbose_name="Номер карты",
        blank=True
    )
    account_number = models.CharField(
        max_length=constants.MAX_ACCOUNT_NUMBER,
        verbose_name="Номер счёта",
        blank=True
    )
    phone = PhoneNumberField(
        verbose_name='Контактный телефон',
        help_text='Телефон для связи по выплате'
    )
    description = models.TextField(
        verbose_name='Описание / Комментарий',
        blank=True,
        help_text='Основание для выплаты, назначение платежа'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["status", "currency"]),
            models.Index(fields=["method"]),
            models.Index(fields=["created_at"]),
        ]
        verbose_name = "Заявка на выплату"
        verbose_name_plural = "Заявки на выплату"

    def __str__(self):
        return (
            f'Заявка {self.payout_uid} на сумму {self.amount}'
            f'{self.currency} - Статус: {self.status}'
        )
