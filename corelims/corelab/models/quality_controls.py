from django.db import models

from corelab.models.models import Instruments, Tests


class QCLots(models.Model):
    """
    Class to handle quality control lots.
    """

    control_name = models.CharField(max_length=100)
    supplier = models.CharField(max_length=100, null=True, blank=True)
    test = models.ForeignKey(
        Tests, on_delete=models.CASCADE, related_name="qc_lots_test"
    )
    activation_date = models.DateField(null=True, blank=True)
    deactivation_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    review_status = models.BooleanField(default=False)
    review_date = models.DateField(null=True, blank=True)
    review_user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="qc_lots_review_user",
    )

    instrument = models.ForeignKey(
        Instruments, on_delete=models.CASCADE, related_name="qc_lots_instrument"
    )
    lot_number = models.CharField(max_length=100)
    expiry_date = models.DateField(null=True, blank=True)
    target_value = models.FloatField(null=True, blank=True)
    standard_deviation = models.FloatField(null=True, blank=True)
    control_range = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"QCLot(instrument={self.instrument}, lot_number={self.lot_number})"


class QCMeasurements(models.Model):
    """
    Class to handle quality control measurements.
    """

    date = models.DateTimeField(auto_now_add=True)
    qc_lot = models.ForeignKey(
        QCLots, on_delete=models.CASCADE, related_name="qc_lots_measurements"
    )
    result = models.ForeignKey(
        Instruments, on_delete=models.CASCADE, related_name="qc_measurements"
    )

    def __str__(self):
        return f"QCMeasurements(instrument={self.qc_lot}, result={self.result})"
