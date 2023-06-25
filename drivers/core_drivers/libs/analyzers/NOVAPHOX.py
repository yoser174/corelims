###############################
# cobas6k driver
#
# auth: Yoserizal
# date: 23 August 2019
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

import serial
import time
import logging
import sqlite3
import MySQLdb
from datetime import datetime
import socket
import sys
from ..db.my_db import my_db
from . import astm

# reload(sys)  
# sys.setdefaultencoding('ISO-8859-1')


DRIVER_NAME = 'NOVAPHOX'
DRIVER_VERSION = '0.0.0.1'

ENCODING = 'latin-1'
NULL = b'\x00'
STX = b'\x02'
ETX = b'\x03'
EOT = b'\x04'
ENQ = b'\x05'
ACK = b'\x06'
NAK = b'\x15'
ETB = b'\x17'
LF  = b'\x0A'
CR  = b'\x0D'
CRLF = CR + LF
VT = b'\x0B'
FS = b'\x1C'
RECORD_SEP    = b'\x0D' # \r #
FIELD_SEP     = b'\x7C' # |  #
REPEAT_SEP    = b'\x5C' # \  #
COMPONENT_SEP = b'\x5E' # ^  #
ESCAPE_SEP    = b'\x26' # &  #


TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024

MY_USER = 'mwconn'
MY_PASS = 'connmw'

class NOVAPHOX(object):

    def __init__(self,server,db,instrument_id,name,
                 connection_type,
                 driver,serial_baud_rate,serial_data_bit,serial_port,serial_stop_bit,
                 tcp_conn_type,tcp_host,tcp_port):
        self.message=''
        logging.info( DRIVER_NAME+' - '+DRIVER_VERSION+' loaded.')
        self.server = server
        self.instrument_id = instrument_id
        self.connection_type = connection_type
        logging.info('connection type: [%s]' % connection_type)
        if not connection_type == 'SER':
            logging.error('Connection ONLY support for SERIAL connection.!')
            sys.exit(0)
        self.tcp_conn_type = tcp_conn_type
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.serial_port = serial_port
        self.serial_baud_rate = serial_baud_rate
        self.serial_data_bit = serial_data_bit
        self.serial_port = serial_port
        if serial_stop_bit == '2':
            self.serial_stop_bit = serial.STOPBITS_TWO
        else:
            self.serial_stop_bit = serial.STOPBITS_ONE
        MY_DB = db
        self.db = db

        # mysql connection
        self.my_conn = my_db(self.server,self.db)
        self.serial = serial.Serial(port=self.serial_port,baudrate=self.serial_baud_rate,
                                    timeout=10, writeTimeout=10,stopbits=self.serial_stop_bit,
                                    bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE)

    ### ASTM FUNCTION ####
    def  make_checksum(self,message):
        if not isinstance(message[0], int):
            message = map(ord, message)
        return hex(sum(message) & 0xFF)[2:].upper().zfill(2).encode()

    def checksum_verify(self,message):
        if not (message.startswith(STX) and message.endswith(CRLF)):
            logging.error('Malformed ASTM message. Expected that it will started'
                         ' with %x and followed by %x%x characters. Got: %r'
                         ' ' % (ord(STX), ord(CR), ord(LF), message))
            return False
        stx, frame_cs = message[0], message[1:-2]
        frame, cs = frame_cs[:-2], frame_cs[-2:]
        ccs = self.make_checksum(frame)
        if cs == ccs:
            logging.info( 'Checksum is OK')
            return True
        else:
            logging.warning('Checksum failure: expected %r, calculated %r' % (cs, ccs))
            return False

    def decode(self,data):
        if not isinstance(data, bytes):
            logging.error ('bytes expected, got %r' % data)
        if data.startswith(STX):  # may be decode message \x02...\x03CS\r\n
            records = self.decode_message(data)
            return records
        byte = data[:1].decode()
        if  byte.isdigit():
            records = self.decode_frame(data)
            return records
        return [self.decode_record(data)]

    def decode_message(self,message):
        if not isinstance(message, bytes):
            logging.error('bytes expected, got %r' % message)
        if not (message.startswith(STX) and message.endswith(CRLF)):
            logging.error('ERROR Malformed ASTM message. Expected that it will started with %x and followed by %x%x characters. Got: %r' % (ord(STX), ord(CR), ord(LF), message))
        stx, frame_cs = message[0], message[1:-2]
        frame, cs = frame_cs[:-2], frame_cs[-2:]
        ccs = self.make_checksum(frame)
        assert cs == ccs, 'Checksum failure: expected %r, calculated %r' % (cs, ccs)
        records = self.decode_frame(frame)
        return records

    def decode_frame(self,frame):
        if not isinstance(frame,bytes):
            logging.error('bytes expected, got %r' % frame)
        if frame.endswith(CR + ETX):
            frame = frame[:-2]
        elif frame.endswith(ETB):
            frame = frame[:-1]
        #else:
        #    logging.warning('Incomplete frame data %r. Expected trailing <CR><ETX> or <ETB> chars' % frame)
        seq = frame[:1].decode()
        if not seq.isdigit():
            logging.warning('Malformed ASTM frame. Expected leading seq number %r' % frame)
        seq, records = int(seq), frame[1:]
        return  [self.decode_record(record)
                 for record in records.split(RECORD_SEP)]

    def decode_record(self,record):
        fields = []
        for item in record.split(FIELD_SEP):
            if REPEAT_SEP in item:
                item = self.decode_repeated_component(item)
            elif COMPONENT_SEP in item:
                item = self.decode_component(item)
            else:
                item = item
            fields.append([None, item][bool(item)])
        return fields

    def decode_component(self,field):
        return [[None, item][bool(item)]
                for item in field.split(COMPONENT_SEP)]
    
    def decode_repeated_component(self,component):
        return [self.decode_component(item)
            for item in component.split(REPEAT_SEP)]


    def encode_message(self,seq,records):
        data = RECORD_SEP.join(self.encode_record(record)
                               for record in records)
        data = b''.join((str(seq % 8).encode(), data, CR, ETX))
        return b''.join([STX, data, self.make_checksum(data), CR, LF])

    def encode_record(self,record):
        fields = []
        _append = fields.append
        for field in record:
            if isinstance(field, bytes):
                _append(field)
            elif isinstance(field, unicode):
                _append(field.encode(encoding))
            elif isinstance(field, Iterable):
                _append(encode_component(field, encoding))
            elif field is None:
                _append(b'')
            else:
                _append(unicode(field).encode(encoding))
        return FIELD_SEP.join(fields)

    def make_chunks(self,s, n):
        iter_bytes = (s[i:i + 1] for i in range(len(s)))
        return [b''.join(item)
                for item in izip_longest(*[iter_bytes] * n, fillvalue=b'')]

    def split(self,msg, size):
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
            item = b''.join([str((idx + frame) % 8).encode(), chunk, ETB])
            yield b''.join([STX, item, make_checksum(item), CRLF])
        item = b''.join([str((idx + frame + 1) % 8).encode(), last, CR, ETX])
        yield b''.join([STX, item, make_checksum(item), CRLF])


    def listen(self):
        logging.info('listening..')
        data = ''
        while data =='':
            while self.serial.inWaiting() > 0:
                    data += self.serial.read(1)
        return data
    
    def send_ack(self):
        logging.info('>>ACK')
        self.serial.write(ACK)

    def sample_query(self,sample_no,sender):
        ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        logging.info(sender)
        h = 'H|\^&|||'+'^'.join(map(str, sender))+'|||||||SA|1394-97|'+ts+'\r'
        logging.info(h)
        # generate PID
        pat_id,name,dob,sex,doctor,diagnosis,origin = self.my_conn.get_patient_id(sample_no)
        p = 'P|1||'+pat_id+'||'+name+'^'+name+'^'+name+'||'+dob+'|'+sex+'|||||'+doctor+'|||||'+diagnosis+'||0001|||||A1|002||||||||\r'
        logging.info(p)
        tes_arr = self.my_conn.get_test_array(sample_no,self.instrument_id)
        tes_dump = ''
        if tes_arr:
            rec = 0
            for tes in tes_arr:
                if rec==0:
                    tes_dump +=str(rec+1)+'^'+str(tes[0])+'^1^1'
                else:
                    tes_dump +='\\'+str(rec+1)+'^'+str(tes[0])+'^1^1'
                rec += 1
        o = 'O|1|1^1^1|'+sample_no+'|'+tes_dump+'|R|'+ts+'|'+ts+'||||||||serum|'+str(doctor)+'|'+str(origin)+'|1|||||||Q|||||\r'
        l = 'L|1|N\r'
        logging.info(o)
        astm_msg = h+p+o+l
        logging.info(astm_msg)
        self.astm.send_enq()
        data = self.astm.listen()
        if data==ACK:
            self.astm.send_msg(astm_msg)
            data = self.astm.listen()
            if data == ACK:
                self.astm.send_eot()
        
    def handlemsg(self,msg):
        msg = '1'+msg
        message = b''.join([STX, msg, self.make_checksum(msg), CR, LF])
        message = self.decode(message)
        logging.info(message)
        order_id = 0
        sample_query = False
        
        for m in message:
            logging.info(m)
            if m[0] == 'H':
                sender = m[4]
            if m[0] == 'P':
                sample_no = m[3]
            if m[0] == 'R':
                tes_code =  m[2][3]
                tes_result =  m[3]
                tes_unit = m[4]
                tes_ref = ''
                tes_flag = ''
                self.my_conn.insert_result(sample_no,tes_code,tes_result,tes_ref,tes_unit,tes_flag,self.instrument_id)
            if m[0] == 'Q':
                q_sample_no = m[2][1]
                sample_query = True
                
        #if sample_query:
        #    logging.info('Sample Query: [%s]' % q_sample_no)
        #    self.sample_query(q_sample_no,sender)
            
        return True



    def open(self):
        if self.connection_type == 'SER':
            logging.info('Connection type is SERIAL')
            logging.info(' serial_port [%s]' % self.serial_port)
            logging.info(' serial_baud_rate [%s]' % self.serial_baud_rate)
            logging.info(' serial_stop_bit [%s]' % self.serial_stop_bit)

            self.message = ''
            
            while 1:
                data = self.listen()
                if data!='':
                    logging.info('<< [%s]' % str(data))
                    if not data: break
                    if isinstance(data, unicode):
                        data = data.encode('utf-8')
                    logging.info("Data: [{}]".format(data))
                    logging.info("data len [%s]" % str(len(data)))

                    if data == ENQ:
                        logging.info('<< ENQ')
                        self.send_ack()

                    elif (data.startswith(STX) and data.endswith(CRLF)):
                        logging.info('got data')
                        self.send_ack()
                        logging.info(data)
                        self.message += str(data[2:-5]).replace(ETB,'')
                        logging.info(str(data[2:-5]).replace(ETB,''))

                    elif (data==EOT) or (data==EOT+ENQ):
                        if self.message  != '':
                            logging.info('Proses message:')
                            logging.info(str(self.message))
                            self.handlemsg(self.message)
                            self.message = ''
                            self.send_ack()
                    else:
                        self.send_ack()
                        

        else:
            logging.error('this driver only support connection type SERIAL')

