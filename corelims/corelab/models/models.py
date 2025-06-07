from __future__ import unicode_literals

from django.db import models
from django.db.models import ExpressionWrapper, F, Sum, DecimalField
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# from django.core.urlresolvers import reverse
from django.urls import reverse
from django.conf import settings
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from datetime import date
from collections import defaultdict
from num2words import num2words

from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token


from calendar import monthrange
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# from gcloud.bigtable import instance
from pickle import INST


# from Crypto.Util.asn1 import _is_number
def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


class Parameters(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    char_value = models.CharField(
        max_length=100, verbose_name=_("Char value"), null=True, blank=True
    )
    num_value = models.IntegerField(
        verbose_name=_("Numeric value"), null=True, blank=True
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

    def get_absolute_url(self):
        return reverse("parameters_detail", args=[str(self.id)])

    def __str__(self):
        return "%s %s %s" % (self.name, self.char_value, self.num_value)

    class Meta:
        verbose_name = _("Parameter")
        verbose_name_plural = _("Parameters")


class Organizations(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Organization Name"))
    ext_code = models.CharField(max_length=30, verbose_name=_("External code"))
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
        return self.name

    class Meta:
        verbose_name = _("Organisation")
        verbose_name_plural = _("Organisations")


class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Service Name"))
    ext_code = models.CharField(max_length=30, verbose_name=_("External code"))
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("service_detail", args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")


class Priority(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Group Name"))
    ext_code = models.CharField(max_length=30, verbose_name=_("External code"))
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("priority_detail", args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Priority")
        verbose_name_plural = _("Priorities")


class Insurance(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Insurance Name"))
    ext_code = models.CharField(max_length=30, verbose_name=_("External code"))
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("insurence_detail", args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Insurence")
        verbose_name_plural = _("Insurences")


class Doctors(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Doctor Name"))
    ext_code = models.CharField(max_length=30, verbose_name=_("External code"))
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("doctors_detail", args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Doctor")
        verbose_name_plural = _("Doctors")


class Origins(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Origin Name"))
    ext_code = models.CharField(max_length=30, verbose_name=_("External code"))
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("origins_detail", args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Origin")
        verbose_name_plural = _("Origins")


class Diagnosis(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Diangosis Name"))
    ext_code = models.CharField(max_length=30, verbose_name=_("External code"))
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("diagnosis_detail", args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Diagnosis")
        verbose_name_plural = _("Diagnosis")


class Genders(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Gender Name"))
    code = models.CharField(max_length=30, verbose_name=_("Code"), null=True)
    ext_code = models.CharField(max_length=30, verbose_name=_("External code"))
    inst_code = models.CharField(
        max_length=30, verbose_name=_("Instrument code"), null=True
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

    def get_absolute_url(self):
        return reverse("priority_detail", args=[str(self.id)])

    def __str__(self):
        return "%s (%s)" % (self.name, self.ext_code)

    class Meta:
        verbose_name = _("Gender")
        verbose_name_plural = _("Genders")


class Specimens(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Specimen Name"))
    suffix_code = models.CharField(max_length=3, verbose_name=_("Suffix code"))

    def get_absolute_url(self):
        return reverse("specimen_detail", args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Specimen")
        verbose_name_plural = _("Specimens")


class SuperGroups(models.Model):
    abbreviation = models.CharField(max_length=100, verbose_name=_("Abbreviation"))
    name = models.CharField(max_length=100, verbose_name=_("Name"))

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
        return "%s %s" % (self.abbreviation, self.name)

    class Meta:
        verbose_name = _("Super group")
        verbose_name_plural = _("Super groups")
        # permissions = (("view_supergroups", "Can view supergroups"),)
        ordering = ["name"]


class TestGroups(models.Model):
    supergroup = models.ForeignKey(
        SuperGroups,
        on_delete=models.PROTECT,
        verbose_name=_("Super Group"),
        related_name="testgroup_supergroup",
        null=True,
    )
    name = models.CharField(max_length=100, verbose_name=_("Group Name"))
    sort = models.IntegerField(verbose_name=_("Sort"), help_text=_("Sorted priority"))
    show_request = models.BooleanField(
        verbose_name=_("Show panel at request form"), default=True, blank=True
    )
    dateofcreation = CreationDateTimeField(verbose_name=_("Created at"))
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("testgroups_detail", args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Test group")
        verbose_name_plural = _("Test groups")
        # permissions = (("view_testgroups", "Can view testgroups"),)
        ordering = ["name"]


class Workarea(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
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
        return "%s" % (self.name)

    class Meta:
        verbose_name = _("Workarea")
        verbose_name_plural = _("Workareas")
        # permissions = (("view_workarea", "Can view worakarea"),)
        ordering = ["name"]


class WorkareaTestGroups(models.Model):
    workarea = models.ForeignKey(
        Workarea,
        on_delete=models.PROTECT,
        verbose_name=_("Workarea"),
        related_name="workareatestgroup_workarea",
        null=True,
    )
    testgroup = models.ForeignKey(
        TestGroups,
        on_delete=models.PROTECT,
        verbose_name=_("Testgroup"),
        related_name="workareatestgroup_testgroup",
        null=True,
    )
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
        return "%s %s" % (self.workarea, self.testgroup)

    class Meta:
        verbose_name = _("Workareatestgroup")
        verbose_name_plural = _("Workareatestgroups")
        # permissions = (("view_workareatestgroups", "Can view workareatestgroups"),)
        ordering = ["sort"]


TEST_RESULT_TYPE = (
    ("NUM", "NUMERIC"),
    ("ALF", "ALFANUMERIC"),
    ("TXT", "TEXT"),
    ("IMG", "IMAGE"),
    ("MB", "MIKROBIOLOGI"),
    ("PBS", "PERIPHERAL BLOOD SMEAR"),
)


class Tests(models.Model):
    NUMERIC = "NUM"
    ALFANUMERIC = "ALF"
    TEXT = "TXT"
    IMAGE = "IMG"
    MIKROBIOLOGI = "MB"
    test_group = models.ForeignKey(
        TestGroups,
        on_delete=models.PROTECT,
        verbose_name=_("Test Group"),
        related_name="tests",
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="children",
        on_delete=models.DO_NOTHING,
    )
    name = models.CharField(max_length=100, verbose_name=_("Test Name"), null=True)
    result_type = models.CharField(
        max_length=3,
        verbose_name=_("Result Type"),
        choices=TEST_RESULT_TYPE,
        default=NUMERIC,
    )
    specimen = models.ForeignKey(
        Specimens,
        on_delete=models.PROTECT,
        verbose_name=_("Specimen"),
        related_name="test_specimen",
        null=True,
    )
    can_request = models.BooleanField(
        verbose_name=_("Can request?"), default=True, blank=True
    )
    can_print = models.BooleanField(
        verbose_name=_("Display at report?"), default=True, blank=True
    )
    sort = models.IntegerField(verbose_name=_("Sort"), help_text=_("Sorted priority"))
    ext_code = models.CharField(
        max_length=30, verbose_name=_("External code"), null=True
    )
    dateofcreation = CreationDateTimeField(verbose_name=_("Created at"))
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("tests_detail", args=[str(self.id)])

    def __str__(self):
        return "(%s) %s" % (self.pk, self.name)

    class Meta:
        verbose_name = _("Test")
        verbose_name_plural = _("Tests")
        # permissions = (("view_tests", "Can view tests"),)
        ordering = ["test_group", "name"]


class TestPrices(models.Model):
    test = models.ForeignKey(
        Tests,
        on_delete=models.PROTECT,
        verbose_name=_("Test"),
        related_name="test_price",
    )
    priority = models.ForeignKey(
        Priority, on_delete=models.PROTECT, verbose_name=_("Priority")
    )
    tariff = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        verbose_name=_("tariff"),
        help_text=_("base tariff"),
    )
    service = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        verbose_name=_("Medc.Serv"),
        help_text=_("Medical service rate"),
    )
    dateofcreation = CreationDateTimeField(verbose_name=_("Created at"))
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("testprices_detail", args=[str(self.id)])

    def __str__(self):
        return "%s %s" % (self.test, self.priority)

    class Meta:
        # unique_together = ('test', 'priority',)
        verbose_name = _("Test price")
        verbose_name_plural = _("Test prices")
        # permissions = (("view_testprices", "Can view test prices"),)
        ordering = ["test", "priority"]


class Profile(models.Model):
    code = models.CharField(max_length=100, verbose_name=_("code"))
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    active = models.BooleanField(verbose_name=_("Active?"), default=True)
    sort = models.IntegerField(
        verbose_name=_("Sort"), help_text=_("Sorted priority"), blank=True, null=True
    )
    ext_code = models.CharField(
        max_length=30, verbose_name=_("External code"), blank=True, null=True
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

    def get_tests(self):
        txt_data = ""
        tes = ProfileTests.objects.filter(profile=self.pk).order_by("test__sort")
        for t in tes:
            txt_data = txt_data + "(" + str(t.test.id) + ") " + t.test.name + "<br>"

        return txt_data

    def __str__(self):
        return "%s - %s" % (self.code, self.name)


class ProfileTests(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        verbose_name=_("Panel"),
        related_name="paneltest_panel",
    )
    test = models.ForeignKey(
        Tests,
        on_delete=models.PROTECT,
        verbose_name=_("Test"),
        related_name="paneltest_test",
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
        return "%s - %s" % (self.profile, self.test)

    class Meta:
        verbose_name_plural = "Profile tests"
        verbose_name = "Profile tests"


class Patients(models.Model):
    patient_id = models.CharField(
        max_length=100,
        verbose_name=_("Patient ID"),
        help_text=_("Medical record number"),
        unique=True,
    )
    name = models.CharField(
        max_length=100, verbose_name=_("Name"), help_text=_("Patient Name")
    )
    gender = models.ForeignKey(
        Genders, on_delete=models.PROTECT, verbose_name=_("Gender")
    )
    dob = models.DateField(
        verbose_name=_("Date of birth"), help_text=_("Date format: YYYY-MM-DD")
    )
    address = models.CharField(
        max_length=100, verbose_name=_("Address"), help_text=_("Patient Address")
    )
    data0 = models.CharField(
        max_length=100,
        verbose_name=_("Data 0"),
        help_text=_("Additional data 0"),
        blank=True,
        null=True,
    )
    data1 = models.CharField(
        max_length=100,
        verbose_name=_("Data 1"),
        help_text=_("Additional data 1"),
        blank=True,
        null=True,
    )
    data2 = models.CharField(
        max_length=100,
        verbose_name=_("Data 2"),
        help_text=_("Additional data 3"),
        blank=True,
        null=True,
    )
    dateofcreation = CreationDateTimeField(verbose_name=_("Created at"), null=True)
    lastmodification = ModificationDateTimeField(verbose_name=_("Last modified"))
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("patient_detail", args=[str(self.id)])

    def calculate_age(self):
        today = date.today()
        return (
            today.year
            - self.dob.year
            - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    def create_order(self):
        order = Orders(patient=self)
        # order.doctor_id = 1
        # order.origin_id = 1
        # order.insurence_id = 1
        # order.priority_id = 1
        # order.lastmodifiedby_id = 1
        order.save()
        return order

    def __str__(self):
        return "%s %s" % (self.patient_id, self.name)

    class Meta:
        verbose_name = _("Patient")
        verbose_name_plural = _("Patients")
        # permissions = (("view_patients", "Can view test patients"),)
        ordering = ["patient_id", "name"]


class PatientComments(models.Model):
    patient = models.ForeignKey(
        Patients, on_delete=models.PROTECT, verbose_name=_("Patient")
    )
    internal = models.BooleanField(verbose_name=_("Internal"), default=True)
    comment = models.TextField(verbose_name=_("Comment"), blank=True, null=True)
    dateofcreation = CreationDateTimeField(
        verbose_name=_("Created at"), auto_now_add=True
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
        return "%s %s %s" % (self.patient, self.internal, self.comment)

    class Meta:
        verbose_name = _("PatientComment")
        verbose_name_plural = _("PatientComments")


ORDER_STATUS = (
    ("0", _("Pending Result")),
    ("1", _("Pending Tech. Val.")),
    ("2", _("Pending Med. Val")),
    ("3", _("Pending Print")),
    ("4", _("Completed")),
)


def auto_order_no():
    dtf = datetime.today().strftime("%y%m%d")
    par = Parameters.objects.filter(name="ORDER_NO", char_value=dtf)
    if par.count() == 0:
        Parameters.objects.filter(name="ORDER_NO").delete()
        par = Parameters(name="ORDER_NO", char_value=dtf, num_value=1)
        par.save()
    par = Parameters.objects.filter(name="ORDER_NO", char_value=dtf)
    id = par.values("id")[0]["id"]
    num_value = int(par.values("num_value")[0]["num_value"])
    par_upd = Parameters.objects.get(pk=id)
    par_upd.num_value = num_value + 1
    par_upd.save()
    return dtf + ("%04d" % (num_value,))


class Orders(models.Model):
    order_date = models.DateField(verbose_name=_("Order date"), auto_now_add=True)
    status = models.CharField(
        max_length=3,
        verbose_name=_("Status"),
        choices=ORDER_STATUS,
        default="0",
    )
    number = models.CharField(
        max_length=100,
        verbose_name=_("Number"),
        default=auto_order_no,
        blank=True,
        null=True,
        unique=True,
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        verbose_name=_("Service"),
        null=True,
        blank=True,
    )
    origin = models.ForeignKey(
        Origins,
        on_delete=models.PROTECT,
        verbose_name=_("Origin"),
        null=True,
        blank=True,
    )
    doctor = models.ForeignKey(
        Doctors,
        on_delete=models.PROTECT,
        verbose_name=_("Sender doctor"),
        null=True,
        blank=True,
    )
    diagnosis = models.ForeignKey(
        Diagnosis,
        on_delete=models.PROTECT,
        verbose_name=_("Diagnosis"),
        null=True,
        blank=True,
    )
    priority = models.ForeignKey(
        Priority,
        on_delete=models.PROTECT,
        verbose_name=_("Order priority"),
        null=True,
        blank=True,
    )
    insurance = models.ForeignKey(
        Insurance,
        on_delete=models.PROTECT,
        verbose_name=_("Insurance"),
        null=True,
        blank=True,
    )
    note = models.CharField(
        max_length=100, verbose_name=_("Note/Comment"), blank=True, null=True
    )
    patient = models.ForeignKey(
        Patients,
        on_delete=models.SET_NULL,
        verbose_name=_("Patient"),
        null=True,
        blank=True,
    )
    conclusion = models.CharField(
        max_length=1000, verbose_name=_("Conclusion"), blank=True, null=True
    )
    dateofcreation = CreationDateTimeField(
        verbose_name=_("Created at"), auto_now_add=True
    )
    ref_no = models.CharField(
        max_length=100, verbose_name=_("Ref No."), blank=True, null=True
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
    # objects = OrdersManager()

    def has_tests(self):
        if OrderTests.objects.filter(order_id=self.pk).count() > 0:
            return True
        else:
            return False

    def get_diagnosis(self):
        return ",".join(
            str(msg.diagnosis) for msg in OrderDiagnosis.objects.filter(order=self.pk)
        )

    def get_tests(self):
        return Orders.objects.filter(
            pk=self.pk, order_items__test__test_price__priority=self.priority
        ).values_list("order_items__test__name", flat=True)

    def get_test_str(self):
        order_result = Orders.objects.filter(
            pk=self.pk, order_items__test__test_price__priority=self.priority
        ).values_list("order_items__test__name", flat=False)
        data = [entry[0] for entry in order_result]
        return ", ".join(map(str, data))

    def get_test_price(self):
        return (
            Orders.objects.filter(
                pk=self.pk, order_items__test__test_price__priority=self.priority
            )
            .values(
                "order_items__test__name",
                "order_items__test__test_price__tariff",
                "order_items__test__test_price__service",
            )
            .annotate(
                sub_total=ExpressionWrapper(
                    F("order_items__test__test_price__tariff")
                    + F("order_items__test__test_price__service"),
                    output_field=DecimalField(decimal_places=2),
                )
            )
        )

    def get_total_price(self):
        return Orders.objects.filter(
            pk=self.pk, order_items__test__test_price__priority=self.priority
        ).aggregate(
            total=Sum(
                F("order_items__test__test_price__tariff")
                + F("order_items__test__test_price__service")
            )
        )

    def get_sub_total_price(self):
        return Orders.objects.filter(
            pk=self.pk, order_items__test__test_price__priority=self.priority
        ).aggregate(
            tariff_subtotal=Sum(F("order_items__test__test_price__tariff")),
            service_subtotal=Sum(F("order_items__test__test_price__service")),
        )

    def get_sub_total_price_tariff(self):
        return (
            Orders.objects.filter(
                pk=self.pk, order_items__test__test_price__priority=self.priority
            )
            .aggregate(tariff_subtotal=Sum(F("order_items__test__test_price__tariff")))
            .values()[0]
        )

    def get_sub_total_price_service(self):
        return (
            Orders.objects.filter(
                pk=self.pk, order_items__test__test_price__priority=self.priority
            )
            .aggregate(tariff_subtotal=Sum(F("order_items__test__test_price__service")))
            .values()[0]
        )

    def get_total_price_words(self):
        return num2words(int(self.get_total_price()["total"]), lang="id")

    def get_progress(self):
        ores = OrderResults.objects.filter(order=self, validation_status=0, is_header=0)
        if ores.count() > 0:
            return 0
        ores = OrderResults.objects.filter(order=self, validation_status=1, is_header=0)
        if ores.count() > 0:
            return 25
        ores = OrderResults.objects.filter(order=self, validation_status=2, is_header=0)
        if ores.count() > 0:
            return 50
        ores = OrderResults.objects.filter(order=self, validation_status=3, is_header=0)
        if ores.count() > 0:
            return 75
        ores = OrderResults.objects.filter(order=self, validation_status=4, is_header=0)
        if ores.count() > 0:
            return 100

    def get_absolute_url(self):
        return reverse("orders_detail", args=[str(self.id)])

    def __str__(self):
        return "%s %s" % (self.number, self.patient)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        # permissions = (("view_orders", "Can view orders"),)
        ordering = ["number", "origin"]


class OrderComments(models.Model):
    patient = models.ForeignKey(
        Orders, on_delete=models.PROTECT, verbose_name=_("Order")
    )
    internal = models.BooleanField(verbose_name=_("Internal"), default=True)
    comment = models.TextField(verbose_name=_("Comment"), blank=True, null=True)
    dateofcreation = CreationDateTimeField(
        verbose_name=_("Created at"), auto_now_add=True
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
        return "%s %s %s" % (self.patient, self.internal, self.comment)

    class Meta:
        verbose_name = _("OrderComment")
        verbose_name_plural = _("OrderComments")


class OrderTests(models.Model):
    order = models.ForeignKey(
        Orders,
        on_delete=models.PROTECT,
        verbose_name=_("Order"),
        related_name="order_items",
    )
    test = models.ForeignKey(
        Tests,
        on_delete=models.PROTECT,
        verbose_name=_("Test"),
        related_name="order_tests",
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        verbose_name=_("Profile"),
        related_name="ordertest_profile",
        null=True,
        blank=True,
    )
    price = models.DecimalField(
        decimal_places=2, max_digits=20, verbose_name=_("Price"), default=0
    )
    dateofcreation = CreationDateTimeField(
        verbose_name=_("Created at"), auto_now_add=True
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

    def get_absolute_url(self):
        return reverse("ordertests_detail", args=[str(self.id)])

    def get_price(self):
        price = (
            TestPrices.objects.filter(test=self.test, priority=self.order.priority)
            .aggregate(price=Sum(F("tariff") + F("service")))
            .values()[0]
        )
        return price

    def __str__(self):
        return "%s %s" % (self.order, self.test)

    class Meta:
        verbose_name = _("Order test")
        verbose_name_plural = _("Order tests")
        # permissions = (("view_ordertests", "Can view order tests"),)
        ordering = ["order", "test"]


class OrderDiagnosis(models.Model):
    order = models.ForeignKey(
        Orders,
        on_delete=models.PROTECT,
        verbose_name=_("Order"),
        related_name="order_diagitems",
    )
    diagnosis = models.ForeignKey(
        Diagnosis,
        on_delete=models.PROTECT,
        verbose_name=_("Diagnosis"),
        related_name="order_diagnosis",
    )
    dateofcreation = CreationDateTimeField(
        verbose_name=_("Created at"), auto_now_add=True
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

    def get_absolute_url(self):
        return reverse("ordertests_detail", args=[str(self.id)])

    def __str__(self):
        return "%s %s" % (self.order, self.diagnosis.name)

    class Meta:
        verbose_name = _("Order diagnosis")
        verbose_name_plural = _("Order diagnosis")
        # permissions = (("view_ordertests", "Can view order tests"),)
        ordering = ["order", "diagnosis"]


SAMPLE_STATUS = (
    ("0", _("Waiting")),
    ("1", _("Received")),
    ("2", _("Request new sample")),
    ("3", _("Missing")),
)


class OrderSamples(models.Model):
    order = models.ForeignKey(
        Orders,
        on_delete=models.PROTECT,
        verbose_name=_("Order"),
        related_name="sample_order",
    )
    specimen = models.ForeignKey(
        Specimens,
        on_delete=models.PROTECT,
        verbose_name=_("Specimen"),
        related_name="sample_specimen",
    )
    sample_no = models.CharField(
        max_length=100, verbose_name=_("sample id"), help_text=_("Sample id")
    )
    status = models.CharField(
        max_length=3,
        verbose_name=_("Status"),
        choices=SAMPLE_STATUS,
        default="0",
    )
    dateofcreation = CreationDateTimeField(
        verbose_name=_("Created at"), auto_now_add=True
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

    def get_absolute_url(self):
        return reverse("ordersamples_detail", args=[str(self.id)])

    def __str__(self):
        return "%s" % (self.sample_no)

    class Meta:
        verbose_name = _("Order samples")
        verbose_name_plural = _("Order samples")
        # permissions = (("view_ordersamples", "Can view order samples"),)
        ordering = ["order", "sample_no"]


class RequestNewReasons(models.Model):
    name = models.CharField(
        max_length=100, verbose_name=_("Name"), help_text=_("Request new reason")
    )
    dateofcreation = CreationDateTimeField(
        verbose_name=_("Created at"), auto_now_add=True
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
        return "%s" % (self.name)

    class Meta:
        verbose_name_plural = "Request new reasons"
        verbose_name = "Request new reasons"


class OrderSampleLogs(models.Model):
    order_sample = models.ForeignKey(
        OrderSamples,
        on_delete=models.PROTECT,
        verbose_name=_("Order sample"),
        related_name="order_sample_log",
    )
    status = models.CharField(
        max_length=3,
        verbose_name=_("Status"),
        choices=SAMPLE_STATUS,
        default="0",
    )
    note = models.TextField("note", null=True, blank=True)
    request_new = models.ForeignKey(
        RequestNewReasons,
        on_delete=models.PROTECT,
        verbose_name=_("Request new"),
        related_name="request_new",
        null=True,
        blank=True,
    )
    dateofcreation = CreationDateTimeField(
        verbose_name=_("Created at"), auto_now_add=True
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
        return "%s %s %s" % (self.order_sample, self.status, self.note)


class LabelPrinters(models.Model):
    name = models.CharField(
        max_length=100, verbose_name=_("Name"), help_text=_("Printer barcode name")
    )
    active = models.BooleanField(default=True, verbose_name=_("is active?"))
    com_port = models.CharField(
        max_length=100,
        verbose_name=_("Com serial port name"),
        help_text=_("eq: COM10,COM11"),
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

    def get_absolute_url(self):
        return reverse("ordersamples_detail", args=[str(self.id)])

    def __str__(self):
        return "%s (%s)" % (self.name, self.com_port)


#### Lab Model #########
#######################
class ReceivedSamples(models.Model):
    order = models.ForeignKey(
        Orders,
        on_delete=models.PROTECT,
        verbose_name=_("Order"),
        related_name="receivedsamples_order",
    )
    sample = models.ForeignKey(
        OrderSamples,
        on_delete=models.PROTECT,
        verbose_name=_("Specimen"),
        related_name="receivedsamples_tube",
    )
    supergroup = models.ForeignKey(
        SuperGroups,
        on_delete=models.PROTECT,
        verbose_name=_("Super Group"),
        related_name="receivedsamples_supergrup",
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
        return "%s%s" % (self.order.number, self.suffix)


CONN_TYPE = (("SER", "Serial"), ("TCP", "TCP/IP"))
SER_PORT = (
    ("COM1", "COM1"),
    ("COM2", "COM2"),
    ("COM3", "COM3"),
    ("COM4", "COM4"),
    ("COM5", "COM5"),
    ("COM6", "COM6"),
    ("COM7", "COM7"),
    ("COM8", "COM8"),
    ("COM9", "COM9"),
    ("COM10", "COM10"),
    ("COM11", "COM11"),
    ("COM12", "COM12"),
    ("COM13", "COM13"),
    ("COM14", "COM14"),
    ("COM15", "COM15"),
    ("COM16", "COM16"),
    ("COM17", "COM17"),
    ("COM18", "COM18"),
    ("COM19", "COM19"),
    ("COM20", "COM20"),
    ("COM21", "COM21"),
    ("COM22", "COM22"),
    ("COM23", "COM23"),
    ("COM24", "COM24"),
    ("COM25", "COM25"),
    ("COM26", "COM26"),
    ("COM27", "COM27"),
    ("COM28", "COM28"),
    ("COM29", "COM29"),
    ("COM30", "COM30"),
    ("COM31", "COM31"),
    ("COM32", "COM32"),
    ("COM33", "COM33"),
    ("COM34", "COM34"),
    ("COM35", "COM35"),
    ("COM36", "COM36"),
    ("COM37", "COM37"),
    ("COM38", "COM38"),
    ("COM39", "COM39"),
    ("COM40", "COM40"),
)
SER_BAUDRATE = (("9600", "9600"), ("19200", "19200"))
SER_DATABIT = (("7", "7"), ("8", "8"))
SER_STOPBIT = (("1", "1"), ("2", "2"))
SER_PARITY = (("N", "None"), ("E", "Even"))
TCP_TYPE = (("S", "Server"), ("C", "Client"))


class Instruments(models.Model):
    code = models.CharField(max_length=10, verbose_name=_("Code"), unique=True)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    active = models.BooleanField(
        verbose_name=_("Batch mode?"), default=False, blank=True
    )
    batch_mode = models.BooleanField(
        verbose_name=_("Active?"), default=True, blank=True
    )
    driver = models.CharField(
        max_length=100, verbose_name=_("Driver name"), blank=True, null=True
    )
    receive_ref_ranges = models.BooleanField(
        verbose_name=_("Receive refranges from instrument"), default=True, blank=True
    )
    connection_type = models.CharField(
        max_length=3,
        verbose_name=_("Connection type"),
        choices=CONN_TYPE,
        null=True,
        blank=True,
    )
    serial_port = models.CharField(
        max_length=5,
        verbose_name=_("Serial port name"),
        choices=SER_PORT,
        null=True,
        blank=True,
    )
    serial_baud_rate = models.CharField(
        max_length=10,
        verbose_name=_("Serial baud rate"),
        choices=SER_BAUDRATE,
        null=True,
        blank=True,
    )
    serial_data_bit = models.CharField(
        max_length=1,
        verbose_name=_("Serial data bit"),
        choices=SER_DATABIT,
        null=True,
        blank=True,
    )
    serial_stop_bit = models.CharField(
        max_length=3,
        verbose_name=_("Serial stop bit"),
        choices=SER_STOPBIT,
        null=True,
        blank=True,
    )
    serial_parity = models.CharField(
        max_length=3,
        verbose_name=_("Serial parity"),
        choices=SER_PARITY,
        null=True,
        blank=True,
    )
    tcp_conn_type = models.CharField(
        max_length=3,
        verbose_name=_("TCP/IP Connection type"),
        choices=TCP_TYPE,
        null=True,
        blank=True,
    )
    tcp_host = models.GenericIPAddressField(
        verbose_name=_("TCP Host name (IP Address)"), blank=True, null=True
    )
    tcp_port = models.IntegerField(verbose_name=_("TCP Port"), blank=True, null=True)
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
        return "%s" % (self.name)


REST_INST_TYPE = (("R", "RAW"), ("N", "NUMBERIC"), ("A", "ALFANUMERIC"))
REST_SELECT = (("1", "Result 1"), ("2", "Result 2"), ("3", "Result 3"))


class InstrumentTests(models.Model):
    instrument = models.ForeignKey(
        Instruments,
        on_delete=models.PROTECT,
        verbose_name=_("Instrument"),
        related_name="instrumentflags_instrument",
    )
    test = models.ForeignKey(
        Tests,
        on_delete=models.PROTECT,
        verbose_name=_("Test"),
        related_name="instrumentflags_test",
    )
    test_code = models.CharField(max_length=100, verbose_name=_("Host test code"))
    result_type = models.CharField(
        max_length=3,
        verbose_name=_("Result type"),
        choices=REST_INST_TYPE,
        default="R",
    )
    result_selection = models.CharField(
        max_length=3,
        verbose_name=_("Result selection"),
        choices=REST_SELECT,
        default="1",
    )
    sql_script = models.TextField(verbose_name=_("SQL Script"), null=True, blank=True)
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
        return "%s %s" % (self.instrument, self.test)

    class Meta:
        verbose_name_plural = "Instrument tests"
        verbose_name = "Instrment tests"


class InstrumentFlags(models.Model):
    instrument = models.ForeignKey(
        Instruments,
        on_delete=models.PROTECT,
        verbose_name=_("Instrument"),
        related_name="instrumenttests_instrument",
    )
    flag_code = models.CharField(max_length=100, verbose_name=_("Host flag code"))
    flag_description = models.CharField(
        max_length=100, verbose_name=_("Host flag description")
    )
    flag_mark = models.CharField(
        max_length=100, verbose_name=_("Host flag mark"), null=True, blank=True
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

    class Meta:
        verbose_name_plural = "Instrument flags"
        verbose_name = "Instrment flags"

    def __str__(self):
        return "%s %s" % (self.instrument, self.flag_code)


BATCH_STATUS = (
    ("0", "New"),
    ("1", "Sent"),
    ("2", "Process"),
    ("3", "Complete"),
)


class InstrumentBatch(models.Model):
    order_sample = models.ForeignKey(
        OrderSamples,
        on_delete=models.PROTECT,
        verbose_name=_("Order sample"),
        related_name="instrumentbatch_ordersample",
    )
    instrument = models.ForeignKey(
        Instruments,
        on_delete=models.PROTECT,
        verbose_name=_("Instrument"),
        related_name="instrumentbatch_instrument",
    )
    status = models.CharField(
        max_length=3,
        verbose_name=_("Batch status"),
        choices=BATCH_STATUS,
        default="0",
    )
    note = models.CharField(
        verbose_name=_("Note"), max_length=100, null=True, blank=True
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
        return "%s %s" % (self.order_sample, self.instrument)


AGE_UNIT = (("D", "DAY"), ("M", "MONTH"), ("Y", "YEAR"))
REF_OPERATOR = (
    ("-", "NA"),
    (">", "GT"),
    (">=", "GTE"),
    ("<", "LT"),
    ("<=", "LTE"),
)


class TestRefRanges(models.Model):
    DAY = "D"
    MONTH = "M"
    YEAR = "Y"
    NA = "-"
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    test = models.ForeignKey(
        Tests,
        on_delete=models.PROTECT,
        verbose_name=_("Test"),
        related_name="refranges_test",
    )
    gender = models.ForeignKey(
        Genders,
        on_delete=models.PROTECT,
        verbose_name=_("Gender"),
        related_name="refranges_gender",
        blank=True,
        null=True,
    )
    age_from = models.IntegerField(verbose_name=_("Age from"), null=True, blank=True)
    age_from_type = models.CharField(
        max_length=3,
        verbose_name=_("Age from unit"),
        choices=AGE_UNIT,
        null=True,
        blank=True,
    )
    age_to = models.IntegerField(verbose_name=_("Age to"), null=True, blank=True)
    age_to_type = models.CharField(
        max_length=3,
        verbose_name=_("Age to unit"),
        choices=AGE_UNIT,
        null=True,
        blank=True,
    )
    operator = models.CharField(
        max_length=3,
        verbose_name=_("Operator"),
        choices=REF_OPERATOR,
        null=True,
        blank=True,
    )
    any_age = models.BooleanField(verbose_name=_("Any age?"), default=True, blank=True)
    lower = models.FloatField(verbose_name=_("lower limit"), null=True, blank=True)
    upper = models.FloatField(verbose_name=_("upper limit"), null=True, blank=True)
    panic_lower = models.FloatField(
        verbose_name=_("panic lower limit"), null=True, blank=True
    )
    panic_upper = models.FloatField(
        verbose_name=_("panic upper limit"), null=True, blank=True
    )
    operator_value = models.FloatField(
        verbose_name=_("operator value"), null=True, blank=True
    )
    alfa_value = models.CharField(
        max_length=100, verbose_name=_("Alfanumberic value"), null=True, blank=True
    )
    special_info = models.TextField(
        verbose_name=_("Special information"), null=True, blank=True
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
        return "%s" % (self.test)

    class Meta:
        verbose_name_plural = "Test ref ranges"
        verbose_name = "Test ref ranges"


class Results(models.Model):
    type = models.CharField(default="R", max_length=1)  # R: Result , Q: QC
    order = models.ForeignKey(
        Orders,
        on_delete=models.PROTECT,
        verbose_name=_("Order"),
        related_name="results_order",
        null=True,
        blank=True,
    )
    test = models.ForeignKey(
        Tests,
        on_delete=models.PROTECT,
        verbose_name=_("Test"),
        related_name="results_test",
    )
    numeric_result = models.FloatField(
        verbose_name=_("Numeric result"), null=True, blank=True
    )
    alfa_result = models.CharField(
        max_length=100, verbose_name=_("Alfanumeric result"), null=True
    )
    text_result = models.TextField(verbose_name=_("Text result"), null=True)
    image_result = models.BinaryField(verbose_name=_("Image result"), null=True)
    ref_range = models.CharField(
        max_length=100, verbose_name=_("Reference range"), null=True
    )
    mark = models.CharField(max_length=3, verbose_name=_("Result mark"), null=True)
    instrument = models.ForeignKey(
        Instruments,
        on_delete=models.PROTECT,
        verbose_name=_("Instrument"),
        related_name="results_instrument",
        null=True,
    )
    flag = models.ForeignKey(
        InstrumentFlags,
        on_delete=models.PROTECT,
        verbose_name=_("Instrument flag"),
        related_name="results_instrumentflag",
        null=True,
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

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def get_patient_age_in_day(self):
        return (self.order.order_date - self.order.patient.dob).days

    def setup_range(
        self,
        alfa_value=None,
        operator=None,
        operator_value=None,
        lower=None,
        upper=None,
        panic_lower=None,
        panic_upper=None,
    ):
        if self.alfa_result:
            if alfa_value:
                # print 'ALFA VALUE'
                self.ref_range = alfa_value
                if self.alfa_result != str(alfa_value):
                    self.mark = "A"
            else:
                # numeric range
                # print 'NUMERIC'
                if operator:
                    # print 'OPERATOR'
                    if (
                        self.test.testparameteters_test.decimal_place
                        or self.test.testparameteters_test.decimal_place == 0
                    ):
                        # print 'ADA decimal place'
                        # print self.test.testparameteters_test.decimal_place
                        str_f = (
                            "%."
                            + str(self.test.testparameteters_test.decimal_place)
                            + "f"
                        )
                        if int(self.test.testparameteters_test.decimal_place) == 0:
                            operator_value = str(int(operator_value))
                            if self.is_number(self.alfa_result):
                                self.alfa_result = int(round(float(self.alfa_result)))
                        else:
                            # print str_f
                            operator_value = str_f % round(
                                float(operator_value),
                                int(self.test.testparameteters_test.decimal_place),
                            )
                            if self.is_number(self.alfa_result):
                                self.alfa_result = str_f % round(
                                    float(self.alfa_result),
                                    int(self.test.testparameteters_test.decimal_place),
                                )

                    self.ref_range = str(operator) + " " + str(operator_value)
                    if (
                        self.is_number(self.alfa_result)
                        and str(self.alfa_result).strip() != ""
                    ):
                        # GT
                        try:
                            if str(operator) == ">":
                                if float(self.alfa_result) <= float(operator_value):
                                    self.mark = "L"
                            if str(operator) == ">=":
                                if float(self.alfa_result) < float(operator_value):
                                    self.mark = "L"
                            if str(operator) == "<":
                                if float(self.alfa_result) >= float(operator_value):
                                    self.mark = "H"
                            if str(operator) == "<=":
                                if float(self.alfa_result) > float(operator_value):
                                    self.mark = "H"
                        except Exception as e:
                            print("Error set mark [%s]" % str(e))
                            self.mark = ""
                else:
                    # range
                    # print 'decimal:' + str(self.test.testparameteters_test.decimal_place)
                    if (
                        self.test.testparameteters_test.decimal_place
                        or self.test.testparameteters_test.decimal_place == 0
                    ):
                        # print 'ADA decimal place'
                        # print self.test.testparameteters_test.decimal_place
                        # print True
                        str_f = (
                            "%."
                            + str(self.test.testparameteters_test.decimal_place)
                            + "f"
                        )
                        if int(self.test.testparameteters_test.decimal_place) == 0:
                            str_low = str(int(lower))
                            str_up = str(int(upper))
                            if self.is_number(self.alfa_result):
                                self.alfa_result = int(round(float(self.alfa_result)))
                        else:
                            # print str_f
                            str_low = str_f % round(
                                float(lower),
                                int(self.test.testparameteters_test.decimal_place),
                            )
                            # print str_low
                            str_up = str_f % round(
                                float(upper),
                                int(self.test.testparameteters_test.decimal_place),
                            )
                            # print str_up
                            self.ref_range = str(str_low) + " - " + str(str_up)
                            # print self.ref_range
                            try:
                                self.alfa_result = float(
                                    str_f
                                    % round(
                                        float(self.alfa_result),
                                        int(
                                            self.test.testparameteters_test.decimal_place
                                        ),
                                    )
                                )
                            except Exception as e:
                                print("Failed when round alfa_result [%s]" % str(e))

                        lower = str_low
                        upper = str_up

                    self.ref_range = str(lower) + " - " + str(upper)

                    # print 'low ['+str_low+'] up['+str_up+']'
                    if self.alfa_result:
                        # print 'RANGE_ALFA_RESULT'
                        if self.is_number(str(self.alfa_result)):
                            try:
                                if float(self.alfa_result) < float(lower):
                                    # print 'MARK L'
                                    self.mark = "L"
                                if float(self.alfa_result) > float(upper):
                                    # print 'MARK H'
                                    self.mark = "H"

                                # PANIC CALCULATION
                                if panic_lower and panic_upper:
                                    if float(self.alfa_result) < float(panic_lower):
                                        self.mark = "LL"
                                    if float(self.alfa_result) > float(panic_upper):
                                        self.mark = "HH"
                            except Exception as e:
                                print("Failed when set flag [%s]" % str(e))
                        else:
                            self.mark = "A"

    def save(self, *args, **kwargs):
        refrange = TestRefRanges.objects.filter(test=self.test).values(
            "any_age",
            "gender",
            "age_from_type",
            "age_from",
            "age_to",
            "operator",
            "operator_value",
            "lower",
            "upper",
            "alfa_value",
            "special_info",
            "gender_id",
            "panic_lower",
            "panic_upper",
        )
        if refrange.count() > 0:
            for range in refrange:
                # any age & any gender
                if range["any_age"]:
                    # check gender
                    if not range["gender"]:
                        self.setup_range(
                            alfa_value=range["alfa_value"],
                            operator=range["operator"],
                            operator_value=range["operator_value"],
                            lower=range["lower"],
                            upper=range["upper"],
                            panic_lower=range["panic_lower"],
                            panic_upper=range["panic_upper"],
                        )

                    else:
                        # gender set
                        if range["gender"] == self.order.patient.gender_id:
                            self.setup_range(
                                alfa_value=range["alfa_value"],
                                operator=range["operator"],
                                operator_value=range["operator_value"],
                                lower=range["lower"],
                                upper=range["upper"],
                                panic_lower=range["panic_lower"],
                                panic_upper=range["panic_upper"],
                            )
                else:
                    # date range
                    # Days
                    if range["age_from_type"] == "D":
                        # print str((self.order.order_date - self.order.patient.dob).days)
                        if (
                            int(range["age_from"])
                            <= relativedelta(
                                self.order.order_date - self.order.patient.dob
                            ).days
                            <= int(range["age_to"])
                        ):
                            if (not range["gender"]) or (
                                range["gender"] == self.order.patient.gender_id
                            ):
                                self.setup_range(
                                    alfa_value=range["alfa_value"],
                                    operator=range["operator"],
                                    operator_value=range["operator_value"],
                                    lower=range["lower"],
                                    upper=range["upper"],
                                    panic_lower=range["panic_lower"],
                                    panic_upper=range["panic_upper"],
                                )
                    # Months
                    if range["age_from_type"] == "M":
                        if (
                            int(range["age_from"])
                            <= relativedelta(
                                self.order.order_date - self.order.patient.dob
                            ).months
                            <= int(range["age_to"])
                        ):
                            if (not range["gender"]) or (
                                range["gender"] == self.order.patient.gender_id
                            ):
                                self.setup_range(
                                    alfa_value=range["alfa_value"],
                                    operator=range["operator"],
                                    operator_value=range["operator_value"],
                                    lower=range["lower"],
                                    upper=range["upper"],
                                    panic_lower=range["panic_lower"],
                                    panic_upper=range["panic_upper"],
                                )
                    # Years
                    if range["age_from_type"] == "Y":
                        if (
                            int(range["age_from"])
                            <= relativedelta(
                                self.order.order_date - self.order.patient.dob
                            ).years
                            <= int(range["age_to"])
                        ):
                            if (not range["gender"]) or (
                                range["gender"] == self.order.patient.gender_id
                            ):
                                self.setup_range(
                                    alfa_value=range["alfa_value"],
                                    operator=range["operator"],
                                    operator_value=range["operator_value"],
                                    lower=range["lower"],
                                    upper=range["upper"],
                                    panic_lower=range["panic_lower"],
                                    panic_upper=range["panic_upper"],
                                )

                # print range

        super(Results, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s %s %s" % (
            self.order,
            self.numeric_result,
            self.alfa_result,
            self.text_result,
        )

    class Meta:
        verbose_name_plural = "Results"
        verbose_name = "Results"


class ResultComments(models.Model):
    patient = models.ForeignKey(
        Results, on_delete=models.PROTECT, verbose_name=_("Result")
    )
    internal = models.BooleanField(verbose_name=_("Internal"), default=True)
    comment = models.TextField(verbose_name=_("Comment"), blank=True, null=True)
    dateofcreation = CreationDateTimeField(
        verbose_name=_("Created at"), auto_now_add=True
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
        return "%s %s %s" % (self.patient, self.internal, self.comment)

    class Meta:
        verbose_name = _("ResultComment")
        verbose_name_plural = _("ResultComments")


class ResultFlags(models.Model):
    result = models.ForeignKey(
        Results,
        on_delete=models.PROTECT,
        verbose_name=_("Result"),
        related_name="resultflags_result",
    )
    instrument_flag = models.ForeignKey(
        InstrumentFlags,
        on_delete=models.PROTECT,
        verbose_name=_("Result"),
        related_name="resultflags_instrumentflag",
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
        return "%s - %s" % (self.result, self.instrument_flag)


class TestParameters(models.Model):
    test = models.OneToOneField(
        Tests,
        on_delete=models.PROTECT,
        primary_key=True,
        related_name="testparameteters_test",
    )
    method = models.CharField(
        max_length=100, verbose_name=_("Method"), null=True, blank=True
    )
    unit = models.CharField(
        max_length=100, verbose_name=_("Test unit"), null=True, blank=True
    )
    decimal_place = models.IntegerField(verbose_name=_("* place"), null=True, default=1)
    special_information = models.CharField(
        max_length=1000, verbose_name=_("Special information"), null=True, blank=True
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

    class Meta:
        verbose_name_plural = "Test parameters"
        verbose_name = "Test parameters"

    def __str__(self):
        return "%s" % (self.test)


class OrderResults(models.Model):
    order = models.ForeignKey(
        Orders,
        on_delete=models.PROTECT,
        verbose_name=_("Order"),
        related_name="orderresults_order",
    )
    sample = models.ForeignKey(
        OrderSamples,
        on_delete=models.PROTECT,
        verbose_name=_("Order Sample"),
        related_name="sampleresults_order",
        null=True,
    )
    test = models.ForeignKey(
        Tests,
        on_delete=models.PROTECT,
        verbose_name=_("Test"),
        related_name="orderresults_test",
        null=True,
    )
    is_header = models.BooleanField(default=False, verbose_name=_("is header?"))
    result = models.ForeignKey(
        Results,
        on_delete=models.PROTECT,
        verbose_name=_("Result"),
        related_name="orderresults_result",
        null=True,
    )
    unit = models.CharField(max_length=100, verbose_name=_("Result unit"), null=True)
    ref_range = models.CharField(
        max_length=200, verbose_name=_("Reference range"), null=True
    )
    patologi_mark = models.CharField(
        max_length=20, verbose_name=_("Patologi mark"), null=True
    )
    validation_status = models.IntegerField(
        verbose_name=_("Validation status"), default=0
    )
    techval_user = models.CharField(
        max_length=20, verbose_name=_("Techical validated by"), null=True
    )
    techval_date = models.DateTimeField(
        verbose_name=_("Technical Validated date"), null=True
    )
    medval_user = models.CharField(
        max_length=20, verbose_name=_("Medical validated by"), null=True
    )
    medval_date = models.DateTimeField(
        verbose_name=_("Medical validated date"), null=True
    )
    print_status = models.IntegerField(verbose_name=_("Print status"), default=0)
    print_user = models.CharField(max_length=20, verbose_name=_("Print by"), null=True)
    print_date = models.DateTimeField(verbose_name=_("Print date"), null=True)
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
        return "%s %s %s %s %s" % (
            self.order,
            self.test,
            self.result,
            self.ref_range,
            self.patologi_mark,
        )

    def previous_result(self):
        return "xxx"

    class Meta:
        unique_together = (
            "order",
            "test",
        )
        permissions = (
            ("techval", "Technical validating results"),
            ("medval", "Medical validating result"),
            ("repeat", "Repeating result"),
        )
        verbose_name_plural = "Result"
        verbose_name = "Result"


class HistoryOrders(models.Model):
    order = models.ForeignKey(
        Orders,
        on_delete=models.PROTECT,
        verbose_name=_("Order"),
        related_name="historyorder_order",
    )
    test = models.ForeignKey(
        Tests,
        on_delete=models.PROTECT,
        verbose_name=_("Test"),
        related_name="historyorder_test",
        null=True,
    )
    action_code = models.CharField(
        max_length=20, verbose_name=_("Action code"), null=True
    )
    action_user = models.CharField(
        max_length=20, verbose_name=_("Action by"), null=True
    )
    action_date = models.DateTimeField(verbose_name=_("Action date"), null=True)
    action_text = models.CharField(
        max_length=1000, verbose_name=_("Action text"), null=True
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
        return "%s %s %s" % (self.order, self.test, self.action_text)


class OrderExtended(models.Model):
    order = models.OneToOneField(
        Orders,
        on_delete=models.PROTECT,
        primary_key=True,
    )
    result_pdf_url = models.CharField(
        max_length=500, verbose_name=_("Result PDF url"), null=True
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

    def get_progress(self):
        # ores = OrderResults.objects.filter(order=self.order,validation_status=0,is_header=0)
        return int(self.order.status) * 25
        # if order.status == 1:
        #    return 0
        # ores = OrderResults.objects.filter(order=self.order,validation_status=1,is_header=0)
        # if ores.count()>0:
        #    return 25
        # ores = OrderResults.objects.filter(order=self.order,validation_status=2,is_header=0)
        # if ores.count()>0:
        #    return 50
        # ores = OrderResults.objects.filter(order=self.order,validation_status=3,is_header=0)
        # if ores.count()>0:
        #    return 75
        # ores = OrderResults.objects.filter(order=self.order,validation_status=4,is_header=0)
        # if ores.count()>0:
        #    return 100

    def __str__(self):
        return "%s" % (self.order)


class BatchGroups(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))

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
        return "%s" % (self.name)

    class Meta:
        verbose_name_plural = "Batch groups"
        verbose_name = "Batch groups"


class BatchGroupTests(models.Model):
    batch_group = models.ForeignKey(
        BatchGroups,
        on_delete=models.PROTECT,
        verbose_name=_("Batch group"),
        related_name="batchtest_batchgroup",
    )
    test = models.ForeignKey(
        Tests,
        on_delete=models.PROTECT,
        verbose_name=_("Test"),
        related_name="batchgroup_test",
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
        return "%s - %s" % (self.batch_group, self.test)


class Worklists(models.Model):
    batch_date = models.DateField(verbose_name=_("Batch date"), auto_now_add=True)
    batch_group = models.ForeignKey(
        BatchGroups,
        on_delete=models.PROTECT,
        verbose_name=_("Batch group"),
        related_name="worklist_batchgroup",
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

    def get_absolute_url(self):
        return reverse("worklists_detail", args=[str(self.id)])

    def __str__(self):
        return "%s - %s" % (self.batch_date, self.batch_group)


class WorklistOrders(models.Model):
    worklist = models.ForeignKey(
        Worklists,
        on_delete=models.PROTECT,
        verbose_name=_("Worklist"),
        related_name="worklist_order",
    )
    order = models.ForeignKey(
        Orders,
        on_delete=models.PROTECT,
        verbose_name=_("Order"),
        related_name="worklistorder_order",
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


class WorklistTests(models.Model):
    worklistorder = models.ForeignKey(
        WorklistOrders,
        on_delete=models.PROTECT,
        verbose_name=_("Worklist order"),
        related_name="worklisttest_worklistorder",
    )
    test = models.ForeignKey(
        Tests,
        on_delete=models.PROTECT,
        verbose_name=_("Test"),
        related_name="worklisttest_test",
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
        return "%s - %s - %s" % (self.worklist, self.order, self.test)


class Hosts(models.Model):
    code = models.CharField(max_length=10, verbose_name=_("Code"), unique=True)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    input_path = models.CharField(max_length=100, verbose_name=_("input path"))

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


LABEL_SCOPE = (
    ("O", "ORDER"),
    ("S", "SAMPEL"),
)


class Labels(models.Model):
    scope = models.CharField(
        max_length=3,
        verbose_name=_("Label scope"),
        choices=LABEL_SCOPE,
        default="S",
    )
    zpl_code = models.TextField(
        verbose_name=_(
            "ZPL code, to change field bracket != with field, example order_no put string <order_no>, patient_id put string <patient_id> and so on. supported field order_no,patient_id,patient_name.."
        )
    )
    number = models.IntegerField(verbose_name=_("Number of copies label"))
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
        return "%s - %s" % (self.scope, self.number)


###
class Menus(models.Model):
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="menu_parent",
        on_delete=models.DO_NOTHING,
    )
    name = models.CharField(
        max_length=100, verbose_name=_("Test Name"), null=True, unique=True
    )
    class_name = models.CharField(
        max_length=100, verbose_name=_("Class name"), blank=True, null=True
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
        return "%s - %s" % (self.parent, self.name)


### user workarea filter saving here
class UserWorkareaFilter(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_("User"),
        related_name="userworkareafilter_user",
    )
    workarea = models.ForeignKey(
        Workarea,
        on_delete=models.PROTECT,
        verbose_name=_("Workarea"),
        related_name="userworkareafilter_workarea",
    )
    name = models.CharField(
        max_length=100, verbose_name=_("Name"), blank=True, null=True
    )
    filter_set = models.CharField(
        max_length=500, verbose_name=_("Filter set"), blank=True, null=True
    )
    default = models.BooleanField(verbose_name=_("Default"), default=True, blank=True)

    lastmodification = ModificationDateTimeField(
        verbose_name=_("Last modified"), null=True
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
        return "%s - %s - %s" % (self.user, self.workarea, self.name)


class QualityControl(models.Model):
    instrument = models.ForeignKey(Instruments, on_delete=models.DO_NOTHING)
    instrument_test = models.ForeignKey(InstrumentTests, on_delete=models.DO_NOTHING)
    result = models.ForeignKey(
        Results,
        on_delete=models.PROTECT,
        verbose_name=_("Result"),
        related_name="quality_control_result",
        null=True,
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
        return "%s - %s: %s" % (self.instrument, self.instrument_test, self.result)


#################################### MIKROBIOLOGI #######################
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


################# BANK DARAH ##########################


class BDGrupJenisDarah(models.Model):
    code = models.CharField(max_length=100, verbose_name=_("code"))
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
        return "%s - %s" % (self.name, self.name)

    class Meta:
        verbose_name_plural = "Bd grup jenis darah"
        verbose_name = "Bd grup jenis darah"


class BDJenisDarah(models.Model):
    group = models.ForeignKey(
        BDGrupJenisDarah,
        on_delete=models.PROTECT,
        verbose_name=_("Group"),
        related_name="bdjenisdarah_bdgrupjenisdarah",
    )
    code = models.CharField(max_length=100, verbose_name=_("code"))
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    unit = models.CharField(max_length=100, verbose_name=_("Unit"))
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
        return "%s - %s" % (self.name, self.unit)

    class Meta:
        verbose_name_plural = "Bd jenis darah"
        verbose_name = "Bd jenis darah"


BD_BLOOD_TYPE = (("A", "A"), ("B", "B"), ("O", "O"), ("AB", "AB"))
BD_BLOOD_RHESUS = (
    ("+", "+"),
    ("-", "-"),
)


class BDPermintaanDarahHeader(models.Model):
    organization = models.ForeignKey(
        Organizations,
        on_delete=models.PROTECT,
        verbose_name=_("Organization"),
        related_name="bdpermintaanbankdarahheader_organization",
    )
    priority = models.ForeignKey(
        Priority,
        on_delete=models.PROTECT,
        verbose_name=_("Priority"),
        related_name="bdpermintaanbankdarahheader_priority",
    )
    origin = models.ForeignKey(
        Origins,
        on_delete=models.PROTECT,
        verbose_name=_("Origin"),
        related_name="bdpermintaanbankdarahheader_origin",
    )
    doctor = models.ForeignKey(
        Priority,
        on_delete=models.PROTECT,
        verbose_name=_("Doctor"),
        related_name="bdpermintaanbankdarahheader_doctor",
    )
    insurance = models.ForeignKey(
        Insurance,
        on_delete=models.PROTECT,
        verbose_name=_("Insurance"),
        related_name="bdpermintaanbankdarahheader_insurance",
    )
    patient = models.ForeignKey(
        Patients,
        on_delete=models.PROTECT,
        verbose_name=_("Patient"),
        related_name="bdpermintaanbankdarahheader_patient",
    )
    note_diagnosis = models.TextField(verbose_name=_("Diagnosis note"))
    note_transfusion_reason = models.TextField(verbose_name=_("Transfusion reason"))
    Hb = models.DecimalField(
        decimal_places=2, max_digits=20, verbose_name=_("Hb"), blank=True, null=True
    )
    blood_type = models.CharField(
        max_length=3,
        verbose_name=_("blood type"),
        choices=BD_BLOOD_TYPE,
        blank=True,
    )
    blood_rhesus = models.CharField(
        max_length=3,
        verbose_name=_("blood rhesus"),
        choices=BD_BLOOD_RHESUS,
        blank=True,
    )
    pervious_transfusion = models.BooleanField(
        verbose_name=_("Pervious transfusion"), default=False
    )
    pervious_transfusion_date = models.DateField(
        verbose_name=_("Pervious transfusion date"), blank=True, null=True
    )
    pervious_transfusion_effect = models.BooleanField(
        verbose_name=_("Pervious transfusion effect"), default=False
    )
    pervious_transfusion_effect_desc = models.TextField(
        verbose_name=_("Pervious transfusion effect description"), blank=True, null=True
    )
    coombs_test = models.BooleanField(verbose_name=_("Coombs test"), default=False)
    coombs_test_location = models.TextField(
        verbose_name=_("Coombs test location"), null=True, blank=True
    )
    coombs_test_date = models.DateField(
        verbose_name=_("Coombs test date"), null=True, blank=True
    )
    coombs_test_result = models.TextField(
        verbose_name=_("Coombs test result"), null=True, blank=True
    )
    condition_women_pregnancy_count = models.TextField(
        verbose_name=_("Condition women pregnancy count"), blank=True, null=True
    )
    condition_women_abortus = models.TextField(
        verbose_name=_("Condition woman abortus?"), blank=True, null=True
    )
    condition_women_neonatus_hemolitic = models.TextField(
        verbose_name=_("Condition women neonatus hemolitic"), blank=True, null=True
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
        return "%s - %s" % (self.organization, self.patient)


class BDPermintaanDarahDetail(models.Model):
    bd_permintaan_darah_header = models.ForeignKey(
        BDPermintaanDarahHeader,
        on_delete=models.PROTECT,
        verbose_name=_("Permintaan darah header"),
        related_name="bdpermintaanbankdarahdetail_bdpermintaanbankdarahheader",
    )
    bd_jenis_darah = models.ForeignKey(
        BDJenisDarah,
        on_delete=models.PROTECT,
        verbose_name=_("Permintaan jenis darah"),
        related_name="bdpermintaanbankdarahdetail_bdjenisdarah",
    )
    quantity = models.DecimalField(
        decimal_places=2, max_digits=20, verbose_name=_("Quantity")
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
        return "%s - %s" % (self.bd_permintaan_darah_header, self.bd_jenis_darah)


class BDDarahMasuk(models.Model):
    in_date = models.DateField(verbose_name=_("In date"), auto_now_add=True)
    nomor_kantong = models.CharField(
        max_length=50, verbose_name=_("Nomor kantong"), unique=True
    )
    bd_jenis_darah = models.ForeignKey(
        BDJenisDarah,
        on_delete=models.PROTECT,
        verbose_name=_("Jenis darah"),
        related_name="bddarahmasuk_bdjenisdarah",
    )
    # quantity = models.DecimalField(decimal_places=2, max_digits=20,verbose_name=_("Quantity (cc)"))
    blood_type = models.CharField(
        max_length=3,
        verbose_name=_("blood type"),
        choices=BD_BLOOD_TYPE,
        blank=True,
    )
    blood_rhesus = models.CharField(
        max_length=3,
        verbose_name=_("blood rhesus"),
        choices=BD_BLOOD_RHESUS,
        blank=True,
    )
    aftap_date = models.DateField(verbose_name=_("Aftap date"), blank=True, null=True)
    process_date = models.DateField(
        verbose_name=_("Process date"), blank=True, null=True
    )
    expired_date = models.DateField(
        verbose_name=_("Expired date"), blank=True, null=True
    )
    note = models.TextField(verbose_name=_("Note"), blank=True, null=True)

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
        return "%s - %s" % (self.bd_permintaan_darah_header, self.bd_jenis_darah)


################### INVENTORY ################################
class Location(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Vendor(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Vendor name"))
    address = models.CharField(
        max_length=200, verbose_name=_("Address"), blank=True, null=True
    )
    country = models.CharField(
        max_length=200, verbose_name=_("Country"), blank=True, null=True
    )
    rep = models.CharField(max_length=45, blank=True, null=True)
    rep_phone = models.CharField(max_length=16, blank=True, null=True)
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("vendor_detail", args=[str(self.id)])

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Vendor")
        verbose_name_plural = _("Vendors")
        # permissions = (("view_vendor", "Can view vendors"),)


class Supplier(models.Model):
    name = models.CharField(max_length=64)
    rep = models.CharField(
        max_length=45, blank=True, null=True, help_text=_("contact person name")
    )
    rep_phone = models.CharField(
        max_length=16, blank=True, null=True, help_text=_("contact telp")
    )
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True, auto_now_add=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("supplier_detail", args=[str(self.id)])

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")
        # permissions = (("view_supplier", "Can view suppliers"),)


class TemperatureCondition(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class ProductGroup(models.Model):
    name = models.CharField(
        max_length=30, help_text=_("Product group name"), blank=True, null=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return "%s" % (self.name)


class Product(models.Model):
    number = models.CharField(
        max_length=30, help_text=_("Product number"), blank=True, null=True
    )
    name = models.CharField(max_length=200, help_text=_("Product name"), null=True)
    group = models.ForeignKey(
        ProductGroup, on_delete=models.PROTECT, null=True, related_name="product_group"
    )
    item_number = models.CharField(
        max_length=200, help_text=_("Product item name"), null=True
    )
    ean_upc = models.CharField(
        max_length=200,
        help_text=_(
            "EAN (European Article Number) / UPC (Universal Product Code) / GTIN (Global Trade In Number)"
        ),
        null=True,
        blank=True,
        unique=True,
    )
    package_size = models.CharField(
        max_length=200, help_text=_("Package size"), blank=True, null=True
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, blank=True, null=True
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.PROTECT, null=True, related_name="product_unit"
    )
    base_multiplier = models.IntegerField(
        verbose_name=_("Base multiplier"), blank=True, null=True
    )
    base_unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="product_base_unit",
    )
    is_lot_controlled = models.BooleanField(
        verbose_name=_("is lot controlled?"), default=False, blank=True
    )
    temperature_condition = models.ForeignKey(
        TemperatureCondition, on_delete=models.PROTECT, blank=True, null=True
    )
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, blank=True, null=True)
    lead_time = models.IntegerField(
        verbose_name=_("Lead time"),
        help_text=_("Lead time in day(s)"),
        blank=True,
        null=True,
    )
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True, auto_now_add=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("product_detail", args=[str(self.id)])

    def __str__(self):
        return "%s %s %s" % (self.ean_upc, self.supplier.name, self.name)

    def __unicode__(self):
        return "[%s] %s " % (self.ean_upc, self.name)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        # permissions = (("view_product", "Can view products"),)
        ordering = ["name"]


class ProductLot(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    number = models.IntegerField(verbose_name=_("Lot number"))
    expired = models.DateField(verbose_name=_("Expired at"))
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True, auto_now_add=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("product_detail", args=[str(self.id)])

    def __str__(self):
        return "%s %s %s" % (self.product, self.number, self.expired)

    class Meta:
        verbose_name = _("Product Lot")
        verbose_name_plural = _("Product Lots")
        # permissions = (("view_productlot", "Can view product lots"),)
        ordering = ["product"]


class Storage(models.Model):
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200)

    def __str__(self):
        return "[%s] %s" % (self.location, self.name)

    class Meta:
        ordering = ["name"]


class PackageCondition(models.Model):
    name = models.CharField(
        max_length=30, help_text=_("Package condition"), blank=True, null=True
    )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return "%s" % (self.name)


class PhysicalCondition(models.Model):
    name = models.CharField(
        max_length=30, help_text=_("Physical condition"), blank=True, null=True
    )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return "%s" % (self.name)


class StockIn(models.Model):
    date_in = models.DateField(verbose_name=_("Date in"), auto_now_add=True)
    storage = models.ForeignKey(Storage, on_delete=models.PROTECT, null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    lot_number = models.CharField(
        max_length=30, verbose_name=_("Lot number"), null=True
    )
    lot_expired = models.DateField(verbose_name=_("Expired at"), null=True)
    quantity = models.IntegerField(verbose_name=_("Quantity"), default=1)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True)
    package_condition = models.ForeignKey(
        PackageCondition, on_delete=models.PROTECT, null=True, blank=True
    )
    physical_condition = models.ForeignKey(
        PhysicalCondition, on_delete=models.PROTECT, null=True, blank=True
    )
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True, auto_now_add=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )

    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    @property
    def stockin_lot(self):
        try:
            return self._stockin_lot
        except StockInLot.DoesNotExist:
            return StockInLot.objects.create(
                stok_in=self,
            )

    def create_usingproduct(self, request):
        usingproduct = UsingProduct()
        usingproduct.stock_in = self
        usingproduct.save()
        return usingproduct

    def get_stockin_lot_url(self):
        return self._stockin_lot.get_absolute_url()

    def get_absolute_url(self):
        return reverse("stockin_detail", args=[str(self.id)])

    def get_row_icon(self):
        if self.product.lot_controlled and not self.product_lot:
            return (
                """%s <i class="fa fa-exclamation-circle" aria-hidden="true"></i>"""
                % self.product
            )
        else:
            return "%s" % self.product

    def get_lot_url(self):
        return self.product.get_absolute_url()

    def has_lot(self):
        return bool(self.product.lot_controlled)

    def __str__(self):
        return "%s %s %s %s %s" % (
            self.product.number,
            self.product.vendor,
            self.product.name,
            self.quantity,
            self.product.base_unit,
        )

    class Meta:
        ordering = ["-lastmodification"]


class StockInLot(models.Model):
    stock_in = models.ForeignKey(
        StockIn,
        related_name="_stockin_lot",
        on_delete=models.DO_NOTHING,
    )
    number = models.CharField(max_length=30, verbose_name=_("Lot number"), null=True)
    expired = models.DateField(verbose_name=_("Expired at"), null=True)
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True, auto_now_add=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("stockin_lot", args=[str(self.id)])

    def __str__(self):
        return "%s %s" % (self.number, self.expired)

    class Meta:
        ordering = ["-lastmodification"]


class UsedAt(models.Model):
    name = models.CharField(max_length=200)
    is_onboard_stockcheck = models.BooleanField(
        verbose_name=_("onboard stock check?"), default=False
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class UsingProduct(models.Model):
    date_use = models.DateField(verbose_name=_("Date used"), auto_now_add=True)
    stock_in = models.ForeignKey(StockIn, on_delete=models.PROTECT, null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    lot_number = models.CharField(
        max_length=30, verbose_name=_("Lot number"), null=True
    )
    lot_expired = models.DateField(verbose_name=_("Expired at"), null=True)
    unit_used = models.IntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True)
    used_at = models.ForeignKey(UsedAt, on_delete=models.PROTECT, null=True)
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True, auto_now_add=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def create_returningproduct(self, request):
        returningproduct = ReturningProduct()
        returningproduct.using_product = self
        returningproduct.save()
        return returningproduct

    def get_absolute_url(self):
        return reverse("usingproduct_detail", args=[str(self.id)])

    def __str__(self):
        return "%s %s %s" % (self.used_at, self.product, self.unit_used)

    class Meta:
        ordering = ["-lastmodification"]


class ReturningProduct(models.Model):
    date_return = models.DateField(verbose_name=_("Date return"), auto_now_add=True)
    used_from = models.ForeignKey(UsedAt, on_delete=models.PROTECT, null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    lot_number = models.CharField(
        max_length=30, verbose_name=_("Lot number"), null=True
    )
    lot_expired = models.DateField(verbose_name=_("Expired at"), null=True)
    unit_return = models.IntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True)
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True, auto_now_add=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_absolute_url(self):
        return reverse("usingproduct_detail", args=[str(self.id)])

    def __str__(self):
        return "%s %s %s %s" % (
            self.used_from,
            self.product.name,
            self.unit_return,
            self.unit,
        )

    class Meta:
        ordering = ["-lastmodification"]


class UserExtension(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="extension",
        verbose_name=_("Benutzer"),
        on_delete=models.DO_NOTHING,
    )
    location = models.OneToOneField(
        Location,
        related_name="extension",
        verbose_name=_("Location"),
        on_delete=models.DO_NOTHING,
    )
    product_group = models.ManyToManyField(
        ProductGroup, verbose_name=_("Group product")
    )
    image = models.ImageField(
        upload_to="avatars/",
        default="avatars/avatar.jpg",
        verbose_name=_("Bild"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("User Extension")
        verbose_name_plural = _("User Extensions")

    def __str__(self):
        return "%s" % self.user

    def __unicode__(self):
        return self.user


ORD_STATUS = (
    ("1", _("New")),
    ("2", _("Partially delivered")),
    ("9", _("Complete")),
    ("0", _("Cancel")),
)


class Ordering(models.Model):
    date_order = models.DateField(verbose_name=_("Date order"), auto_now_add=True)
    status = models.CharField(
        max_length=1, verbose_name=_("Ordering status"), choices=ORD_STATUS, default="1"
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(verbose_name=_("Quantity"), default=1)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True)
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True, auto_now_add=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )
    lastmodifiedby = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def get_delivered(self):
        ret = 0
        a = OrderingStockin.objects.filter(ordering_id=self.id).all()
        for b in a:
            ret += b.quantity
        return ret

    def __str__(self):
        return "%s %s" % (self.supplier, self.product)


class OrderingStockin(models.Model):
    ordering = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    stockin = models.ForeignKey(
        StockIn, on_delete=models.PROTECT, null=True, related_name="orderingstock"
    )
    quantity = models.IntegerField(default=0)


class StockAdjustReason(models.Model):
    reason = models.CharField(verbose_name=_("Reason"), max_length=30)

    def __str__(self):
        return "%s" % (self.reason)


class StockAdjust(models.Model):
    adjust_date = models.DateField(verbose_name=_("Adjust date"), auto_now_add=True)
    reason = models.ForeignKey(
        StockAdjustReason,
        verbose_name=_("Adjust Reason"),
        on_delete=models.PROTECT,
        null=True,
    )
    storage = models.ForeignKey(Storage, on_delete=models.PROTECT, null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    lot_number = models.CharField(
        max_length=30, verbose_name=_("Lot number"), null=True
    )
    lot_expired = models.DateField(verbose_name=_("Expired at"), null=True)
    quantity = models.IntegerField(verbose_name=_("Quantity"), default=1)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True)
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True, auto_now_add=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )

    def __str__(self):
        return "%s %s %s" % (self.reason, self.quantity, self.unit)


class Closing(models.Model):
    """
    class to handle Closing.
    This class represents a closing period for inventory management.
    It includes details such as the closing date, the user who created the closing,
    and timestamps for creation and last modification.
    The closing date indicates when the inventory was closed for adjustments,
    and the created_by field tracks the user responsible for the closing.
    This class is used to manage inventory closing periods, ensuring accurate records
    and facilitating the closing process.
    """

    closing_date = models.DateField(verbose_name=_("Closing date"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_staff": True},
        blank=True,
        verbose_name=_("Last modified by"),
        null=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return "%s %s" % (self.closing_date, self.created_by)


class ClosingStockIn(models.Model):
    """
    class to handle Closing Stock In.
    This class represents a record of stock that has been added to the inventory
    during a closing period. It includes details such as the closing date, storage location,
    product information, lot number, expiration date, quantity, unit of measurement,
    and timestamps for creation and last modification.
    It also keeps track of the user who last modified the record.
    This class is used to manage and track stock movements during closing periods,
    ensuring accurate inventory records and facilitating the closing process."""

    closing = models.ForeignKey(
        Closing, verbose_name=_("Closing"), on_delete=models.PROTECT, null=True
    )
    date_in = models.DateField(verbose_name=_("Date in"), auto_now_add=True)
    storage = models.ForeignKey(Storage, on_delete=models.PROTECT, null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    lot_number = models.CharField(
        max_length=30, verbose_name=_("Lot number"), null=True
    )
    lot_expired = models.DateField(verbose_name=_("Expired at"), null=True)
    quantity = models.IntegerField(verbose_name=_("Quantity"), default=1)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True)
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True, auto_now_add=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
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
        return "%s %s %s %s %s" % (
            self.product.number,
            self.product.vendor,
            self.product.name,
            self.quantity,
            self.product.base_unit,
        )


class ClosingUsingProduct(models.Model):
    """
    class to handle Closing Using Product.
    This class represents a record of a product that has been used
    during a closing period. It includes details such as the closing date,
    """

    closing = models.ForeignKey(
        Closing, verbose_name=_("Closing"), on_delete=models.PROTECT, null=True
    )
    date_use = models.DateField(verbose_name=_("Date used"), auto_now_add=True)
    stock_in = models.ForeignKey(StockIn, on_delete=models.PROTECT, null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    lot_number = models.CharField(
        max_length=30, verbose_name=_("Lot number"), null=True
    )
    lot_expired = models.DateField(verbose_name=_("Expired at"), null=True)
    unit_used = models.IntegerField(default=1)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True)
    used_at = models.ForeignKey(UsedAt, on_delete=models.PROTECT, null=True)
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True, auto_now_add=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
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
        return "%s %s %s" % (self.used_at, self.product, self.unit_used)


########################## Gambaran Darah Tepi ##################################
class PBSTest(models.Model):
    """
    Class to handle PBSTest.
    This class represents a test that can be performed on a blood sample.
    It is linked to a specific test and contains information about the test name,
    whether it is active, its sort order, and timestamps for creation and last modification.
    It also keeps track of the user who last modified the test.
    This class is used to manage and organize tests within the system, allowing for
    easy retrieval and display of test information in the context of blood sample analysis.
    """

    test = models.ForeignKey(Tests, verbose_name=_("test"), on_delete=models.PROTECT)
    name = models.CharField(max_length=50, verbose_name=_("Nama test"))
    active = models.BooleanField(verbose_name=_("Active?"), default=True, blank=True)
    sort = models.IntegerField(verbose_name=_("Sort"), help_text=_("Sorted priority"))
    dateofcreation = models.DateTimeField(
        verbose_name=_("Created at"), blank=True, null=True, auto_now_add=True
    )
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
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
        return "%s %s" % (self.test, self.name)


class PBSResult(models.Model):
    order = models.ForeignKey(Orders, verbose_name=_("order"), on_delete=models.PROTECT)
    pbs_test = models.ForeignKey(
        PBSTest, verbose_name=_("HDT Result"), on_delete=models.PROTECT
    )
    text_result = models.TextField(verbose_name=_("Text result"), blank=True, null=True)
    lastmodification = models.DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
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
        return "%s %s %s" % (self.order, self.pbs_test, self.text_result)

    class Meta:
        unique_together = (("order", "pbs_test"),)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Create a token when a new user is created.
    This function is connected to the post_save signal of the User model.
    It checks if the user is newly created and then creates a Token for that user.
    Args:
        sender (Model): The model class that sent the signal.
        instance (User): The instance of the user that was created or updated.
        created (bool): A boolean indicating whether a new instance was created.
        **kwargs: Additional keyword arguments.
    """
    if created:
        Token.objects.create(user=instance)


@receiver(models.signals.post_save, sender=Worklists)
def create_worklist_test(sender, instance, created, **kwargs):
    """
    create worklist test when a new worklist is created.
    This function checks if the worklist is newly created and then
    checks for pending OrderResults. If there are pending results that
    """
    if created:
        have_test = False
        res_pend = OrderResults.objects.filter(validation_status=0).all()
        for rp in res_pend:
            if BatchGroupTests.objects.filter(
                batch_group=instance.batch_group, test=rp.test
            ).exists():
                if not WorklistTests.objects.filter(
                    worklistorder__order=rp.order, test=rp.test
                ).exists():
                    # insert
                    wl_order, msg = WorklistOrders.objects.get_or_create(
                        worklist=instance, order=rp.order
                    )
                    wl_tes = WorklistTests(worklistorder=wl_order, test=rp.test)
                    wl_tes.save()
                    have_test = True

        if not have_test:
            instance.delete()


@receiver(models.signals.post_save, sender=Results)
def create_result(sender, instance, created, **kwargs):
    """
    Create or update result in OrderResults when a new result is created.
    This function checks if the result is new and updates the corresponding
    OrderResults entry with the unit, reference range, and pathology mark.
    This is triggered after a Results instance is saved.
    This function is connected to the post_save signal of the Results model.
    It updates the OrderResults model with the unit, reference range, and pathology mark
    """
    if created:
        # update unit
        tes_par = TestParameters.objects.filter(test_id=instance.test_id)
        if tes_par:
            OrderResults.objects.filter(
                order_id=instance.order_id, test_id=instance.test_id
            ).update(unit=tes_par[0].unit)

        # update ref range and flag based on result calculation
        OrderResults.objects.filter(
            order_id=instance.order_id, test_id=instance.test_id
        ).update(patologi_mark=instance.mark, ref_range=instance.ref_range)


