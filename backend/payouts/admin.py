from django.contrib import admin

from .models import Payout


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = (
        'payout_uid',
        'amount',
        'currency',
        'status',
        'created_at',
        'updated_at',
    )
    list_filter = ('status', 'currency', 'created_at')
    search_fields = (
        'payout_uid',
        'bank_name',
        'bank_bik',
        'card_number',
        'account_number',
        'phone'
    )
    ordering = ('-created_at',)
    readonly_fields = (
        'payout_uid',
        'created_at',
        'updated_at',
    )
