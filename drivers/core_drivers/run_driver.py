###############################
# run_driver.py
#
# Desc: Running driver menggunakan format minimal tanpa threading
#
# Auth: Yose
# Date: 24 Mei 2018
#
# update:
#   20190904 - exception if instrument code not found.

from importlib import import_module
import os
import MySQLdb
import logging.config
import yaml
import configparser
import sys
# from importlib import import_module


VERSION = '0.0.3'

DRIVER_LIST = ('BC6800','BC5000','BS480','ASTM1394',
               'MINDRAYBS','MISSIONU500','READER40','DF50',
               'NOVAPHOX','BT3500','E411')


# default
from libs.analyzers.ASTM1394 import ASTM1394
# Mindray
from libs.analyzers.BC6800 import BC6800
from libs.analyzers.BC5000 import BC5000
from libs.analyzers.BS480 import BS480
from libs.analyzers.MINDRAYBS import MINDRAYBS
from libs.analyzers.MISSIONU500 import MISSIONU500
from libs.analyzers.READER40 import READER40
from libs.analyzers.DF50 import DF50
from libs.analyzers.BT3500 import BT3500
# Nova
from libs.analyzers.NOVAPHOX import NOVAPHOX
# Roche
from libs.analyzers.E411 import E411

SERVER = '127.0.0.1'
INSTRUMENT_CODE = '1'

config = configparser.ConfigParser()
config.read('run_driver.ini')
SERVER = config.get('General','server')
INSTRUMENT_CODE = config.get('General','instrument_code')
DB = config.get('General','db')


def main():
    logging.info('~~~~~#####  core_driver [%s] #####~~~~~' % VERSION)
    logging.info('DRIVER_LIST [%s]' % str(DRIVER_LIST))
    logging.info('SERVER IP Address:%s' % SERVER)
    logging.info('INSTRUMENT_CODE:%s' % INSTRUMENT_CODE)
    logging.debug('trying to get configuration...')

    b_run_class = False

    try:
        conn = MySQLdb.connect(host= SERVER,
                  user='corelab_comm',
                  passwd='corelab_comm',
                  db=DB)
        cursor = conn.cursor()
        SQL = """
SELECT name,connection_type,driver,serial_baud_rate,serial_data_bit,serial_port,serial_stop_bit,tcp_conn_type,tcp_host,tcp_port,id
FROM corelab_instruments 
WHERE code = '{code}'  
-- AND active = 1
"""
        SQL = SQL.format(code=INSTRUMENT_CODE)
        logging.info(SQL)
        cursor.execute(SQL)
        data = cursor.fetchall()
        if len(data)>0:
            logging.info('OK got instrument count [%s] - %s' % (str(len(data)),data[0]))
            try:
                name = str(data[0][0])
                connection_type = str(data[0][1])
                driver = str(data[0][2])
                serial_baud_rate = str(data[0][3])
                serial_data_bit = str(data[0][4])
                serial_port = str(data[0][5])
                serial_stop_bit = str(data[0][6])
                tcp_conn_type = str(data[0][7])
                tcp_host = str(data[0][8])
                tcp_port = 0
                if data[0][9]:
                    tcp_port = int(data[0][9])
                INSTRUMENT_ID = data[0][10]
            except Exception as e:
                logging.error('Error read data [%s]' % str(e))
                sys.exit(0)
            if driver in DRIVER_LIST:
                logging.info('driver available')
                b_run_class = True
               #try:
                cls = getattr(import_module("libs.analyzers."+driver),driver)
                con = cls(SERVER,DB,INSTRUMENT_ID,name,connection_type,driver,serial_baud_rate,serial_data_bit,serial_port,serial_stop_bit,tcp_conn_type,tcp_host,tcp_port)
                con.open()
                # except Exception as e:
                #    logging.error('RUNNING DRIVER [%s]:%s' % (driver,str(e)))
                #    sys.exit(1)
            else:
                logging.error('driver [%s] not found.' % driver)
        else:
            logging.error('Instrument code [%s] not found.' % INSTRUMENT_CODE)
            conn.close()
            sys.exit(1)
    except Exception as e:
        logging.error(e)
        sys.exit(1)
        # conn.close()

    if b_run_class:
        cls = getattr(import_module("libs.analyzers."+driver),driver)
        con = cls(SERVER,DB,INSTRUMENT_ID,name,connection_type,driver,serial_baud_rate,serial_data_bit,serial_port,serial_stop_bit,tcp_conn_type,tcp_host,tcp_port)
        con.open()
        
        
if __name__ == "__main__":
    with open('run_driver.yaml', 'rt') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    logging.info('starting core_drivers')
    main()
