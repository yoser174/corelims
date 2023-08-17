# encoding=utf-8


# -*- coding: utf-8 -*-
###############################
# Mindray BC6800
#
# auth: Yoserizal
# date: 17 Agustus 2023
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
####
# fix:

from ..db.my_db import my_db
import serial
import time
import logging
from datetime import datetime
import socket
import hl7
import MySQLdb


import sys

# reload(sys)
# sys.setdefaultencoding('utf-8')


DRIVER_NAME = "BC5000"
DRIVER_VERSION = "0.0.0.1"

SEND_ACK_MSG = False

ENCODING = "utf-8"
NULL = b"\x00"
STX = b"\x02"
ETX = b"\x03"
EOT = b"\x04"
ENQ = b"\x05"
ACK = b"\x06"
NAK = b"\x15"
ETB = b"\x17"
LF = b"\x0A"
CR = b"\x0D"
CRLF = CR + LF
VT = b"\x0B"
FS = b"\x1C"
RECORD_SEP = b"\x0D"  # \r #
FIELD_SEP = b"\x7C"  # |  #
REPEAT_SEP = b"\x5C"  # \  #
COMPONENT_SEP = b"\x5E"  # ^  #
ESCAPE_SEP = b"\x26"  # &  #


TCP_IP = "127.0.0.1"
TCP_PORT = 5005
BUFFER_SIZE = 1024

MY_USER = "mwconn"
MY_PASS = "connmw"
MY_DB = "ciremai"


class ZYBIO(object):
    def __init__(
        self,
        server,
        db,
        instrument_id,
        name,
        connection_type,
        driver,
        serial_baud_rate,
        serial_data_bit,
        serial_port,
        serial_stop_bit,
        tcp_conn_type,
        tcp_host,
        tcp_port,
    ):
        self.message = ""
        logging.info(DRIVER_NAME + " - " + DRIVER_VERSION + " loaded.")
        logging.info("connection type: [%s]" % connection_type)
        self.server = server
        MY_DB = db
        self.instrument_id = instrument_id
        self.connection_type = connection_type
        self.tcp_conn_type = tcp_conn_type
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port

        # mysql connection
        self.my_conn = my_db(self.server, MY_DB)

    def handlemsg(self, msg):
        """handle raw message"""
        if msg.startswith(VT.decode(ENCODING)) and msg.endswith(
            FS.decode(ENCODING) + CR.decode(ENCODING)
        ):
            message = msg[1:-3]
        else:
            message = msg

        logging.info(message)
        h = hl7.parse(message)
        message_type = str(h.segment("MSH")[9])
        msh10 = str(h.segment("MSH")[10])

        if message_type == "ORU^R01":
            logging.info("proses result patient..")
            sample_no = h.segment("OBR")[3] or ""
            logging.info(f"Try parsing result [{sample_no}] and insert to DB..")
            try:
                for obx in h["OBX"]:
                    tes_code = obx[3][0][1] or ""
                    tes_result = obx[5] or ""
                    tes_unit = obx[6] or ""
                    tes_ref = obx[7] or ""
                    tes_flag = obx[8] or ""
                    self.my_conn.insert_result(
                        sample_no,
                        tes_code,
                        tes_result,
                        tes_ref,
                        tes_unit,
                        tes_flag,
                        self.instrument_id,
                    )
            except Exception as e:
                pass

            if SEND_ACK_MSG:
                # proses send ACK

                ts = datetime.now().strftime("%Y%m%d%H%M%S")
                ack_msg = (
                    VT
                    + "MSH|$~&|LIS||||"
                    + str(ts)
                    + "||"
                    + message_type
                    + "|"
                    + msh10
                    + "|P|2.3.1||||||UNICODE\r"
                )
                ack_msg += "MSA|AA|" + msh10 + "\r" + FS + CR

                logging.info(f"send ACK mesage >> {ack_msg}")

                self.conn.send(ack_msg)

        elif message_type == "ORM^O01":
            logging.info("instrument query for sample, prepare message for reply..")
            # order request for sampel ID
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            send_application = str(h.segment("MSH")[3])
            send_facility = str(h.segment("MSH")[4])
            control_id = str(h.segment("MSH")[10])
            sample_id = str(h.segment("ORC")[3])

            # get patient info
            (
                pat_id,
                name,
                dob,
                sex,
                doctor,
                diagnosis,
                origin,
            ) = self.my_conn.get_patient_id(sample_no)
            send_message = (
                "MSH|^~\&|"
                + send_application
                + "|"
                + send_facility
                + "|||"
                + str(ts)
                + "||ORR^O02||P|2.3.1||||||UNICODE\r"
            )
            send_message += "MSA|AA|" + control_id + "\r"
            send_message += (
                "PID|1||"
                + pat_id
                + "^^^^MR||"
                + name
                + "^"
                + name
                + "||"
                + dob
                + "|"
                + sex
                + "\r"
            )
            send_message += "PV1|1||" + origin + "^^|||||||||||||||||\r"
            send_message += "ORC|AF||" + sample_id + "\r"
            send_message += (
                "OBR|1|"
                + sample_no
                + "||00001^Automated Count^99MRC||"
                + str(ts)
                + "||||||||"
                + str(ts)
                + "||||||||||HM||||||||\r"
            )

            send_message = VT + send_message + FS + CR
            logging.info(f"send message >>{send_message}")

            self.conn.send(send_message)

        else:
            logging.info(f"Message unknown [{message_type}] : {message}")
            # proses send ACK
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            ack_msg = (
                VT
                + "MSH|$~&|LIS||||"
                + str(ts)
                + "||"
                + message_type
                + "|"
                + msh10
                + "|P|2.3.1||||||UNICODE\r"
            )
            ack_msg += "MSA|AA|" + msh10 + "\r" + FS + CR

            logging.info("send ACK mesage >> {ack_msg}")

            self.conn.send(ack_msg)

    def open(self):
        if self.connection_type == "TCP":
            while 1:
                if self.tcp_conn_type == "S":
                    if self.tcp_host == "None" or not self.tcp_host:
                        self.tcp_host = "0.0.0.0"
                    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.s.bind((self.tcp_host, self.tcp_port))
                    logging.info(
                        f"starting TCP server [{self.tcp_host}:{ self.tcp_port}] ..."
                    )
                    logging.info("listening...")
                    self.s.listen(1)
                    self.conn, self.addr = self.s.accept()

                    logging.info("Connection address: [%s]", self.addr)

                elif self.tcp_conn_type == "C":
                    self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    res = self.conn.connect((self.tcp_host, self.tcp_port))

                while 1:
                    data = self.conn.recv(BUFFER_SIZE)
                    if not data:
                        break
                    if isinstance(data, str):
                        data = data.encode("utf-8")
                    if data != STX:
                        logging.info(f"Data: [{data}]")
                        logging.info(f"Len[{len(data)}]")
                        self.message += data.decode(ENCODING)
                        self.message = str(self.message).replace(
                            STX.decode(ENCODING), ""
                        )
                        logging.info(f"Message: [{self.message}]")
                        logging.info(f"Len{len(self.message)}]")

                    if str(self.message).startswith(VT.decode(ENCODING)) and str(
                        self.message
                    ).endswith(FS.decode(ENCODING) + CR.decode(ENCODING)):
                        logging.info("proses message")
                        self.handlemsg(self.message)
                        self.message = ""

                self.conn.close()
                logging.info("Socked closed. sleep 1s then restart listenning.")
                time.sleep(1)

        else:
            logging.error("ZYBIO only support connection type TCP")

        # close db connection
        self.my_conn.close()
