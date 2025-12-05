import pytest
from unittest.mock import patch
from rest_framework.test import APIClient

from payouts.models import CurrencyChoice, Payout, PaymentMethodChoice


@pytest.fixture
def api_client():
    """Неавторизованный APIClient."""
    return APIClient()


@pytest.fixture
@patch("payouts.signals.process_payout_task.delay")
def payout_card(mocked_delay):
    """Фикстура для создания выплаты на карту."""
    payout = Payout.objects.create(
        method=PaymentMethodChoice.CARD_TRANSFER,
        amount=100.0,
        currency=CurrencyChoice.RUB,
        bank_name="Test bank",
        card_number="1234567890123456",
        phone="89526984567",
        description="Test payout to card"
    )
    return payout


@pytest.fixture
@patch("payouts.signals.process_payout_task.delay")
def payout_bank(mocked_delay):
    """Фикстура для создания выплаты на банковский счёт."""
    payouts = Payout.objects.create(
        method=PaymentMethodChoice.BANK_TRANSFER,
        amount=250.0,
        currency=CurrencyChoice.USD,
        bank_name="T-Bank",
        bank_bik="044525974",
        account_number="12345678901234567890",
        phone="8954258954321",
        description="Test payout to bank account"
    )
    return payouts
