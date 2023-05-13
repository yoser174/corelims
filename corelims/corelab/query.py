from django.db import connection


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def medical_service_dtl(patient_id="", filter_sql=""):
    with connection.cursor() as cursor:
        sql = """ SELECT order_date,name,count(number) jum,tariff,(tariff * count(number)) tot
FROM
(
SELECT bbconnlab_orders.number,bbconnlab_orders.origin_id,bbconnlab_orders.insurance_id,bbconnlab_orders.order_date,
bbconnlab_tests.name, SUM(IFNULL(bbconnlab_testprices.tariff,0)) tariff
FROM
bbconnlab_ordertests
LEFT JOIN bbconnlab_orders ON bbconnlab_ordertests.order_id = bbconnlab_orders.id
LEFT JOIN bbconnlab_testprices ON bbconnlab_testprices.test_id = bbconnlab_ordertests.test_id 
AND bbconnlab_testprices.priority_id = bbconnlab_orders.priority_id
LEFT JOIN bbconnlab_tests ON bbconnlab_ordertests.test_id = bbconnlab_tests.id
WHERE patient_id = '"""
        sql += patient_id
        sql += """'
GROUP BY bbconnlab_orders.number,bbconnlab_orders.origin_id,bbconnlab_orders.insurance_id,bbconnlab_orders.order_date,
bbconnlab_tests.name
) dtl
WHERE
1 = 1
"""
        sql += filter_sql
        sql += " group by order_date,name,tariff "

        # print sql

        cursor.execute(sql)
        row = dictfetchall(cursor)
        return row


def medical_service_dtl_total(patient_id="", filter_sql=""):
    with connection.cursor() as cursor:
        sql = """ SELECT sum(tot) total FROM
        (SELECT order_date,name,count(number) jum,tariff,(tariff * count(number)) tot
FROM
(
SELECT bbconnlab_orders.number,bbconnlab_orders.origin_id,bbconnlab_orders.insurance_id,bbconnlab_orders.order_date,
bbconnlab_tests.name, SUM(IFNULL(bbconnlab_testprices.tariff,0)) tariff
FROM
bbconnlab_ordertests
LEFT JOIN bbconnlab_orders ON bbconnlab_ordertests.order_id = bbconnlab_orders.id
LEFT JOIN bbconnlab_testprices ON bbconnlab_testprices.test_id = bbconnlab_ordertests.test_id 
AND bbconnlab_testprices.priority_id = bbconnlab_orders.priority_id
LEFT JOIN bbconnlab_tests ON bbconnlab_ordertests.test_id = bbconnlab_tests.id
WHERE patient_id = '"""
        sql += patient_id
        sql += """'
GROUP BY bbconnlab_orders.number,bbconnlab_orders.origin_id,bbconnlab_orders.insurance_id,bbconnlab_orders.order_date,
bbconnlab_tests.name
) dtl
WHERE
1 = 1
"""
        sql += filter_sql
        sql += " group by order_date,name,tariff ) t "

        cursor.execute(sql)
        row = dictfetchall(cursor)

        return row[0]["total"]
