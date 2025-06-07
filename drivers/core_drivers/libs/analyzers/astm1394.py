# -*- coding: utf-8 -*-
"""
astm1394.py - A driver for ASTM 1394 protocol communication.
This driver handles communication with ASTM 1394 instruments, processing messages
and sending queries based on received data.
"""


import time
import logging
from datetime import datetime
import sys

# from ..db.my_db import my_db
from astm import astm

# reload(sys)
# sys.setdefaultencoding('ISO-8859-1')


DRIVER_NAME = "astm1394"
DRIVER_VERSION = "0.0.1"

ENCODING = "latin-1"
NULL = b"\x00"
STX = b"\x02"
ETX = b"\x03"
EOT = b"\x04"
ENQ = b"\x05"
ACK = b"\x06"
NAK = b"\x15"
ETB = b"\x17"
LF = b"\x0a"
CR = b"\x0d"
CRLF = CR + LF
VT = b"\x0b"
FS = b"\x1c"
RECORD_SEP = b"\x0d"  # \r #
FIELD_SEP = b"\x7c"  # |  #
REPEAT_SEP = b"\x5c"  # \  #
COMPONENT_SEP = b"\x5e"  # ^  #
ESCAPE_SEP = b"\x26"  # &  #


TCP_IP = "127.0.0.1"
TCP_PORT = 5005
BUFFER_SIZE = 1024

MY_USER = "mwconn"
MY_PASS = "connmw"


class astm1394(object):

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
        self.instrument_id = instrument_id
        self.connection_type = connection_type
        self.tcp_conn_type = tcp_conn_type
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.name = name
        self.driver = driver
        self.serial_baud_rate = serial_baud_rate
        self.serial_data_bit = serial_data_bit
        self.serial_port = serial_port
        self.serial_stop_bit = serial_stop_bit
        self.astm = astm.astm(
            self.connection_type, self.tcp_conn_type, self.tcp_host, self.tcp_port
        )

    def sample_query(self, sample_no, sender):
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        logging.info(sender)
        h = "H|\^&|||" + "^".join(map(str, sender)) + "|||||||SA|1394-97|" + ts + "\r"
        logging.info(h)
        # generate PID
        pat_id, name, dob, sex, doctor, diagnosis, origin = self.my_conn.get_patient_id(
            sample_no
        )
        p = (
            "P|1||"
            + pat_id
            + "||"
            + name
            + "^"
            + name
            + "^"
            + name
            + "||"
            + dob
            + "|"
            + sex
            + "|||||"
            + doctor
            + "|||||"
            + diagnosis
            + "||0001|||||A1|002||||||||\r"
        )
        logging.info(p)
        tes_arr = self.my_conn.get_test_array(sample_no, self.instrument_id)
        tes_dump = ""
        o = ""
        if tes_arr:
            rec = 0
            for tes in tes_arr:
                if rec == 0:
                    tes_dump += str(rec + 1) + "^" + str(tes[0]) + "^1^1"
                else:
                    tes_dump += "\\" + str(rec + 1) + "^" + str(tes[0]) + "^1^1"
                rec += 1
        o = (
            "O|1|"
            + sample_no
            + "^1^1|"
            + sample_no
            + "|"
            + tes_dump
            + "|R|"
            + ts
            + "|"
            + ts
            + "||||||||serum|"
            + str(doctor)
            + "|"
            + str(origin)
            + "|1|||||||Q|||||\r"
        )
        l = "L|1|N"
        logging.info(o)
        astm_msg = h + p + o + l
        logging.info(astm_msg)
        self.astm.send_enq()
        data = self.astm.listen()
        if data == ACK:
            self.astm.send_msg(astm_msg)
            data = self.astm.listen()
            if data == ACK:
                self.astm.send_eot()

    def handlemsg(self, msg):
        logging.info("handle message....[%s]" % msg)
        msg = "1" + msg
        message = b"".join([STX, msg, self.astm.make_checksum(msg), CR, LF])
        message = self.astm.decode(message)
        logging.info(message)
        order_id = 0
        q_o = ""
        sample_query = False

        for m in message:
            logging.info(m)
            if m[0] == "H":
                sender = m[4]
            if m[0] == "O":
                q_o = m
                # sample_no = m[2][0]
                sample_no = m[3] or m[2][0]
            if m[0] == "R":
                tes_code = m[2][0]
                tes_result = m[3][0]
                tes_unit = m[4]
                tes_ref = ""
                tes_flag = ""
                self.my_conn.insert_result(
                    sample_no,
                    tes_code,
                    tes_result,
                    tes_ref,
                    tes_unit,
                    tes_flag,
                    self.instrument_id,
                )
            if m[0] == "Q":
                q_sample_no = m[2][1]
                sample_query = True

        if sample_query:
            logging.info("Sample Query: [%s]" % q_sample_no)
            self.sample_query(q_sample_no, sender)
        return True

    def open(self):
        if self.connection_type == "TCP":
            logging.info(
                "Client connected. [%s:%s] ..." % (self.tcp_host, self.tcp_port)
            )
            while 1:
                while 1:
                    data = self.astm.conn.recv(BUFFER_SIZE)
                    if not data:
                        break
                    if isinstance(data, unicode):
                        data = data.encode("utf-8")
                    logging.info("Data: [{}]".format(data))
                    logging.info("data len [%s]" % str(len(data)))

                    if data == ENQ:
                        logging.info("<< ENQ")
                        self.astm.send_ack()

                    elif data.startswith(STX) and data.endswith(CRLF):
                        logging.info("got data")
                        self.astm.send_ack()
                        logging.info(data)
                        self.message += str(data[2:-5]).replace(ETB, "")
                        logging.info(str(data[2:-5]).replace(ETB, ""))

                    elif (data == EOT) or (data == EOT + ENQ):
                        logging.info("Proses message:")
                        logging.info(str(self.message))
                        self.handlemsg(self.message)
                        self.message = ""

                    elif data.endswith(EOT):
                        logging.info("data ends with EOT")
                        self.astm.send_ack()
                        logging.info(data)
                        self.message += str(data).replace(EOT, "")
                        logging.info(str(self.message))
                        try:
                            logging.info("try to processing message")
                            self.handlemsg(self.message)
                        except Exception as e:
                            logging.error(
                                "Failed when processing message [%s] with error [%s]"
                                % (str(self.message), str(e))
                            )
                        self.message = ""

                    else:
                        if data:
                            self.message += data
                        self.astm.send_ack()

                self.astm.conn.close()
                logging.info("Socked closed. sleep 1s then restart listenning.")
                time.sleep(1)

        else:
            logging.error("BS4800 only support connection type TCP")

        # close db connection
        self.my_conn.close()

        sys.exit(0)
