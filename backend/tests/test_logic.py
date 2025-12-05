import re
import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status

from payouts.models import (
    CurrencyChoice,
    Payout,
    PaymentMethodChoice,
    StatusChoice
)


pytestmark = pytest.mark.django_db


class TestPayoutPossitive:
    """Набор положительных тестов по работе с выплатами."""

    @patch("payouts.signals.process_payout_task.delay")
    def test_create_payout_bank(self, mocked_delay, api_client):
        """Тест создания заявки на выплату на счёт."""
        url = reverse("api:payouts-list")
        data = {
            "method": PaymentMethodChoice.BANK_TRANSFER,
            "amount": 1045.5,
            "currency": CurrencyChoice.RUB,
            "bank_name": "Сбербанк",
            "bank_bik": "044525225",
            "account_number": "40817810099910004312",
            "phone": "+79856584565",
            "description": "Оплата обучения"
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["method"] == PaymentMethodChoice.BANK_TRANSFER
        assert Payout.objects.filter(
            payout_uid=response.data["payout_uid"]
        ).exists()
        mocked_delay.assert_called_once_with(response.data["payout_uid"])

    @patch("payouts.signals.process_payout_task.delay")
    def test_create_payout_card(self, mocked_delay, api_client):
        """Тест создания заявки на выплату на карту."""
        url = reverse("api:payouts-list")
        data = {
            "method": PaymentMethodChoice.CARD_TRANSFER,
            "amount": 1000.0,
            "currency": CurrencyChoice.RUB,
            "bank_name": "Тинькофф",
            "card_number": "2201221554561245",
            "phone": "+79856584565",
        }

        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        payout_uid = response.data["payout_uid"]
        mocked_delay.assert_called_once_with(payout_uid)

    def test_get_payout(self, api_client, payout_card):
        """Тест получения информации по заявке на выплату."""
        url = reverse("api:payouts-detail", args=[payout_card.payout_uid])
        response = api_client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data["payout_uid"] == str(payout_card.payout_uid)
        assert response.data["method"] == PaymentMethodChoice.CARD_TRANSFER

    def test_list_payouts(self, api_client, payout_bank, payout_card):
        """Тест на получения списка заявок на выплату."""
        url = reverse("api:payouts-list")
        response = api_client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 2
        payout_uids = [item["payout_uid"] for item in response.data["results"]]
        assert str(payout_bank.payout_uid) in payout_uids

    def test_partial_update_payout(self, api_client, payout_card):
        """Тест частичного обновления заявки на выплату."""
        url = reverse("api:payouts-detail", args=[payout_card.payout_uid])
        data = {
            "status": StatusChoice.CANCELLED,
        }
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == StatusChoice.CANCELLED

    def test_delete_payout(self, api_client, payout_card):
        """Тест на удаления заявки на выплату."""
        url = reverse("api:payouts-detail", args=[payout_card.payout_uid])
        response = api_client.delete(url, format='json')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Payout.objects.filter(
            payout_uid=payout_card.payout_uid
        ).exists()


class TestPayoutNegative:
    """Набор отрицательных тестов по работе с выплатами."""

    @pytest.mark.parametrize(
        "data,invalid_field",
        [
            (
                {
                    "method": PaymentMethodChoice.CARD_TRANSFER,
                    "amount": 1000.0,
                    "currency": CurrencyChoice.RUB,
                    "bank_name": "Тинькофф",
                    "phone": "+79856584565",
                },
                "card_number",
            ),
            (
                {
                    "method": PaymentMethodChoice.CARD_TRANSFER,
                    "amount": 1000.0,
                    "currency": CurrencyChoice.RUB,
                    "bank_name": "Тинькофф",
                    "phone": "+79856584565",
                    "card_number": "1234ABCD5678EFGH",
                },
                "card_number",
            ),
            (
                {
                    "method": PaymentMethodChoice.BANK_TRANSFER,
                    "amount": 1500.0,
                    "currency": CurrencyChoice.USD,
                    "bank_name": "Сбербанк",
                    "phone": "+79856584565",
                },
                "account_number",
            ),
            (
                {
                    "method": PaymentMethodChoice.BANK_TRANSFER,
                    "amount": 1500.0,
                    "currency": CurrencyChoice.USD,
                    "bank_name": "Сбербанк",
                    "phone": "+79856584565",
                    "account_number": "12345INVALID67890",
                },
                "account_number",
            ),
            (
                {
                    "method": PaymentMethodChoice.BANK_TRANSFER,
                    "amount": 1500.0,
                    "currency": "рубли",
                    "bank_name": "Сбербанк",
                    "phone": "+79856584565",
                    "account_number": "40817810099910004312",
                },
                "currency",
            ),
            (
                {
                    "method": PaymentMethodChoice.BANK_TRANSFER,
                    "amount": -1500.0,
                    "currency": CurrencyChoice.USD,
                    "bank_name": "Сбербанк",
                    "phone": "+79856584565",
                    "account_number": "40817810099910004312",
                },
                "amount",
            ),
            (
                {
                    "method": PaymentMethodChoice.BANK_TRANSFER,
                    "amount": 1500.0,
                    "currency": CurrencyChoice.USD,
                    "bank_name": "Сбербанк",
                    "phone": "+7584565",
                    "account_number": "40817810099910004312",
                },
                "phone",
            ),
        ],
    )
    def test_create_payout_negative(self, api_client, data, invalid_field):
        url = reverse("api:payouts-list")
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert invalid_field in response.data

    def test_get_nonexistent_payout(self, api_client):
        """Тест на получение несуществующей заявки на выплату."""
        url = reverse(
            "api:payouts-detail",
            args=["00000-0000-0000-0000-00000"]
        )
        response = api_client.get(url, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_partial_update_payout(self, api_client, payout_card):
        """Тест изменения заявки на выплату с некорретными данными."""
        url = reverse("api:payouts-detail", args=[payout_card.payout_uid])
        data = {
            "status": "unknown_status",
        }
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "status" in response.data
