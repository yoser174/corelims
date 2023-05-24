import base64
import requests
import token
from django.conf import settings


class JasperServer(object):
    def get_token(self):
        username = settings.JASPER_USER
        password = settings.JASPER_PASS
        # token = base64.encodestring("%s:%s" % (username, password)).replace("\n", "")
        token = (
            base64.encodestring(("%s:%s" % (username, password)).encode())
            .decode()
            .strip()
        )
        return token

    def get_report(self, order_id, group_id):
        # print order_id
        # print group_id
        if not group_id:
            group_id = ""
            data = """
            <reportExecutionRequest>
                <reportUnitUri>/reports/corelims/clinical_result</reportUnitUri>
                <async>false</async>
                <freshData>true</freshData>
                <saveDataSnapshot>false</saveDataSnapshot>
                <outputFormat>pdf</outputFormat>
                <interactive>true</interactive>
                <ignorePagination>false</ignorePagination>
                <parameters>
                    <reportParameter name="ORDER_ID">
                        <value>{order_id}</value>
                    </reportParameter>
                </parameters>
            </reportExecutionRequest>
            """.format(
                order_id=order_id
            )

        else:
            data = """
            <reportExecutionRequest>
                <reportUnitUri>/reports/corelims/clinical_result</reportUnitUri>
                <async>false</async>
                <freshData>true</freshData>
                <saveDataSnapshot>false</saveDataSnapshot>
                <outputFormat>pdf</outputFormat>
                <interactive>true</interactive>
                <ignorePagination>false</ignorePagination>
                <parameters>
                    <reportParameter name="ORDER_ID">
                        <value>{order_id}</value>
                    </reportParameter>
                    <reportParameter name="GROUP_ID">
                        <value>{group_id}</value>
                    </reportParameter>
                </parameters>
            </reportExecutionRequest>
            """.format(
                order_id=order_id, group_id=group_id
            )

        # print data
        token = self.get_token()
        response = requests.post(
            url=settings.JASPER_REST + "reportExecutions",
            headers={
                "Authorization": "Basic " + token,
                "Accept": "application/json",
                "Content-Type": "application/xml",
            },
            data=data,
        )
        data = response.json()
        # print data
        try:
            request_id = data.get("requestId")
            export_id = data.get("exports")[0].get("id")
            status = data.get("status")
        except Exception as e:
            return False, data

        if status == "ready":
            report_url = (
                settings.JASPER_REST
                + "reportExecutions/{request_id}/exports/{export_id}/outputResource".format(
                    request_id=request_id, export_id=export_id
                )
            )

            report_resp = requests.get(
                url=report_url, headers=response.headers, cookies=response.cookies
            )
            return True, report_resp.content
        else:
            return False, data

    def get_report_orders(self, start_date, end_date, output):
        if not start_date:
            start_date = ""
        if not end_date:
            end_date = ""
        data = """
        <reportExecutionRequest>
            <reportUnitUri>/reports/corelims/report_orders</reportUnitUri>
            <async>false</async>
            <freshData>true</freshData>
            <saveDataSnapshot>false</saveDataSnapshot>
            <outputFormat>{output}</outputFormat>
            <interactive>true</interactive>
            <ignorePagination>false</ignorePagination>
            <parameters>
                <reportParameter name="START_DATE">
                    <value>{start_date}</value>
                </reportParameter>
                <reportParameter name="END_DATE">
                    <value>{end_date}</value>
                </reportParameter>
            </parameters>
        </reportExecutionRequest>
        """.format(
            start_date=start_date, end_date=end_date, output=output
        )

        # print data
        token = self.get_token()
        response = requests.post(
            url=settings.JASPER_REST + "reportExecutions",
            headers={
                "Authorization": "Basic " + token,
                "Accept": "application/json",
                "Content-Type": "application/xml",
            },
            data=data,
        )
        data = response.json()
        # print data
        try:
            request_id = data.get("requestId")
            export_id = data.get("exports")[0].get("id")
            status = data.get("status")
        except Exception as e:
            return False, data

        if status == "ready":
            report_url = (
                settings.JASPER_REST
                + "reportExecutions/{request_id}/exports/{export_id}/outputResource".format(
                    request_id=request_id, export_id=export_id
                )
            )

            report_resp = requests.get(
                url=report_url, headers=response.headers, cookies=response.cookies
            )
            return True, report_resp.content
        else:
            return False, data

    def get_report_ordertests(self, start_date, end_date, output):
        if not start_date:
            start_date = ""
        if not end_date:
            end_date = ""

        # print start_date
        # print end_date
        data = """
        <reportExecutionRequest>
            <reportUnitUri>/reports/corelims/report_ordertests</reportUnitUri>
            <async>false</async>
            <freshData>true</freshData>
            <saveDataSnapshot>false</saveDataSnapshot>
            <outputFormat>{output}</outputFormat>
            <interactive>true</interactive>
            <ignorePagination>false</ignorePagination>
            <parameters>
                <reportParameter name="START_DATE">
                    <value>{start_date}</value>
                </reportParameter>
                <reportParameter name="END_DATE">
                    <value>{end_date}</value>
                </reportParameter>
            </parameters>
        </reportExecutionRequest>
        """.format(
            start_date=start_date, end_date=end_date, output=output
        )

        # print data
        token = self.get_token()
        response = requests.post(
            url=settings.JASPER_REST + "reportExecutions",
            headers={
                "Authorization": "Basic " + token,
                "Accept": "application/json",
                "Content-Type": "application/xml",
            },
            data=data,
        )
        data = response.json()
        # print data
        try:
            request_id = data.get("requestId")
            export_id = data.get("exports")[0].get("id")
            status = data.get("status")
        except Exception as e:
            return False, data

        if status == "ready":
            report_url = (
                settings.JASPER_REST
                + "reportExecutions/{request_id}/exports/{export_id}/outputResource".format(
                    request_id=request_id, export_id=export_id
                )
            )

            report_resp = requests.get(
                url=report_url, headers=response.headers, cookies=response.cookies
            )
            return True, report_resp.content
        else:
            return False, data

    def get_report_tats(self, start_date, end_date, output):
        if not start_date:
            start_date = ""
        if not end_date:
            end_date = ""

        # print start_date
        # print end_date
        data = """
        <reportExecutionRequest>
            <reportUnitUri>/reports/corelims/report_tats</reportUnitUri>
            <async>false</async>
            <freshData>true</freshData>
            <saveDataSnapshot>false</saveDataSnapshot>
            <outputFormat>{output}</outputFormat>
            <interactive>true</interactive>
            <ignorePagination>false</ignorePagination>
            <parameters>
                <reportParameter name="START_DATE">
                    <value>{start_date}</value>
                </reportParameter>
                <reportParameter name="END_DATE">
                    <value>{end_date}</value>
                </reportParameter>
            </parameters>
        </reportExecutionRequest>
        """.format(
            start_date=start_date, end_date=end_date, output=output
        )

        # print data
        token = self.get_token()
        response = requests.post(
            url=settings.JASPER_REST + "reportExecutions",
            headers={
                "Authorization": "Basic " + token,
                "Accept": "application/json",
                "Content-Type": "application/xml",
            },
            data=data,
        )
        data = response.json()
        # print data
        try:
            request_id = data.get("requestId")
            export_id = data.get("exports")[0].get("id")
            status = data.get("status")
        except Exception as e:
            return False, data

        if status == "ready":
            report_url = (
                settings.JASPER_REST
                + "reportExecutions/{request_id}/exports/{export_id}/outputResource".format(
                    request_id=request_id, export_id=export_id
                )
            )

            report_resp = requests.get(
                url=report_url, headers=response.headers, cookies=response.cookies
            )
            return True, report_resp.content
        else:
            return False, data


    def get_report_order(self, order_pk, report, output):
        data = """
        <reportExecutionRequest>
            <reportUnitUri>/reports/corelims/{report}</reportUnitUri>
            <async>false</async>
            <freshData>true</freshData>
            <saveDataSnapshot>false</saveDataSnapshot>
            <outputFormat>{output}</outputFormat>
            <interactive>true</interactive>
            <ignorePagination>false</ignorePagination>
            <parameters>
                <reportParameter name="ORDER_ID">
                    <value>{order_pk}</value>
                </reportParameter>
            </parameters>
        </reportExecutionRequest>
        """.format(
            report=report, order_pk=order_pk, output=output
        )

        # print data
        token = self.get_token()
        response = requests.post(
            url=settings.JASPER_REST + "reportExecutions",
            headers={
                "Authorization": "Basic " + token,
                "Accept": "application/json",
                "Content-Type": "application/xml",
            },
            data=data,
        )
        data = response.json()
        # print data
        try:
            request_id = data.get("requestId")
            export_id = data.get("exports")[0].get("id")
            status = data.get("status")
        except Exception as e:
            return False, data

        if status == "ready":
            report_url = (
                settings.JASPER_REST
                + "reportExecutions/{request_id}/exports/{export_id}/outputResource".format(
                    request_id=request_id, export_id=export_id
                )
            )

            report_resp = requests.get(
                url=report_url, headers=response.headers, cookies=response.cookies
            )
            return True, report_resp.content
        else:
            return False, data

    def get_patient_trans_history(self, start_date, end_date, output, patient_id):
        if not start_date:
            start_date = ""
        if not end_date:
            end_date = ""
        data = """
        <reportExecutionRequest>
            <reportUnitUri>/reports/corelims/patient_transactions_history</reportUnitUri>
            <async>false</async>
            <freshData>true</freshData>
            <saveDataSnapshot>false</saveDataSnapshot>
            <outputFormat>{output}</outputFormat>
            <interactive>true</interactive>
            <ignorePagination>false</ignorePagination>
            <parameters>
                <reportParameter name="START_DATE">
                    <value>{start_date}</value>
                </reportParameter>
                <reportParameter name="END_DATE">
                    <value>{end_date}</value>
                </reportParameter>
                <reportParameter name="PATIENT_ID">
                    <value>{patient_id}</value>
                </reportParameter>
            </parameters>
        </reportExecutionRequest>
        """.format(
            start_date=start_date,
            end_date=end_date,
            output=output,
            patient_id=patient_id,
        )

        # print data
        token = self.get_token()
        response = requests.post(
            url=settings.JASPER_REST + "reportExecutions",
            headers={
                "Authorization": "Basic " + token,
                "Accept": "application/json",
                "Content-Type": "application/xml",
            },
            data=data,
        )
        data = response.json()
        # print data
        try:
            request_id = data.get("requestId")
            export_id = data.get("exports")[0].get("id")
            status = data.get("status")
        except Exception as e:
            return False, data

        if status == "ready":
            report_url = (
                settings.JASPER_REST
                + "reportExecutions/{request_id}/exports/{export_id}/outputResource".format(
                    request_id=request_id, export_id=export_id
                )
            )

            report_resp = requests.get(
                url=report_url, headers=response.headers, cookies=response.cookies
            )
            return True, report_resp.content
        else:
            return False, data
