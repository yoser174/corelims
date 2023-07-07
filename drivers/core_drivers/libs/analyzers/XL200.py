###############################
# cobas6k driver
#
# auth: Yoserizal
# date: 7 July 2023
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

import serial
import time
import logging
import sqlite3
import MySQLdb
from datetime import datetime
import socket
import sys

from libs.corelab_astm.codec import decode, make_checksum
from ..db.my_db import my_db
from .astm import astm

# reload(sys)  
# sys.setdefaultencoding('ISO-8859-1')


DRIVER_NAME = 'XL200'
DRIVER_VERSION = '0.0.2'

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

MY_USER = 'corelims'
MY_PASS = 'corelims'

class XL200(object):
    def __init__(self,server,db,instrument_id,name,
                 connection_type,
                 driver,serial_baud_rate,serial_data_bit,serial_port,serial_stop_bit,
                 tcp_conn_type,tcp_host,tcp_port):
        self.message=''
        logging.info( DRIVER_NAME+' - '+DRIVER_VERSION+' loaded.')
        logging.info('connection type: [%s]' % connection_type)
        self.server = server
        self.instrument_id = instrument_id
        self.connection_type = connection_type
        self.tcp_conn_type = tcp_conn_type
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        MY_DB = db

        # mysql connection
        try:
            self.my_conn = my_db(self.server,MY_DB)
            self.astm = astm(self.connection_type,self.tcp_conn_type,self.tcp_host,self.tcp_port)
        except Exception as e:
            logging.error(str(e))

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
        o = ''
        if tes_arr:
            rec = 0
            for tes in tes_arr:
                if rec==0:
                    tes_dump +=str(rec+1)+'^'+str(tes[0])+'^1^1'
                else:
                    tes_dump +='\\'+str(rec+1)+'^'+str(tes[0])+'^1^1'
                rec += 1
        o = 'O|1|'+sample_no+'^1^1|'+sample_no+'|'+tes_dump+'|R|'+ts+'|'+ts+'||||||||serum|'+str(doctor)+'|'+str(origin)+'|1|||||||Q|||||\r'  
        l = 'L|1|N'
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
        logging.debug('handlemsg()')
        msg = msg.replace("b'",'')
        msg = msg.replace("'",'')
        # msg = msg.replace("\\",'\')
        msg = msg.replace("\r",CR.decode(ENCODING))
        logging.debug(msg)
        logging.debug(type(msg))
        msg = '1'+msg
        msg = msg.encode(ENCODING)
        logging.debug(msg)
        msg = STX+ msg+CR+ETX+ make_checksum(msg+CR+ETX)+ CR+ LF
        codec_msg = decode(msg,encoding=ENCODING)
        logging.info(codec_msg)

        order_id = 0
        message_type = ''
        sender = ''
        sample_id = ''
        seq = ''
        rack = ''
        pos = ''
        rack_type = ''
        container_type = ''
        TSREQ_REAL = False
        order_id = 0
        q_o = ''
        perv_rec = ''
        sample_query = False
        
        for m in codec_msg:
            logging.info(m)
            if m[0] == 'H':
                sender = m[4]
            if m[0] == 'O':
                q_o = m
                # sample_no = m[2][0]
                sample_no = m[3] or m[2][0]
            if m[0] == 'R':
                tes_code =  m[2][3]
                tes_result =  m[3]
                tes_unit = m[4]
                tes_ref = ''
                tes_flag = m[6]
                self.my_conn.insert_result(sample_no,tes_code,tes_result,tes_ref,tes_unit,tes_flag,self.instrument_id)
            if m[0] == 'Q':
                q_sample_no = m[2][1]
                sample_query = True
            if m[0] == 'C':
                logging.info('comment [%s]' % perv_rec)
            
            perv_rec =  m[0]
                
        if sample_query:
            logging.info('Sample Query: [%s]' % q_sample_no)
            self.sample_query(q_sample_no,sender)
        return True
                    
    def open(self):
        if self.connection_type == 'TCP':
            logging.info('Client connected.')
            while 1:
                while 1:
                    data = self.astm.conn.recv(BUFFER_SIZE)
                    if not data: break
                    if isinstance(data, str):
                        data = data.encode(ENCODING)
                    logging.info("Data: [{}]".format(data))
                    logging.info("data len [%s]" % str(len(data)))

                    if data == ENQ:
                        logging.info('<< ENQ')
                        self.astm.send_ack()

                    elif (data.startswith(STX) and data.endswith(CRLF)):
                        logging.info('got data')
                        self.astm.send_ack()
                        logging.info(data)
                        # self.message += str(data[2:-5]).replace(ETB.decode(ENCODING),'')
                        self.message += data[2:-5].decode(ENCODING)
                        logging.debug('message [%s]' % self.message)

                    elif (data==EOT) or (data==EOT+ENQ):
                        logging.info('Proses message:')
                        logging.info(str(self.message))
                        self.handlemsg(self.message)
                        self.message = ''

                    elif data.endswith(EOT):
                        logging.info('data ends with EOT')
                        self.astm.send_ack()
                        logging.info(data)
                        self.message += str(data).replace(EOT,'')
                        logging.info(str(self.message))
                        try:
                            logging.info('try to processing message')
                            self.handlemsg(self.message)
                        except Exception as e:
                            logging.error('Failed when processing message [%s] with error [%s]' % (str(self.message),str(e)))
                        self.message = ''                       
                    else:
                        if data:
                            self.message += data
                        self.astm.send_ack()           
                self.astm.conn.close()
                logging.info('Socked closed. sleep 1s then restart listenning.')
                time.sleep(1)
        else:
            logging.error('[%s] only support connection type TCP' % DRIVER_NAME)

        # close db connection
        self.my_conn.close()

        sys.exit(0)
