from django.db import models
from django.urls import reverse
from .base import BaseModel


class Patients(BaseModel):
    patient_id = models.CharField(
        max_length=100, unique=True, verbose_name="Patient ID"
    )
    name = models.CharField(max_length=100, verbose_name="Name")
    dob = models.DateField(verbose_name="Date of birth")
    address = models.CharField(max_length=100, verbose_name="Address")

    def calculate_age(self):
        from datetime import date

        today = date.today()
        return (
            today.year
            - self.dob.year
            - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    def __str__(self):
        return f"{self.patient_id} - {self.name}"

    def get_absolute_url(self):
        return reverse("patient_detail", args=[str(self.id)])

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        ordering = ["patient_id", "name"]
