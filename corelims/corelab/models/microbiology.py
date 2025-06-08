"""
Microbiology models for handling microbiological results, tests, and related entities.
This module defines various models to manage microbiology results, tests, antibiotics, and their relationships within the core lab application.
"""

from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import ModificationDateTimeField

from corelab.models import Orders, OrderTests, Tests

MIB_RESULT_TYPE = (
    ("AL", "All type"),
    ("MT", "Main test"),
    ("CM", "Culture medium"),
    ("ST", "Secondary test"),
    ("AB", "Antibogram"),
    ("ID", "Isolate description"),
    ("MQ", "Microorganism quantification"),
    ("MO", "Microorganism"),
    ("AB", "Antibiotic"),
)


class MBResults(models.Model):
    code = models.CharField(max_length=10, verbose_name=_("Code"), unique=True)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    type = models.CharField(
        max_length=3,
        verbose_name=_("result type"),
        choices=MIB_RESULT_TYPE,
        null=True,
        blank=True,
    )
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    sort = models.IntegerField(verbose_name=_("Sort"), help_text=_("Sorted priority"))
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.code, self.name)

    class Meta:
        verbose_name_plural = "Microbiologi results"
        verbose_name = "Microbiologi results"
        ordering = ["sort"]


class MBResultGroups(models.Model):
    code = models.CharField(max_length=10, verbose_name=_("Code"), unique=True)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    sort = models.IntegerField(verbose_name=_("Sort"), help_text=_("Sorted priority"))
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.code, self.name)


class MBResultGroupItems(models.Model):
    mb_result_group = models.ForeignKey(
        MBResultGroups,
        on_delete=models.PROTECT,
        verbose_name=_("Result groups"),
        related_name="mbresultgroupitem_mbresultgroup",
    )
    mb_result = models.ForeignKey(
        MBResults,
        on_delete=models.PROTECT,
        verbose_name=_("Result"),
        related_name="mbresultgroupitem_mbresult",
    )
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.mb_result_group, self.mb_result)


class MBAntibioticFamilies(models.Model):
    code = models.CharField(max_length=10, verbose_name=_("Code"), unique=True)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    sort = models.IntegerField(verbose_name=_("Sort"), help_text=_("Sorted priority"))
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.code, self.name)

    class Meta:
        verbose_name_plural = "Mb antibiotic families"
        verbose_name = "Mb antibiotic families"


class MBAntibiotics(models.Model):
    code = models.CharField(max_length=10, verbose_name=_("Code"), unique=True)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    family = models.ForeignKey(
        MBAntibioticFamilies,
        on_delete=models.PROTECT,
        verbose_name=_("Antibiotic family"),
        related_name="mbantibiotic_mbantibioticfamilies",
    )
    low = models.DecimalField(
        decimal_places=2, max_digits=20, verbose_name=_("low"), blank=True, null=True
    )
    high = models.DecimalField(
        decimal_places=2, max_digits=20, verbose_name=_("high"), blank=True, null=True
    )
    sort = models.IntegerField(verbose_name=_("Sort"), help_text=_("Sorted priority"))
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    print_assesment = models.BooleanField(
        verbose_name=_("Print assessment"), default=True, blank=True
    )
    print_method = models.BooleanField(
        verbose_name=_("Print method"), default=True, blank=True
    )
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.code, self.name)

    class Meta:
        verbose_name_plural = "Microbiologi antibiotics"
        verbose_name = "Microbiologi antibiotics"
        ordering = ["family", "sort"]


class MBAntibioticMethods(models.Model):
    code = models.CharField(max_length=10, verbose_name=_("Code"), unique=True)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    sort = models.IntegerField(verbose_name=_("Sort"), help_text=_("Sorted priority"))
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        verbose_name_plural = "Mb antibiotic methods"
        verbose_name = "Mb antibiotic methods"

    def __str__(self):
        return "%s - %s" % (self.code, self.name)


class MBAntibiograms(models.Model):
    code = models.CharField(max_length=10, verbose_name=_("Code"), unique=True)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    relative_value_unit = models.CharField(
        max_length=200, verbose_name=_("Relative value unit"), blank=True
    )
    sort = models.IntegerField(verbose_name=_("Sort"), help_text=_("Sorted priority"))
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    print_assesment = models.BooleanField(
        verbose_name=_("Print assessment"), default=True, blank=True
    )
    print_method = models.BooleanField(
        verbose_name=_("Print method"), default=True, blank=True
    )
    print_label = models.BooleanField(
        verbose_name=_("Print label"), default=True, blank=True
    )
    mb_antibiotic_method = models.ForeignKey(
        MBAntibioticMethods,
        on_delete=models.PROTECT,
        verbose_name=_("Antibiotic method"),
        related_name="mbantibiogram_mbantibioticmethod",
    )
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.code, self.name)

    class Meta:
        verbose_name_plural = "Microbiologi antibiograms"
        verbose_name = "Microbiologi antibiograms"
        ordering = ["mb_antibiotic_method", "sort"]


class MBAntibiogramAntibiotics(models.Model):
    mb_antibiogram = models.ForeignKey(
        MBAntibiograms,
        on_delete=models.PROTECT,
        verbose_name=_("Antibiogram"),
        related_name="mbantibiogram_mbantibiogram",
    )
    mb_antibiotic = models.ForeignKey(
        MBAntibiotics,
        on_delete=models.PROTECT,
        verbose_name=_("Antibiotic"),
        related_name="mbantibiogram_mbantibiotic",
    )
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.mb_antibiogram, self.mb_antibiotic)

    class Meta:
        unique_together = (("mb_antibiogram", "mb_antibiotic"),)

    class Meta:
        verbose_name_plural = "Mb antibiogram antibiotics"
        verbose_name = "Mb antibiogram antibiotics"


class MBCultureMedia(models.Model):
    code = models.CharField(max_length=10, verbose_name=_("Code"), unique=True)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    relative_value_unit = models.CharField(
        max_length=200, verbose_name=_("Relative value unit"), blank=True
    )
    sort = models.IntegerField(verbose_name=_("Sort"), help_text=_("Sorted priority"))
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    can_seeded = models.BooleanField(
        verbose_name=_("it can be seeded."), default=True, blank=True
    )
    visible = models.BooleanField(verbose_name=_("Visible"), default=True, blank=True)
    print_label = models.BooleanField(
        verbose_name=_("Print label"), default=True, blank=True
    )
    # mb_antibiotic_method = models.ForeignKey(MBAntibiotics,on_delete=models.PROTECT,verbose_name=_("Antibiotic method"),related_name='mbculturemedia_mbantibioticmethod')
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.code, self.name)


MIB_TEST_TYPE = (
    ("M", "Main"),
    ("S", "Secondary"),
)


class MBTests(models.Model):
    test = models.OneToOneField(
        Tests,
        on_delete=models.PROTECT,
        primary_key=True,
    )
    type = models.CharField(
        max_length=3,
        verbose_name=_("test type"),
        choices=MIB_TEST_TYPE,
        default="M",
        blank=True,
    )
    relative_value_unit = models.CharField(
        max_length=200, verbose_name=_("Relative value unit"), blank=True
    )
    sort = models.IntegerField(verbose_name=_("Sort"), help_text=_("Sorted priority"))
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    print_isolates = models.BooleanField(
        verbose_name=_("Print isolates"), default=True, blank=True
    )
    printable = models.BooleanField(
        verbose_name=_("Printable"), default=True, blank=True
    )
    print_label = models.BooleanField(
        verbose_name=_("Print label"), default=True, blank=True
    )
    comment = models.TextField(verbose_name=_("Comment"), blank=True)
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.test, self.type)

    class Meta:
        verbose_name_plural = "Microbiologi tests"
        verbose_name = "Microbiologi tests"
        ordering = ["sort"]


class MBTestCultureMedia(models.Model):
    mb_test = models.ForeignKey(
        MBTests,
        on_delete=models.PROTECT,
        verbose_name=_("Test"),
        related_name="mbtestculturemdia_mbtest",
    )
    mb_culture_media = models.ForeignKey(
        MBCultureMedia,
        on_delete=models.PROTECT,
        verbose_name=_("Culture media"),
        related_name="mbtestculturemedia_mbculturemedia",
    )
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.mb_test, self.mb_culture_media)


class MBAnatomicLocation(models.Model):
    code = models.CharField(max_length=10, verbose_name=_("Code"), unique=True)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.code, self.name)


class MBResultHeader(models.Model):
    order_test = models.ForeignKey(
        OrderTests,
        on_delete=models.PROTECT,
        verbose_name=_("Order test"),
        related_name="mbresultheader_ordertest",
    )
    mb_result = models.ForeignKey(
        MBResults,
        on_delete=models.PROTECT,
        verbose_name=_("MB Result"),
        related_name="mbresultheader_mbresult",
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), auto_now_add=True
    )
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.order_test, self.mb_result)


class MBResultDetail(models.Model):
    mb_result_header = models.ForeignKey(
        MBResultHeader,
        on_delete=models.PROTECT,
        verbose_name=_("MB Result Header"),
        related_name="mbresultdetail_mbresultheader",
    )
    mb_antibiogram = models.ForeignKey(
        MBAntibiograms,
        on_delete=models.PROTECT,
        verbose_name=_("MB Antibiogram"),
        related_name="mbresultdetail_mbantibiogram",
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), auto_now_add=True
    )
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.mb_result_header, self.mb_result)

    class Meta:
        unique_together = (("mb_result_header", "mb_antibiogram"),)


MIB_ANTIBIOTIC_RESULT = (("R", "RESISTENCE"), ("I", "INTERMEDIATE"), ("S", "SENSITIVE"))


class MBResultDetailAntibiotics(models.Model):
    mb_result_detail = models.ForeignKey(
        MBResultDetail,
        on_delete=models.PROTECT,
        verbose_name=_("MB Result Detail"),
        related_name="mbresultdetailantibiotic_mbresultdetail",
    )
    mb_antibiotic = models.ForeignKey(
        MBAntibiotics,
        on_delete=models.PROTECT,
        verbose_name=_("MB Antibiotic"),
        related_name="mbresultdetailantibiotic_mbaresultdetail",
    )
    low = models.DecimalField(
        decimal_places=2, max_digits=20, verbose_name=_("low"), blank=True, null=True
    )
    high = models.DecimalField(
        decimal_places=2, max_digits=20, verbose_name=_("high"), blank=True, null=True
    )
    num_value = models.DecimalField(
        decimal_places=2, max_digits=20, verbose_name=_("value"), blank=True, null=True
    )
    char_value = models.CharField(
        max_length=2,
        verbose_name=_("char value"),
        choices=MIB_ANTIBIOTIC_RESULT,
        null=True,
        blank=True,
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), auto_now_add=True
    )

    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s - %s" % (self.mb_result_header, self.mb_result)

    class Meta:
        unique_together = (("mb_result_detail", "mb_antibiotic"),)


class MBOrderExtended(models.Model):
    order = models.OneToOneField(
        Orders,
        on_delete=models.PROTECT,
        primary_key=True,
    )
    note = models.TextField(verbose_name=_("Note for patients"), null=True, blank=True)

    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s" % (self.order)
