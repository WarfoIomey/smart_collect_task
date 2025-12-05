from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Payout
from .tasks import process_payout_task


@receiver(post_save, sender=Payout)
def run_payout_task(sender, instance, created, **kwargs):
    if created:
        process_payout_task.delay(str(instance.payout_uid))
