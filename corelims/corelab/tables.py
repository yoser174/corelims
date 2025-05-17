import django_tables2 as tables
from pprint import pprint

from .models import (
    QualityControl,
    TestGroups,
    Tests,
    Orders,
    Patients,
    HistoryOrders,
    OrderTests,
    OrderSampleLogs,
    OrderSamples,
    Instruments,
    InstrumentBatch,
)
from django.db.models import Q
from .custom.custom_columns import (
    ModelDetailLinkColumn,
    IncludeColumn,
    CssFieldColumn,
    LabelIconColumn,
    ButtonColumn,
    WaStatusIconColumn,
)
from django.contrib.humanize.templatetags.humanize import intcomma

from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


class ColumnWithThausandSeparator(tables.Column):
    def render(self, value):
        return intcomma(value)


class TestGroupsTable(tables.Table):
    edit_test_group = IncludeColumn(
        "includes/testgroups_row_edit_toolbar.html",
        attrs={"th": {"width": "120px"}},
        verbose_name=" ",
        orderable=False,
    )

    class Meta:
        model = TestGroups
        exclude = ("id",)
        sequence = ("name", "sort")
        order_by = ("sort",)


class TestsTable(tables.Table):
    edit_test = IncludeColumn(
        "includes/tests_row_edit_toolbar.html",
        attrs={"th": {"width": "120px"}},
        verbose_name=" ",
        orderable=False,
    )

    class Meta:
        model = Tests
        exclude = ("id",)
        sequence = ("name", "sort")
        order_by = ("sort",)


class OrdersTable(tables.Table):
    total_price = CssFieldColumn(
        "record.get_total_price.total",
        verbose_name=_("Total Price"),
        attrs={"td": {"align": "right"}},
    )
    edit_order = IncludeColumn(
        "includes/billing/orders_row_edit_toolbar.html",
        attrs={"th": {"width": "120px"}},
        verbose_name=" ",
        orderable=False,
    )

    class Meta:
        model = Orders
        exclude = ("id",)
        # sequence = ('number')
        fields = (
            "order_date",
            "service",
            "number",
            "priority",
            "origin",
            "patient.patient_id",
            "patient.name",
            "total_price",
        )
        order_by = ("-number",)


class OrdersTableWaGroup(tables.Table):
    total_price = CssFieldColumn(
        "record.get_total_price.total",
        verbose_name=_("Total Price"),
        attrs={"td": {"align": "right"}},
    )
    edit_order = IncludeColumn(
        "includes/orders_wa_row_edit_toolbar.html",
        attrs={"th": {"width": "120px"}},
        verbose_name=" ",
        orderable=False,
    )

    class Meta:
        model = Orders
        exclude = ("id",)
        # sequence = ('number')
        fields = (
            "order_date",
            "service",
            "number",
            "priority",
            "origin",
            "patient.patient_id",
            "patient.name",
            "total_price",
        )
        order_by = ("-number",)


class PatientsTable(tables.Table):
    edit_order = IncludeColumn(
        "includes/billing/patient_row_edit_toolbar.html",
        attrs={"th": {"width": "120px"}},
        verbose_name=" ",
        orderable=False,
    )

    class Meta:
        model = Patients
        fields = (
            "patient_id",
            "name",
            "gender",
            "dob",
            "address",
        )
        exclude = ("id",)


class SelectPatientsTable(tables.Table):
    use_product = ButtonColumn(
        gl_icon="external-link",
        extra_class="btn-info",
        condition="1",
        onclick="location.href='{% url 'create_order_from_patient' record.pk %}'",
        verbose_name="",
        orderable=False,
    )

    class Meta:
        model = Patients
        exclude = ("id",)


class JMTable(tables.Table):
    export_formats = ["csv", "xls"]
    ColumnWithThausandSeparator("get_sub_total_price_tariff")
    ColumnWithThausandSeparator("get_sub_total_price_service")

    class Meta:
        model = Orders
        fields = (
            "order_date",
            "number",
            "priority",
            "patient",
            "insurance",
            "origin",
            "get_test_str",
            "doctor",
            "get_sub_total_price_tariff",
            "get_sub_total_price_service",
        )
        exclude = ("id",)
        template = "django_tables2/bootstrap.html"


class InpatMedSrvTable(tables.Table):
    ColumnWithThausandSeparator("get_sub_total_price_tariff")
    ColumnWithThausandSeparator("get_sub_total_price_service")

    class Meta:
        model = Orders
        fields = (
            "patient__patient_id",
            "patient__name",
            "origin__name",
            "insurance__name",
        )
        exclude = ("id",)
        template = "django_tables2/bootstrap.html"


class OriginTable(tables.Table):
    export_formats = ["csv", "xls"]

    class Meta:
        model = Orders
        fields = (
            "origin__name",
            "number__count",
        )
        exclude = ("id",)
        template = "django_tables2/bootstrap.html"


class InsuranceTable(tables.Table):
    export_formats = ["csv", "xls"]

    class Meta:
        model = Orders
        fields = (
            "insurance__name",
            "number__count",
        )
        exclude = ("id",)
        template = "django_tables2/bootstrap.html"


class TestsTable(tables.Table):
    export_formats = ["csv", "xls"]

    class Meta:
        model = Orders
        fields = (
            "order_items__test__name",
            "number__count",
        )
        exclude = ("id",)
        template = "django_tables2/bootstrap.html"


class pdfColumn(tables.Column):
    def render(self, value):
        return format_html(
            '<a href="{}" target="_blank" class="btn btn-default" role="button"> \
        <span class="fa fa-file-pdf"></span></a>',
            value,
        )


class progressColumn(tables.Column):
    def render(self, value):
        clr = "danger"
        if str(value) == "25":
            clr = "danger"
        if str(value) == "50":
            clr = "warning"
        if str(value) == "75":
            clr = "success"
        if str(value) == "100":
            clr = "info"
        return format_html(
            '<div class="progress progress-striped"> \
        <div class="progress-bar progress-bar-'
            + clr
            + '" role="progressbar" style="width: {}%;"> \
        &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;\
        </div></div>',
            value,
        )


class receiveColumn(tables.Column):
    def render(self, value):
        str_output = '<a href="#" data-id="{}" class="viewdetails">'
        rcv = OrderSamples.objects.filter(order_id=value).exclude(status=1)
        if rcv.count() > 0:
            str_output = str_output + '<span class="fa fa-window-close"></span>'
        else:
            str_output = str_output + '<span class="fa fa-check-circle"></span>'
        # have comment
        log = OrderSampleLogs.objects.filter(
            order_sample__order_id=value, note__isnull=False
        )
        if log.count() > 0:
            str_output = (
                str_output + '&nbsp;&nbsp;&nbsp;<span class="fa fa-comment"></span>'
            )
        # request new sample
        order_sample = OrderSamples.objects.filter(order_id=value, status=2)
        if order_sample.count() > 0:
            str_output = (
                str_output + '&nbsp;&nbsp;&nbsp;<span class="fa fa-exclamation"></span>'
            )
        str_output = str_output + "</a>"
        return format_html(str_output, value)


class OrderResultTable(tables.Table):
    receive = receiveColumn(accessor="orderextended.order_id", verbose_name=_("s.rcv"))
    progs = progressColumn(accessor="orderextended.get_progress", verbose_name="")
    pdf_url = pdfColumn(accessor="orderextended.result_pdf_url", verbose_name="")
    edit_order = IncludeColumn(
        "middleware/include/orders_row_edit_toolbar.html",
        attrs={"th": {"width": "120px"}},
        verbose_name=" ",
        orderable=False,
        accessor="orderextended.result_pdf_url",
    )

    class Meta:
        model = Orders
        exclude = ("id",)
        # sequence = ('number')
        fields = (
            "dateofcreation",
            "service",
            "number",
            "priority",
            "origin",
            "patient.patient_id",
            "patient.name",
        )
        order_by = ("-number",)


class OrderResultTableWa(tables.Table):
    receive = receiveColumn(accessor="id", verbose_name=_("s.rcv"))
    # progs = progressColumn(accessor="orderextended.get_progress",verbose_name='')
    pdf_url = pdfColumn(accessor="orderextended.result_pdf_url", verbose_name="")
    edit_order = IncludeColumn(
        "includes/orders_wa_row_edit_toolbar.html",
        attrs={"th": {"width": "120px"}},
        verbose_name=" ",
        orderable=False,
        accessor="orderextended.result_pdf_url",
    )

    class Meta:
        model = Orders
        exclude = ("id",)
        # sequence = ('number')
        fields = (
            "dateofcreation",
            "service",
            "number",
            "priority",
            "origin",
            "patient.patient_id",
            "patient.name",
        )
        order_by = ("-number",)


class CompleteOrderTable(tables.Table):
    # progs = progressColumn(accessor="orderextended.get_progress",verbose_name='')
    pdf_url = pdfColumn(accessor="orderextended.result_pdf_url", verbose_name="")
    edit_order = IncludeColumn(
        "includes/orders_complete_toolbar.html",
        attrs={"th": {"width": "120px"}},
        verbose_name=" ",
        orderable=False,
        accessor="orderextended.result_pdf_url",
    )

    class Meta:
        model = Orders
        exclude = ("id",)
        # sequence = ('number')
        fields = (
            "dateofcreation",
            "service",
            "number",
            "priority",
            "origin",
            "patient.patient_id",
            "patient.name",
        )
        order_by = ("-number",)


class OrderHistoryTable(tables.Table):
    class Meta:
        model = HistoryOrders
        exclude = ("id",)
        # sequence = ('number')
        fields = (
            "action_user",
            "action_date",
            "action_code",
            "test",
            "action_text",
        )
        # fields = ('order_date','number','priority','origin','patient.patient_id','patient.name')
        order_by = ("-action_date",)


class WorklistTable(tables.Table):
    edit_order = IncludeColumn(
        "includes/worklist_row_edit_toolbar.html",
        attrs={"th": {"width": "120px"}},
        verbose_name=" ",
        orderable=False,
    )

    class Meta:
        model = Orders
        fields = (
            "id",
            "batch_date",
            "batch_group",
            "lastmodifiedby",
            "lastmodification",
        )
        order_by = ("-id",)


class TransTable(tables.Table):
    price = CssFieldColumn(
        "record.get_price", verbose_name=_("Price"), attrs={"td": {"align": "right"}}
    )

    class Meta:
        model = OrderTests
        fields = (
            "order.number",
            "order.order_date",
            "order.service",
            "order.priority",
            "order.origin",
            "order.insurance",
            "test",
        )
        order_by = ("order",)


class InstrumentBachModeTable(tables.Table):
    edit_order = IncludeColumn(
        "middleware/include/instrumentbatchmode_row_edit_toolbar.html",
        attrs={"th": {"width": "120px"}},
        verbose_name=" ",
        orderable=False,
        accessor="orderextended.result_pdf_url",
    )

    class Meta:
        model = Instruments
        fields = ("name",)
        order_by = ("name",)


class InstrumentBachTable(tables.Table):
    class Meta:
        model = InstrumentBatch
        fields = (
            "order_sample",
            "order_sample.specimen.name",
            "status",
            "note",
        )
        order_by = ("order_sample",)


class QualityControlTable(tables.Table):
    # edit_order = IncludeColumn(
    #     "includes/worklist_row_edit_toolbar.html",
    #     attrs={"th": {"width": "120px"}},
    #     verbose_name=" ",
    #     orderable=False,
    # )

    class Meta:
        model = QualityControl
        fields = (
            "instrument",
            "instrument_test.test.name",
            "result.numeric_result",
            "result.lastmodification",
        )
        order_by = ("-id",)
