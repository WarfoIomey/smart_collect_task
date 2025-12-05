from django.contrib.auth import get_user_model
from rest_framework import serializers

from payouts.models import PaymentMethodChoice, Payout


User = get_user_model()


class PayoutReadSerializer(serializers.ModelSerializer):
    """Сериализатор для выплат."""

    class Meta:
        model = Payout
        fields = (
            'payout_uid',
            'amount',
            'method',
            'currency',
            'status',
            'bank_name',
            'bank_bik',
            'card_number',
            'account_number',
            'phone',
            'description',
            'created_at',
            'updated_at'
        )


class PayoutCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания выплат."""

    method = serializers.ChoiceField(
        choices=PaymentMethodChoice.choices,
        help_text="Выберите способ выплаты"
    )

    class Meta:
        model = Payout
        fields = (
            'payout_uid',
            'method',
            'amount',
            'currency',
            'bank_name',
            'bank_bik',
            'card_number',
            'account_number',
            'phone',
            'description',
        )
        read_only_fields = ('payout_uid',)

    def validate(self, attrs):
        method = attrs.get('method')
        card = attrs.get('card_number')
        account = attrs.get('account_number')
        if method == "card":
            if not card:
                raise serializers.ValidationError({
                    "card_number": "Для выплаты на карту требуется card_number"
                })
            if not card.isdigit() or len(card) != 16:
                raise serializers.ValidationError(
                    {"card_number": "Номер карты должен содержать 16 цифр"}
                )
        if method == "bank":
            if not account:
                raise serializers.ValidationError({
                    "account_number": (
                        "Для выплаты на банковский счёт "
                        "требуется account_number"
                    )
                })
            if not account.isdigit() or len(account) != 20:
                raise serializers.ValidationError(
                    {"account_number": "Номер счёта должен содержать 20 цифр"}
                )
        return attrs


class PayoutUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления выплат."""

    method = serializers.ChoiceField(
        choices=PaymentMethodChoice.choices,
        help_text="Выберите способ выплаты",
        required=False,
    )

    class Meta:
        model = Payout
        fields = (
            'status',
            'method',
            'bank_name',
            'bank_bik',
            'card_number',
            'account_number',
            'phone',
            'description',
        )

    def validate(self, attrs):
        """Валидатор для проверки полей в зависимости от метода выплаты."""
        if self.instance is None:
            raise serializers.ValidationError({"detail": "Заявка не найдена"})
        method = attrs.get("method") or getattr(self.instance, "method", None)
        card = attrs.get("card_number") or getattr(
            self.instance, "card_number", None
        )
        account = attrs.get("account_number") or getattr(
            self.instance, "account_number", None
        )
        if not method:
            raise serializers.ValidationError(
                {"method": "Выберите допустимый способ выплаты"}
            )

        if method == "card":
            if "card_number" in attrs and not attrs["card_number"]:
                raise serializers.ValidationError(
                    {"card_number": "Номер карты не может быть пустым"}
                )
        if not card:
            raise serializers.ValidationError(
                {"card_number": "Для выплаты на карту требуется номер карты"}
            )
        if method == "bank":
            if "account_number" in attrs and not attrs["account_number"]:
                raise serializers.ValidationError(
                    {"account_number": "Номер счёта не может быть пустым"}
                )
            if not account:
                raise serializers.ValidationError(
                    {
                        "account_number": (
                            "Для выплаты на счёт "
                            "требуется номер счёта"
                        )
                    }
                )
        return attrs
