"""
Copyright (c) 2025, Yoserizal
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE"""

from datetime import datetime
import logging
import socket
import time
import sys

from ..api.bearer_api_client import BearerApiClient


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

DRIVER_NAME = "astm"
DRIVER_VERSION = "0.0.3"

BUFFER_SIZE = 1024
SOCKET_TIMEOUT = 5


class astm:
    """ASTM Protocol Handler Class"""

    def __init__(
        self,
        api_url,
        token,
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
        logging.info("%s - %s loaded.", DRIVER_NAME, DRIVER_VERSION)
        logging.info("connection type: [%s]", connection_type)
        self.api_url = api_url
        self.token = token
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

        self.api_conn = BearerApiClient(token=self.token, api_url=self.api_url)

        # fix
        if self.tcp_conn_type == "S":
            self.tcp_host = "0.0.0.0"

        if self.tcp_conn_type == "S":
            logging.info(
                "Connection is Server [%s:%s], open socket...",
                self.tcp_host,
                self.tcp_port,
            )
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.tcp_host, self.tcp_port))
            self.s.listen(1)
            logging.info("Ok")
            self.conn, self.addr = self.s.accept()
            logging.info("Connection address: [%s]", self.addr)

        elif self.tcp_conn_type == "C":
            logging.info("Connection is Client.")
            logging.info(
                "trying to make connection to [%s:%s] ...",
                str(self.tcp_host),
                str(self.tcp_port),
            )
            try:
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.settimeout(SOCKET_TIMEOUT)
                self.conn.connect((self.tcp_host, self.tcp_port))
            except (socket.error, OSError) as e:
                logging.error("Failed [%s]", str(e))
                sys.exit(0)

    def send_enq(self):
        """Send ENQ (Enquiry) to the instrument."""
        logging.info(">>ENQ")
        self.conn.send(ENQ)

    def send_eot(self):
        """Send EOT (End of Transmission) to the instrument."""
        logging.info(">>EOT")
        self.conn.send(EOT)

    def send_ack(self):
        """Send ACK (Acknowledge) to the instrument."""
        logging.info(">>ACK")
        self.conn.send(ACK)

    def send_msg(self, msg):
        """Send a message to the instrument."""
        logging.info(">>%s", msg)
        data = b"".join((str(1 % 8).encode(), msg, CR, ETX))
        data_tx = b"".join([STX, data, self.make_checksum(data), CR, LF])
        logging.info("data to TX:%s", data_tx)
        self.conn.send(data_tx)
        time.sleep(0.01)

    def listen(self):
        """Listen for incoming data from the instrument."""
        logging.info("listening..")
        data = ""
        while data == "":
            data = self.conn.recv(BUFFER_SIZE)
        return data

    def make_checksum(self, message):
        """Calculate the checksum for a given message."""
        if not isinstance(message[0], int):
            message = map(ord, message)
        return hex(sum(message) & 0xFF)[2:].upper().zfill(2).encode()

    def checksum_verify(self, message):
        """Verify the checksum of a given ASTM message."""
        if not (message.startswith(STX) and message.endswith(CRLF)):
            logging.error(
                "Malformed ASTM message. Expected that it will started"
                " with %x and followed by %x%x characters. Got: %r"
                " " % (ord(STX), ord(CR), ord(LF), message)
            )
            return False
        _stx, frame_cs = message[0], message[1:-2]
        frame, cs = frame_cs[:-2], frame_cs[-2:]
        ccs = self.make_checksum(frame)
        if cs == ccs:
            logging.info("Checksum is OK")
            return True
        else:
            logging.warning("Checksum failure: expected %r, calculated %r", cs, ccs)
            return False

    def decode(self, data):
        if data.startswith(
            STX.decode(ENCODING)
        ):  # may be decode message \x02...\x03CS\r\n
            records = self.decode_message(data)
            return records
        byte = data[:1]
        if byte.isdigit():
            records = self.decode_frame(data)
            return records
        return [self.decode_record(data)]

    def decode_message(self, message):
        if not isinstance(message, bytes):
            logging.error("bytes expected, got %r", message)
        if not (message.startswith(STX) and message.endswith(CRLF)):
            logging.error(
                "ERROR Malformed ASTM message. Expected that it will started with %x and followed by %x%x characters. Got: %r"
                % (ord(STX), ord(CR), ord(LF), message)
            )
        _stx, frame_cs = message[0], message[1:-2]
        frame, cs = frame_cs[:-2], frame_cs[-2:]
        ccs = self.make_checksum(frame)
        assert cs == ccs, "Checksum failure: expected %r, calculated %r" % (cs, ccs)
        records = self.decode_frame(frame)
        return records

    def decode_frame(self, frame):
        if not isinstance(frame, bytes):
            logging.error("bytes expected, got %r" % frame)
        if frame.endswith(CR.decode(ENCODING) + ETX.decode(ENCODING)):
            frame = frame[:-2]
        elif frame.endswith(ETB):
            frame = frame[:-1]
        else:
            logging.warning(
                "Incomplete frame data %r. Expected trailing <CR><ETX> or <ETB> chars"
                % frame
            )
        seq = frame[:1]
        if not seq.isdigit():
            logging.warning(
                "Malformed ASTM frame. Expected leading seq number %r" % frame
            )
        seq, records = int(seq), frame[1:]
        return [
            self.decode_record(record)
            for record in records.split(RECORD_SEP.decode(ENCODING))
        ]

    def decode_record(self, record):
        fields = []
        for item in record.split(FIELD_SEP.decode(ENCODING)):
            if REPEAT_SEP.decode(ENCODING) in item:
                item = self.decode_repeated_component(item)
            elif COMPONENT_SEP.decode(ENCODING) in item:
                item = self.decode_component(item)
            else:
                item = item
            fields.append([None, item][bool(item)])
        return fields

    def decode_component(self, field):
        return [
            [None, item][bool(item)]
            for item in field.split(COMPONENT_SEP.decode(ENCODING))
        ]

    def decode_repeated_component(self, component):
        return [
            self.decode_component(item)
            for item in component.split(REPEAT_SEP.decode(ENCODING))
        ]

    def encode_message(self, seq, records):
        data = RECORD_SEP.join(self.encode_record(record) for record in records)
        data = b"".join((str(seq % 8).encode(), data, CR, ETX))
        return b"".join([STX, data, self.make_checksum(data), CR, LF])

    def encode_record(self, record):
        fields = []
        _append = fields.append
        for field in record:
            if isinstance(field, bytes):
                _append(field)
            elif isinstance(field, str):
                _append(field.encode(encoding))
            elif isinstance(field, Iterable):
                _append(encode_component(field, encoding))
            elif field is None:
                _append(b"")
            else:
                _append(str(field).encode(encoding))
        return FIELD_SEP.join(fields)

    def make_chunks(self, s, n):
        iter_bytes = (s[i : i + 1] for i in range(len(s)))
        return [
            b"".join(item) for item in izip_longest(*[iter_bytes] * n, fillvalue=b"")
        ]

    def split(self, msg, size):
        stx, frame, msg, tail = msg[:1], msg[1:2], msg[2:-6], msg[-6:]
        assert stx == STX
        assert frame.isdigit()
        assert tail.endswith(CRLF)
        assert size is not None and size >= 7
        frame = int(frame)
        chunks = make_chunks(msg, size - 7)
        chunks, last = chunks[:-1], chunks[-1]
        idx = 0
        for idx, chunk in enumerate(chunks):
            item = b"".join([str((idx + frame) % 8).encode(), chunk, ETB])
            yield b"".join([STX, item, make_checksum(item), CRLF])
        item = b"".join([str((idx + frame + 1) % 8).encode(), last, CR, ETX])
        yield b"".join([STX, item, make_checksum(item), CRLF])

    def db_query(self, sql):
        conn = sqlite3.connect("cobas6k.db")
        cursor = conn.cursor()
        logging.info("Query - %s " % sql)
        cursor.execute(sql)
        r = cursor.fetchall()
        conn.close()
        logging.info("Return = %s" % r)
        return r

    def db_delexists(self, sid, tesno):
        logging.info("deleting existing data")
        conn = sqlite3.connect("cobas6k.db")
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM GUI_RESULTS WHERE SID = '"
            + str(sid)
            + "' AND TestNo = '"
            + str(tesno)
            + "' "
        )
        conn.commit()
        conn.close()

    def db_insert(self, sql, resdata):
        sid = resdata[0] or ""
        tesno = resdata[1] or ""
        if sid != "" and tesno != "":
            logging.info("delete existing data (%s,%s)" % (sid, tesno))
            self.db_delexists(sid, tesno)

        conn = sqlite3.connect("cobas6k.db")
        cursor = conn.cursor()
        logging.info("Insert - %s data:%s" % (sql, resdata))
        cursor.execute(sql, resdata)
        conn.commit()
        conn.close()

    def db_insert_raw(self, sql, resdata):
        conn = sqlite3.connect("cobas6k.db")
        cursor = conn.cursor()
        logging.info("Insert - %s data:%s" % (sql, resdata))
        cursor.execute(sql, resdata)
        conn.commit()
        conn.close()

    def my_insert(self, sql):
        logging.info("IP MySQL [%s]" % self.my_server)
        logging.info(sql)
        try:
            conn = MySQLdb.connect(
                host=self.my_server, user=MY_USER, passwd=MY_PASS, db=MY_DB
            )
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
        except MySQLdb.Error as e:
            logging.error(e)
            conn.rollback()
        conn.close()

    def get_testdesc(self, testno):
        logging.info("getting test description..")
        try:
            tesdesc = self.db_query(
                "SELECT Desc FROM ALL_SET_TESTS WHERE TestNo = '" + testno + "' "
            )
            return str(tesdesc[0][0])
        except Exception as e:
            logging.error(
                "Gagal dapat test code [%s] cek cobas6k.db edit table `ALL_SET_TEST` sesuaikan dengan HOST_CODE alat dari System > Utilities > test code. "
                % testno
            )
            sys.exit(1)

    def save_raw(self, direction, msg):
        logging.info("saving raw data [%s,%s]" % (direction, msg))
        sql = "INSERT INTO RAW_DATA (direction,message) VALUES (?,?)"
        dt = [str(direction), str(msg)]
        self.db_insert_raw(sql, dt)
        return True

    def handleTSReq(self, msg):
        logging.info("handle TS Request..")
        q_sid = ""
        q_seq = ""
        q_rackid = ""
        q_posno = ""
        q_racktype = ""
        q_conttype = ""
        sql = ""
        is_sent = False
        for line in msg:
            logging.info(line)
            if line[0] == "Q":
                logging.info(" Q - Getting SID..")
                q_sid = str(line[2][2]).strip() or ""
                logging.info(' SID is "%s"' % q_sid)
                # cek apakah sudah pernah kirim
                sql = (
                    "SELECT count(id) jum FROM SAMPLE_SENT WHERE sample_no = '"
                    + str(q_sid)
                    + "'"
                )
                res = self.db_query(sql)

                logging.info(res[0][0])
                if int(res[0][0]) > 0:
                    logging.info("Sudah pernah dikirim.")
                    is_sent = True

                q_seq = line[2][3] or ""
                q_rackid = line[2][4] or ""
                q_posno = line[2][5] or ""
                q_racktype = line[2][7] or ""
                q_conttype = line[2][8] or ""
                logging.info(
                    "  -> seq:%s RackNo-Pos: (%s - %s) Racktype-ContainerType:(%s-%s)"
                    % (q_seq, q_rackid, q_posno, q_racktype, q_conttype)
                )

        logging.info(" getting config name TS..")
        sql = "SELECT char_value FROM config WHERE name = 'TS'"
        res = self.db_query(sql)
        if str(res[0][0]) == "ALL_SET_TESTS":
            """
                        H|\^&|||Host^1|||||Modular|TSDWN^REPLY|P|1
            P|1||PatID|||||M||||||40^Y
            O|1|SampleID|Seq^Rack^Pos^^S1^SC|^^^1^1\^^^2^1|R||20170508204635||||A||||1||||||||||O
            C|1|L|Comm1^Comm2^Comm3^Comm4^Comm5|G
            L|1|N
            """
            # parsing Header
            ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            ts_reply = "H|\^&|||Host^1|||||cobas6000|TSDWN^REPLY|P|1\r"
            ts_reply += "P|1|||||||U||||||^\r"

            comm1 = ""
            comm2 = ""
            comm3 = ""
            comm4 = ""
            comm5 = ""
            logging.info("ALL_SET_TESTS : get SET TEST and send it to instrument")
            sql = "SELECT TestNo,Dilution FROM ALL_SET_TESTS WHERE Active = 1"
            res = self.db_query(sql)
            tes_dump = ""
            if not is_sent:
                rec = 0
                for tes in res:
                    if rec == 0:
                        tes_dump += "^^^" + str(tes[0]) + "^" + str(tes[1])
                    else:
                        tes_dump += "\^^^" + str(tes[0]) + "^" + str(tes[1])
                    rec += 1
            logging.info(tes_dump)
            ts_reply += (
                "O|1|"
                + str(q_sid).rjust(22)
                + "|"
                + str(q_seq)
                + "^"
                + str(q_rackid)
                + "^"
                + str(q_posno)
                + "^^"
                + str(q_racktype)
                + "^"
                + str(q_conttype)
                + "|"
                + str(tes_dump)
                + "|R||"
                + str(ts)
                + "||||A||||1||||||||||O\r"
            )
            logging.info(" -> Generate comment field")
            sql = "SELECT char_value FROM config WHERE name = 'TS_ALL_SET_TESTS_COMM1'"
            res = self.db_query(sql)
            comm1 = res[0][0] or ""
            sql = "SELECT char_value FROM config WHERE name = 'TS_ALL_SET_TESTS_COMM2'"
            res = self.db_query(sql)
            comm2 = res[0][0] or ""
            sql = "SELECT char_value FROM config WHERE name = 'TS_ALL_SET_TESTS_COMM3'"
            res = self.db_query(sql)
            comm3 = res[0][0] or ""
            sql = "SELECT char_value FROM config WHERE name = 'TS_ALL_SET_TESTS_COMM4'"
            res = self.db_query(sql)
            comm4 = res[0][0] or ""
            sql = "SELECT char_value FROM config WHERE name = 'TS_ALL_SET_TESTS_COMM5'"
            res = self.db_query(sql)
            comm5 = res[0][0] or ""
            # comment
            ts_reply += (
                "C|1|L|"
                + str(comm1)
                + "^"
                + str(comm2)
                + "^"
                + str(comm3)
                + "^"
                + str(comm4)
                + "^"
                + str(comm5)
                + "|G\r"
            )
            ts_reply += "L|1|N"
            logging.info("TS REPLY:%s" % ts_reply)
            # if DB_OFFLINE:
            #     self.save_raw("OUT", ts_reply)
            self.send_enq()
            data = self.listen()
            if data == ACK:
                self.send_msg(ts_reply)
                data = self.listen()
                if data == ACK:
                    self.send_eot()
                    logging.info("insert sample_no yang sudah berhasil dikirim.")
                    # insert SAMPLE_SENT
                    sql = "INSERT INTO SAMPLE_SENT (sample_no) VALUES (?)"
                    logging.info("data [%s]" % str(q_sid))
                    sidno_data = [str(q_sid)]
                    self.db_insert_raw(sql, sidno_data)

        return True

    def handle_message(self, msg):
        """Handle incoming ASTM message."""
        # if DB_OFFLINE:
        #     self.save_raw("IN", str(msg))
        o_sid = ""  # sample ID
        o_time = ""  # specimen colection date\time
        r_testno = ""  # test No
        r_dilut = ""  # dilution
        r_predilut = ""  # pre-dilut
        r_tes = ""  # dummy tes
        r_result = ""  # measurement data
        r_unit = ""  # unit
        r_flag = ""  # flag A=Abnormal L=Below normal H=Higher than normal high N=Normal
        # LL=Lower than panic low HH=higer than panic high
        r_status = ""  # status result C= crr. of prev.trasm.results F=Final results
        r_operator = ""  # operator identification
        r_insid = ""  # instrument identification
        o_lastmod = ""  # last modified date result

        for line in msg:
            logging.info(line)
            if line[0] == "H":
                logging.info("=> Header message")
                try:
                    h_instname = str(line[4][0] + "." + line[4][1]).strip() or ""
                    logging.info(line[10])
                    if line[10][0] == "RSUPL" and (
                        line[10][1] == "REAL" or line[10][1] == "BATCH"
                    ):
                        logging.info("Message is RESULT UPLOAD")
                    elif line[10][0] == "TSREQ" and line[10][1] == "REAL":
                        logging.info("Message is TEST SELECTION request.")
                        self.handleTSReq(msg)
                        return True
                    else:
                        logging.info("!!! Mesage not expeted, skip it.")
                        return False
                except Exception as e:
                    logging.info(
                        "error pasing H segment [%s][%s]" % (str(line), str(e))
                    )
            elif line[0] == "P":
                logging.info("=> Patient message")
            elif line[0] == "C":
                logging.info("=> Comment message")
            elif line[0] == "L":
                logging.info("=> Terminate message")
            elif line[0] == "O":
                logging.info("=> Order message")
                try:
                    o_sid = str(line[2]).strip() or ""
                    o_reslastmoddate = str(line[22]).strip() or ""
                    o_lastmod = str(line[22]).strip() or ""
                    o_sampletype = str(line[11]).strip() or ""
                except Exception as e:
                    logging.error(
                        "Failed parsing O segment [%s][%s]" % (str(line), str(e))
                    )

            elif line[0] == "R":
                logging.info("=> Test result message")
                try:
                    r_tes = str(line[2][3]).split("/")
                    r_testno = r_tes[0] or ""
                    r_dilut = r_tes[1] or ""
                    r_predilut = r_tes[2] or ""
                    r_result = line[3] or ""
                    r_unit = line[4] or ""
                    r_flag = line[6] or ""
                    r_status = line[8] or ""
                    r_operator = line[10] or ""
                    r_insid = line[13] or ""
                except Exception as e:
                    logging.error(
                        "Failed parsing O segment [%s][%s]" % (str(line), str(e))
                    )

                res_num = r_result

                s = o_lastmod
                o_reslastmoddate = (
                    s[0:4]
                    + "-"
                    + s[4:6]
                    + "-"
                    + s[6:8]
                    + " "
                    + s[8:10]
                    + ":"
                    + s[10:12]
                    + ":"
                    + s[12:14]
                )
                logging.info("Posting results...")
                self.api_conn.insert_result(
                    sample_no=o_sid,
                    test_code=r_testno,
                    test_result=res_num,
                    test_ref="",
                    test_unit=r_unit,
                    test_flag=r_flag,
                    instrument_id=self.instrument_id,
                )
                logging.info(
                    "Posting results done. sample_no:%s, test_code:%s, test_result:%s, test_unit:%s, test_flag:%s, instrument_id:%s",
                    o_sid,
                    r_testno,
                    res_num,
                    r_unit,
                    r_flag,
                    self.instrument_id,
                )
            else:
                logging.info("Unkown message.")

        return True

    def clean_msg(self, s):
        """Clean the message by removing ETB characters."""
        logging.info("clean...")
        t = ""
        a = 1
        while a > 0:
            try:
                a = s.find(ETB.decode(ENCODING))
                t = s[a : a + 6]
                s = str(s).replace(t, "")
            except ValueError as e:
                logging.error("ValueError occurred: %s", str(e))
            except IndexError as e:
                logging.error("IndexError occurred: %s", str(e))
                a = 0

        logging.info("result [%s]", str(s))

        return s

    def open(self):
        """Open the connection to the instrument."""
        if self.connection_type == "TCP":
            while 1:
                self.message = ""
                while 1:
                    data = self.conn.recv(BUFFER_SIZE)
                    if not data:
                        break
                    if isinstance(data, str):
                        data = data.encode(ENCODING)
                    logging.info("Data: [%s]", data)
                    # logging.info("data len [%s]", len(data))

                    if data != "":
                        self.send_ack()
                        self.message = self.message + data.decode(ENCODING)
                        # logging.info("message [%s]", str(self.message))
                        if (
                            (
                                str(self.message).startswith(STX.decode(ENCODING))
                                and str(self.message).endswith(EOT.decode(ENCODING))
                            )
                            or (
                                str(self.message).startswith(ENQ.decode(ENCODING))
                                and str(self.message).endswith(EOT.decode(ENCODING))
                            )
                            or str(data) == EOT.decode(ENCODING)
                        ):
                            if len(self.message) > 0:
                                logging.info(
                                    "start processing message [%s]", str(self.message)
                                )
                                msg = self.message
                                msg = str(msg).replace(ENQ.decode(ENCODING), "")
                                msg = str(msg).replace(ETX.decode(ENCODING), "")
                                msg = str(msg).replace(EOT.decode(ENCODING), "")
                                msg = str(msg).replace(STX.decode(ENCODING), "")
                                # clean ETB
                                # logging.info("clean ETB.")
                                msg = self.clean_msg(msg)
                                # logging.info("cleaned message ETB is [%s]" % str(msg))
                                msg = msg[1:-4]
                                # logging.info("cleaned message final is [%s]" % str(msg))
                                msg = self.decode(
                                    "1"
                                    + str(msg)
                                    + CR.decode(ENCODING)
                                    + ETX.decode(ENCODING)
                                )
                                logging.info("decoded to [%s]", str(msg))
                                self.handle_message(msg)
                                self.message = ""

        else:
            logging.error("astm only support connection type TCP")
