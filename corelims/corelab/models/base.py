from django.db import models
from django.conf import settings
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


class BaseModel(models.Model):
    dateofcreation = CreationDateTimeField(verbose_name="Created at")
    lastmodification = ModificationDateTimeField(verbose_name="Last modified")
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        verbose_name="Last modified by",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        abstract = True
