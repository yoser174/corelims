###############################
# cobas6k driver
#
# auth: Yoserizal
# date: 29 Maret 2018
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


DRIVER_NAME = 'BT3500'
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

class BT3500(object):

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
        self.my_conn = my_db(self.server,MY_DB)
        self.astm = astm(self.connection_type,self.tcp_conn_type,self.tcp_host,self.tcp_port)

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
        message = b''.join([STX, msg, self.astm.make_checksum(msg), CR, LF])
        message = self.astm.decode(message)
        logging.info(message)
        order_id = 0
        sample_query = False
        
        for m in message:
            logging.info(m)
            if m[0] == 'H':
                sender = m[4]
            if m[0] == 'O':
                # sample_no = m[2][0]
                sample_no = m[3]
            if m[0] == 'R':
                tes_code =  m[2][0]
                tes_result =  m[3][0]
                tes_unit = m[4]
                tes_ref = ''
                tes_flag = ''
                self.my_conn.insert_result(sample_no,tes_code,tes_result,tes_ref,tes_unit,tes_flag,self.instrument_id)
            if m[0] == 'Q':
                q_sample_no = m[2][1]
                sample_query = True
                
        if sample_query:
            logging.info('Sample Query: [%s]' % q_sample_no)
            self.sample_query(q_sample_no,sender)
        return True

    def  make_checksum_bt(self,message):
        if not isinstance(message[0], int):
            message = map(ord, message)
        return str(int(hex(sum(message) & 0xFF)[2:].upper().zfill(2).encode(),16)).zfill(3)
                    
    def open(self):
        if self.connection_type == 'TCP':
            logging.info('connecting TCP server [%s:%s] ...' % (self.tcp_host,self.tcp_port))
            while 1:
                # get batch to sent to instrument
                logging.info('getting sample batch for instrument..')
                proces = False
                try:
                    samples = self.my_conn.get_sample_batch(self.instrument_id,0)
                    logging.info(samples[0])
                    logging.info(len(samples[0]))
                    samples = samples[0]
                    process = True
                except:
                    pass
                for sample in samples:
                    logging.info('processing [%s]' % str(sample))
                    sample_no = str(sample).ljust(15)+'TSN'
                    logging.info('sample_no [%s]' % sample_no)
                    logging.info('getting test array..')
                    tests = self.my_conn.get_test_array(sample,self.instrument_id)
                    test_count = 0
                    test_str = ''
                    for test in tests:
                        test_count += 1
                        test_str = test_str + test[0] + ' '
                    logging.info('got [%s] test' % test_count)
                    logging.info('test string [%s]' % test_str)
                    sample_no = sample_no + str(test_count).zfill(3)+test_str
                    sample_no = sample_no + self.make_checksum_bt(sample_no)
                    logging.info(sample_no)
                    logging.info('sendding to instrument data [%s]' % sample_no)
                    self.astm.send_stx()
                    data = self.astm.conn.recv(BUFFER_SIZE)
                    if data == ACK:
                        logging.info('<< ACK')
                        #self.astm.send(sample_no)
                        for s in sample_no:
                            self.astm.send(s)
                        self.astm.send_eot()
                        data = self.astm.conn.recv(BUFFER_SIZE)
                        logging.info('data [%s]' % str(data))
                        # update status to 1 (processed)
                        self.my_conn.set_status_batch(sample,'1')
                    else:
                        logging.error('data not expected [%s]' % str(data))


                # get batch waiting for result
                logging.info('getting pending result from instrument..')
                proces = False
                try:
                    samples = self.my_conn.get_sample_batch(self.instrument_id,1)
                    logging.info(samples[0])
                    logging.info(len(samples[0]))
                    samples = samples[0]
                    process = True
                except:
                    pass

                for sample in samples:
                    logging.info('try processing [%s]' % str(sample))
                    try:
                        self.astm.send('R')
                        data = self.astm.conn.recv(BUFFER_SIZE)
                        logging.info('<< %s' % data)
                    except Exception as e:
                        logging.warning('Failed [%s]' % str(e))
                        pass
                    
                    
                    
                        
                    
                logging.debug('sleep 5 secs..')


        else:
            logging.error('BS4800 only support connection type TCP')

        # close db connection
        self.my_conn.close()

        sys.exit(0)
