from django.db import models
from model_utils.models import TimeStampedModel

class BaseModel(TimeStampedModel):
    """
    Базовая модель с полями created и modified
    """
    class Meta:
        abstract = True
