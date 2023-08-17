""" CTKRAFIA.py driver"""
###############################
# BW300 driver
#
# auth: Yoserizal
# date: 17 Agusutus 2023
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

import logging
import serial
import sys
from ..db.my_db import my_db

# reload(sys)
# sys.setdefaultencoding('ISO-8859-1')


DRIVER_NAME = "CTKRAFIA"
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
LF = b"\x0A"
CR = b"\x0D"
CRLF = CR + LF
VT = b"\x0B"
ESC = b"\x1B"
FS = b"\x1C"
RECORD_SEP = b"\x0D"  # \r #
FIELD_SEP = b"\x7C"  # |  #
REPEAT_SEP = b"\x5C"  # \  #
COMPONENT_SEP = b"\x5E"  # ^  #
ESCAPE_SEP = b"\x26"  # &  #


TCP_IP = "127.0.0.1"
TCP_PORT = 5005
BUFFER_SIZE = 1024
SOCKET_TIMEOUT = 5

MY_USER = "mwconn"
MY_PASS = "connmw"


class CTKRAFIA(object):
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
        logging.info(f"{DRIVER_NAME}  - {DRIVER_VERSION} loaded.")
        logging.info("connection type: [%s]", connection_type)
        self.server = server
        self.instrument_id = instrument_id
        self.connection_type = connection_type
        self.MY_DB = db
        self.serial_port = serial_port or "COM10"
        self.serial_baud_rate = serial_baud_rate or 115200
        self.serial_stop_bit = serial_stop_bit or 8
        self.serial_data_bit = serial_data_bit or 1
        self.serial_parity = None

        # mysql connection
        logging.info("init mysql connection [%s]", self.MY_DB)
        self.my_conn = my_db(self.server, self.MY_DB)

    def proses_raw(self, message):
        """proses raw message dari alat"""
        msg_spl = message[1 : len(message) - 2].split("\n")
        logging.info(msg_spl)
        date = ""
        sample_no = ""
        test_code = ""
        rest_result = ""
        for d in msg_spl:
            logging.info(d)
            # if str(d).startswith("DATE:"):
            #     date = str(d).replace("DATE:", "").strip()
            #     logging.info(f"DATE:[{date}]")
            # elif str(d).startswith("NO.:"):
            #     sample_no = str(d).replace("NO.:", "").strip()
            #     logging.info(f"NO.:[{sample_no}]")
            # else:
            #     logging.info(f"data result [{d}]")
            #     test_code = str(d)[1:4].strip()
            #     test_result = str(d)[7:11].strip()
            #     logging.info(f"result data [{test_code}][{test_result}]")
            #     tes_ref = ""
            #     tes_unit = ""
            #     tes_flag = ""
            #     self.my_conn.insert_result(
            #         sample_no,
            #         test_code,
            #         test_result,
            #         tes_ref,
            #         tes_unit,
            #         tes_flag,
            #         self.instrument_id,
            #     )

    def open(self):
        """open connection"""
        if self.connection_type == "SER":
            logging.info(f"connection > Serial [{self.serial_port}]")
            parity = serial.PARITY_NONE

            ser = serial.Serial(
                port=self.serial_port,
                baudrate=self.serial_baud_rate,
                parity=parity,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
            )

            with ser.is_open():
                while True:
                    message = ""
                    while True:
                        data = ""
                        while ser.in_waiting() > 0:
                            data += ser.read(1)
                        if not data:
                            break
                        logging.info(f"data from client [{data}]")
                        message += data
                        if message.startswith(
                            ESC.decode(ENCODING)
                        ) and message.endswith(NULL.decode(ENCODING)):
                            logging.info(
                                f"data lengkap start with ESC end with NULL, olah data yang diterima [{message}]"
                            )
                            self.proses_raw(message)

        else:
            logging.error("CTK RAFIA only support connection type SERIAL")

        # close db connection
        sys.exit(0)
