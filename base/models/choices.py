from django.db import models

class NotificationSubjectAll(models.TextChoices):
    ALL = "all", "All"


class PriorityChoices(models.TextChoices):
    HIGH = 'high', 'High'
    NORMAL = 'normal', 'Normal'
