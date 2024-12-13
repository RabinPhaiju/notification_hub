from django.db import models

class OfferNotificationSubject(models.TextChoices):
    NEW_OFFER = "new_offer", "New Offer"
    OFFER_REMINDER = "offer_reminder", "Offer Reminder"
