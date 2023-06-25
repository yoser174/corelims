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
# 2018-07-25 got barcode as Sampel ID data m[3] rather than sample id from instrument

import serial
import time
import logging
import MySQLdb
from datetime import datetime
import sys
from ..db.my_db import my_db

# reload(sys)  
# sys.setdefaultencoding('ISO-8859-1')


DRIVER_NAME = 'MISSIONU500'
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

class MISSIONU500(object):

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
        self.serial_port = serial_port
        self.serial_baud_rate = serial_baud_rate
        self.serial_data_bit = serial_data_bit
        self.serial_port = serial_port
        if serial_stop_bit == '2':
            self.serial_stop_bit = serial.STOPBITS_TWO
        else:
            self.serial_stop_bit = serial.STOPBITS_ONE
        MY_DB = db

        # mysql connection
        self.my_conn = my_db(self.server,MY_DB)
        self.serial = serial.Serial(port=self.serial_port,baudrate=self.serial_baud_rate,
                                    timeout=10, writeTimeout=10,stopbits=self.serial_stop_bit,
                                    bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE)

    def listen(self):
        logging.info('listening..')
        data = ''
        while data =='':
            while self.serial.inWaiting() > 0:
                    data += self.serial.read(1)
        return data
        
    def handlemsg(self,msg):
        flag_qc = None
        flag = []
        data_msg = str(msg).split(CRLF)
        logging.info('data_msg [%s]' % str(data_msg))
        logging.info('getting sample_id...')
        sample_id = str(str(data_msg[1]).split(':')[1]).strip()
        logging.info('Sample ID : [%s]' % str(sample_id))
        num_id = str(data_msg[2][5:15]).strip()
        s_count = str(str(data_msg[2][16:]).strip())[1:-1]
        logging.info('No. [%s]' % str(num_id))
        logging.info('Sample count [%s]' % s_count)
        if num_id.endswith('E'):
            flag_qc = 'E'
            logging.info('QC flag [E]')
        
        for data in data_msg[3:-1]:
            logging.info(data)
            test_code = str(data[0:7]).strip()
            if test_code.startswith('*'):
                test_code = test_code[1:]
                flag.append('*')
            logging.info('test_code [%s]' % str(test_code))
            result_1 = str(data[7:17]).strip()
            logging.info('result_1 [%s]' % str(result_1))
            result_2 = str(data[17:]).strip()
            logging.info('result_2 [%s]' % str(result_2))
            logging.info('flag [%s]' % str(flag))
            # cek to db
            logging.info('checking if test_code exists')
            test_attr = self.my_conn.get_mapping_code_attribut(self.instrument_id,test_code)
            if test_attr > 0 :
                logging.info('found attribut test [%s]' % str(test_attr))
                result_selection = str(test_attr[2]).strip()
                logging.info('selecting result number [%s]' % result_selection)
                result_ori = result_1
                if result_selection == '2':
                    result_ori = result_2     
                logging.info('selected result value [%s]' % str(result_ori))
                result_final = result_ori
 
                # insert result
                logging.info('inserting result to database..')
                last_insert_id = self.my_conn.insert_result(sample_id,test_code,result_final,'','','',self.instrument_id)
                if flag_qc == 'E':
                    logging.info('insert flag "E"')
                    # get flag mapping
                    flag_id = self.my_conn.my_select(" SELECT ID FROM bbconnlab_instrumentflags  WHERE instrument_id = %s AND flag_code = 'E' " % str(self.instrument_id))
                    if len(flag_id)>0:                   
                        self.my_conn.my_insert(' INSERT INTO bbconnlab_resultflags (instrument_flag_id,result_id,lastmodification) VALUE (%s,%s,NOW()) ' % (str(flag_id[0][0]),last_insert_id))
                # flag result
                for fl in flag:
                    logging.info('insert flag [%s]' % str(fl))
                    # get flag mapping
                    flag_id = self.my_conn.my_select(" SELECT ID FROM bbconnlab_instrumentflags  WHERE instrument_id = %s AND flag_code = '%s' " % (str(self.instrument_id),str(fl)))
                    if len(flag_id)>0:
                        self.my_conn.my_insert(' INSERT INTO bbconnlab_resultflags (instrument_flag_id,result_id,lastmodification) VALUE (%s,%s,NOW()) ' % (str(flag_id[0][0]),last_insert_id))
                    
                    
                    
                
                    
                    
                    
                    
            else:
                logging.info('test code [%s] not found !' % test_code)
        
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
                    self.message = self.message + data
                    if (self.message.startswith(STX) and self.message.endswith(ETX)):
                        logging.info('start processing data [%s]' % str(self.message))
                        try:
                            self.handlemsg(self.message)
                            self.message = ''
                        except Exception as e:
                            logging.info('Failed processing message [%s]' % str(e))

        else:
            logging.error('this driver only support connection type SERIAL')

        # close db connection
        self.my_conn.close()

        sys.exit(0)
