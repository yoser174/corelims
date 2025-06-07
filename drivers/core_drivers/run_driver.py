"""run_driver.py main driver app"""

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
import sys
import logging.config
import configparser
import yaml
import argparse

# import MySQLdb
from libs.api.bearer_api_client import BearerApiClient


# default
# from libs.analyzers.ASTM1394 import ASTM1394

# Mindray
# from libs.analyzers.BC6800 import BC6800  # noqa: F401
# from libs.analyzers.BC5000 import BC5000
# from libs.analyzers.BS480 import BS480
# from libs.analyzers.MINDRAYBS import MINDRAYBS
# from libs.analyzers.MISSIONU500 import MISSIONU500
# from libs.analyzers.READER40 import READER40
# from libs.analyzers.DF50 import DF50
# from libs.analyzers.BT3500 import BT3500


# Nova
# from libs.analyzers.NOVAPHOX import NOVAPHOX

# Roche
# from libs.analyzers.E411 import E411

# Erba
# from libs.analyzers.XL200 import XL200

# Unknown
# from libs.analyzers.BW300 import BW300
# from libs.analyzers.ZYBIO import ZYBIO
# from libs.analyzers.ES20 import ES20
# from libs.analyzers.AERC3 import AERC3
# from libs.analyzers.CTKRAFIA import CTKRAFIA

# from importlib import import_module


VERSION = "0.0.4"

DRIVER_LIST = (
    "astm",
    "BC6800",
    "BC5000",
    "BS480",
    "astm1394",
    "MINDRAYBS",
    "MISSIONU500",
    "READER40",
    "DF50",
    "NOVAPHOX",
    "BT3500",
    "E411",
    "XL200",
    "BW300",
    "ZYBIO",
    "ES20",
    "AERC3",
    "CTKRAFIA",
)


SERVER = "127.0.0.1"
INSTRUMENT_CODE = "1"

parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("-i", "--ini_file", help="config INI file", required=True)
parser.add_argument("-l", "--yaml_file", help="config YAML file", required=True)

# Read arguments from command line
args = parser.parse_args()


ini_file = "run_driver.ini"
yaml_file = "run_driver.yaml"

if args.ini_file:
    ini_file = args.ini_file
if args.yaml_file:
    yaml_file = args.yaml_file


config = configparser.ConfigParser()
config.read(ini_file)
API_URL = config.get("General", "api_url", fallback="http://localhost:8000/api/")
TOKEN = config.get("General", "token")
SERVER = config.get("General", "server")
INSTRUMENT_CODE = config.get("General", "instrument_code")
DB = config.get("General", "db")


def main():
    """Function main"""
    logging.info(f"~~~~~#####  core_driver [{VERSION}] #####~~~~~")
    logging.info(f"DRIVER_LIST [{DRIVER_LIST}]")
    logging.info(f"SERVER IP Address:{SERVER}")
    logging.info(f"INSTRUMENT_CODE:{INSTRUMENT_CODE}")
    logging.debug("trying to get configuration...")

    b_run_class = False

    try:
        #         conn = MySQLdb.connect(
        #             host=SERVER, user="corelab_comm", passwd="corelab_comm", db=DB
        #         )
        #         cursor = conn.cursor()
        #         sql_str = """
        # SELECT name,connection_type,driver,serial_baud_rate,serial_data_bit,serial_port,serial_stop_bit,tcp_conn_type,tcp_host,tcp_port,id
        # FROM corelab_instruments
        # WHERE code = '{code}'
        # -- AND active = 1
        # """
        client = BearerApiClient(token=TOKEN, api_url=API_URL)
        instruments = client.get_all_instruments()
        for instrument in instruments:
            if instrument["code"] == INSTRUMENT_CODE:
                logging.info(f"Found instrument: {instrument}")
                name = instrument["name"]
                connection_type = instrument["connection_type"]
                driver = instrument["driver"]
                serial_baud_rate = instrument["serial_baud_rate"]
                serial_data_bit = instrument["serial_data_bit"]
                serial_port = instrument["serial_port"]
                serial_stop_bit = instrument["serial_stop_bit"]
                tcp_conn_type = instrument["tcp_conn_type"]
                tcp_host = instrument["tcp_host"]
                tcp_port = instrument.get("tcp_port", 0)
                INSTRUMENT_ID = instrument["id"]
                break
        else:
            logging.error(f"Instrument code [{INSTRUMENT_CODE}] not found in API.")
            sys.exit(1)

        if driver in DRIVER_LIST:
            logging.info(f"Running driver: {driver}")
            # Check if the driver module exists
            if not os.path.exists(f"libs/analyzers/{driver}.py"):
                logging.error(f"Driver module {driver} does not exist.")
                sys.exit(1)
            # Import the driver class dynamically
            logging.info(f"Driver [{driver}] found, proceeding to run.")

            b_run_class = True
            # try:
            cls = getattr(import_module("libs.analyzers." + driver), driver)
            con = cls(
                API_URL,
                TOKEN,
                INSTRUMENT_ID,
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
            )
            con.open()
            # except Exception as e:
            #    logging.error('RUNNING DRIVER [%s]:%s' % (driver,str(e)))
            #    sys.exit(1)
        else:
            logging.error(f"driver [{driver}] not found.")
    except (KeyError, AttributeError, ImportError, SystemExit) as e:
        logging.error(e)
        sys.exit(1)
        # conn.close()

    if b_run_class:
        cls = getattr(import_module("libs.analyzers." + driver), driver)
        con = cls(
            SERVER,
            DB,
            INSTRUMENT_ID,
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
        )
        con.open()


if __name__ == "__main__":
    with open(file=yaml_file, encoding="utf-8", mode="rt") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    logging.info("starting core_drivers")
    main()
