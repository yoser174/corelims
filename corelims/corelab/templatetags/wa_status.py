from django import template

register = template.Library()

from ..models import (
    OrderResults,
    Tests,
    Workarea,
    WorkareaTestGroups,
    Orders,
    OrderResults,
    Tests,
    Results,
    OrderSampleLogs,
)
from django.utils.html import format_html

from django.utils.translation import gettext_lazy as _


@register.filter
def order_sample_log(order_sample_id):
    if order_sample_id != "":
        log = ""
        log_object = OrderSampleLogs.objects.filter(order_sample_id=order_sample_id)
        for detail in log_object:
            log = log + detail.dateofcreation.strftime("%Y-%m-%d %H:%M:%S")
            if str(detail.status) == "1":
                log = (
                    log
                    + " Sample No. <b>"
                    + detail.order_sample.sample_no
                    + "</b> ["
                    + detail.order_sample.specimen.name
                    + "]"
                    + str(_(" received by "))
                    + "<b>"
                    + detail.lastmodifiedby.username
                    + "</b>"
                )
            elif str(detail.status) == "2":
                log = (
                    log
                    + " <b>"
                    + detail.lastmodifiedby.username
                    + "</b>"
                    + str(_(" Request new sample, reason : "))
                    + "<b>"
                    + detail.request_new.name
                    + "</b>"
                )

            # comment
            elif str(detail.status) == "0" and detail.note:
                log = (
                    log
                    + " <b>"
                    + detail.lastmodifiedby.username
                    + "</b>"
                    + str(_(" add comment : "))
                    + "<b>"
                    + detail.note
                    + "</b>"
                )

            log = log + "<br>"
            # user_id = detail['lastmodifiedby']
            # user_object = Users.objects.get(pk=user_id)
            # log = log + 'Received <b>'+user_object.name+'</b><br>'

        return format_html(log)
    else:
        return ""


@register.filter
def pervious_rerun(order_id, test_id):
    if order_id != "" and test_id != "":
        order = Orders.objects.get(pk=int(order_id))
        test = Tests.objects.get(pk=int(test_id))
        order_result = OrderResults.objects.filter(order=order, test=test).values(
            "result_id"
        )
        if not order_result[0]["result_id"]:
            return ""
        print(order_result.count())
        result = (
            Results.objects.filter(
                order=order,
                test=test,
                pk__lt=order_result[0]["result_id"],
                alfa_result__isnull=False,
            )
            .values("id", "alfa_result")
            .order_by("-id")[:1]
        )
        if result.count() > 0:
            return format_html(result[0]["alfa_result"])
            # if result[0]['alfa_result'] != None:
            #    return format_html(result[0]['alfa_result'])
            # else:
            #    return ''
        else:
            return ""
    else:
        return ""


@register.filter
def pervious_result_1(order_id, test_id):
    if order_id != "" and test_id != "":
        order = Orders.objects.get(pk=int(order_id))
        test = Tests.objects.get(pk=int(test_id))
        order_result = (
            OrderResults.objects.filter(
                order_id__lt=order.id,
                order__patient_id=order.patient_id,
                test=test,
                validation_status__gte=3,
            )
            .values("id", "result_id")
            .order_by("-order_id")[:1]
        )
        if order_result.count() > 0:
            o_order_result = OrderResults.objects.get(pk=order_result[0]["id"])
            result = Results.objects.get(pk=order_result[0]["result_id"])
            return format_html(
                result.alfa_result
                + '<br><small><a href="/orders/results/'
                + str(o_order_result.order.id)
                + '/"  target="_blank" >('
                + o_order_result.order.number
                + ")</a></small>"
            )
        else:
            return ""
    else:
        return ""


@register.filter
def pervious_result_2(order_id, test_id):
    if order_id != "" and test_id != "":
        order = Orders.objects.get(pk=int(order_id))
        test = Tests.objects.get(pk=int(test_id))
        order_result = (
            OrderResults.objects.filter(
                order_id__lt=order.id,
                order__patient_id=order.patient_id,
                test=test,
                validation_status__gte=3,
            )
            .values("id", "result_id")
            .order_by("-order_id")[1:2]
        )
        if order_result.count() > 0:
            o_order_result = OrderResults.objects.get(pk=order_result[0]["id"])
            result = Results.objects.get(pk=order_result[0]["result_id"])
            return format_html(
                result.alfa_result
                + '<br><small><a href="/orders/results/'
                + str(o_order_result.order.id)
                + '/"  target="_blank" >('
                + o_order_result.order.number
                + ")</a></small>"
            )
        else:
            return ""
    else:
        return ""


@register.filter
def pervious_result_3(order_id, test_id):
    if order_id != "" and test_id != "":
        order = Orders.objects.get(pk=int(order_id))
        test = Tests.objects.get(pk=int(test_id))
        order_result = (
            OrderResults.objects.filter(
                order_id__lt=order.id,
                order__patient_id=order.patient_id,
                test=test,
                validation_status__gte=3,
            )
            .values("id", "result_id")
            .order_by("-order_id")[2:3]
        )
        if order_result.count() > 0:
            o_order_result = OrderResults.objects.get(pk=order_result[0]["id"])
            result = Results.objects.get(pk=order_result[0]["result_id"])
            return format_html(
                result.alfa_result
                + '<br><small><a href="/orders/results/'
                + str(o_order_result.order.id)
                + '/"  target="_blank" >('
                + o_order_result.order.number
                + ")</a></small>"
            )
        else:
            return ""
    else:
        return ""


@register.filter
def status_of_wa(wa_id, order_id):
    wa_group = Workarea.objects.get(pk=wa_id)
    test_group = WorkareaTestGroups.objects.filter(workarea=wa_group).values(
        "testgroup"
    )

    html_div = """<td class="progs"><div class="progress progress-striped">         
<div class="progress-bar progress-bar-success" role="progressbar" style="width: 75%;">
         &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;        
</div>
</div>
</td>
"""
    # return format_html(html_div)

    order_res = OrderResults.objects.filter(
        order_id=order_id,
        validation_status=0,
        is_header=0,
        test__test_group__in=test_group,
    )
    if order_res.count() > 0:
        return format_html(
            """<td class="progs"><div class="progress progress-striped">         
<div class="progress-bar progress-bar-danger" role="progressbar" style="width: 0%;">
         &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;        
</div>
</div>
</td>
"""
        )

    order_res = OrderResults.objects.filter(
        order_id=order_id,
        validation_status=1,
        is_header=0,
        test__test_group__in=test_group,
    )
    if order_res.count() > 0:
        return format_html(
            """<td class="progs"><div class="progress progress-striped">         
<div class="progress-bar progress-bar-danger" role="progressbar" style="width: 25%;">
         &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;        
</div>
</div>
</td>
"""
        )

    order_res = OrderResults.objects.filter(
        order_id=order_id,
        validation_status=2,
        is_header=0,
        test__test_group__in=test_group,
    )
    if order_res.count() > 0:
        return format_html(
            """<td class="progs"><div class="progress progress-striped">         
<div class="progress-bar progress-bar-warning" role="progressbar" style="width: 50%;">
         &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;        
</div>
</div>
</td>
"""
        )

    order_res = OrderResults.objects.filter(
        order_id=order_id,
        validation_status=3,
        is_header=0,
        test__test_group__in=test_group,
    )
    if order_res.count() > 0:
        return format_html(
            """<td class="progs"><div class="progress progress-striped">         
<div class="progress-bar progress-bar-success" role="progressbar" style="width: 75%;">
         &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;        
</div>
</div>
</td>
"""
        )

    order_res = OrderResults.objects.filter(
        order_id=order_id,
        validation_status=4,
        is_header=0,
        test__test_group__in=test_group,
    )
    if order_res.count() > 0:
        return format_html(
            """<td class="progs"><div class="progress progress-striped">         
<div class="progress-bar progress-bar-info" role="progressbar" style="width: 100%;">
         &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;        
</div>
</div>
</td>
"""
        )

    return format_html(
        """<td class="progs"><div class="progress progress-striped">         
<div class="progress-bar progress-bar-info" role="progressbar" style="width: 100%;">
         &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;        
</div>
</div>
</td>
"""
    )
