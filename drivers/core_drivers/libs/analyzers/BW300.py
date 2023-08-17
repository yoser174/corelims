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
import socket
import sys
from ..db.my_db import my_db

# reload(sys)
# sys.setdefaultencoding('ISO-8859-1')


DRIVER_NAME = "BW300"
DRIVER_VERSION = "0.0.0.1"

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


class BW300(object):
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
        self.tcp_conn_type = tcp_conn_type
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        MY_DB = db
        self.conn = None
        self.addr = None
        self.socket = None

        # mysql connection
        logging.info("init mysql connection [%s]", MY_DB)
        self.my_conn = my_db(self.server, MY_DB)

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
            if str(d).startswith("DATE:"):
                date = str(d).replace("DATE:", "").strip()
                logging.info(f"DATE:[{date}]")
            elif str(d).startswith("NO.:"):
                sample_no = str(d).replace("NO.:", "").strip()
                logging.info(f"NO.:[{sample_no}]")
            else:
                logging.info(f"data result [{d}]")
                test_code = str(d)[1:4].strip()
                test_result = str(d)[7:11].strip()
                logging.info(f"result data [{test_code}][{test_result}]")
                tes_ref = ""
                tes_unit = ""
                tes_flag = ""
                self.my_conn.insert_result(
                    sample_no,
                    test_code,
                    test_result,
                    tes_ref,
                    tes_unit,
                    tes_flag,
                    self.instrument_id,
                )

    def open(self):
        logging.info(
            f"create connection [{self.tcp_conn_type}][{self.tcp_host}][{self.tcp_port}]"
        )
        if self.tcp_conn_type == "S":
            logging.info("connection > TCP server")
            if self.tcp_host == "None" or not self.tcp_host:
                self.tcp_host = "0.0.0.0"
            logging.info(f"create socket [{self.tcp_host}:{self.tcp_port}]")
            server_socket = socket.socket()
            server_socket.bind((self.tcp_host, self.tcp_port))
            server_socket.listen(1)
            logging.info("listening...")
            conn, address = server_socket.accept()
            logging.info(f"Connection from:{address}")
            while True:
                message = ""
                while True:
                    data = conn.recv(1024).decode(ENCODING)
                    if not data:
                        break
                    logging.info(f"data from client [{data}]")
                    message += data
                    if message.startswith(STX.decode(ENCODING)) and message.endswith(
                        ETX.decode(ENCODING)
                    ):
                        logging.info(
                            f"data lengkap start with STX end with ETX, olah data yang diterima [{message}]"
                        )
                        self.proses_raw(message)

                    data = None

            conn.close()

        elif self.tcp_conn_type == "C":
            logging.info("Connection is Client.")
            logging.info(
                "trying to make connection to [%s:%s] ..."
                % (str(self.tcp_host), str(self.tcp_port))
            )
            try:
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.settimeout(SOCKET_TIMEOUT)
                self.conn.connect((self.tcp_host, self.tcp_port))
            except Exception as e:
                logging.error("Failed [%s]" % str(e))
                sys.exit(0)

                # self.conn.sendall(data)

        else:
            logging.error("BS4800 only support connection type TCP")

        # close db connection
        sys.exit(0)
