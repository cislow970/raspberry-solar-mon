import sys
import logging
import datetime
import requests
import urllib3
import json
from shelly.emeter import config
from logging.handlers import RotatingFileHandler
from argparse import ArgumentParser
from influxdb import InfluxDBClient


# InsecureRequestWarning suppress (HTTPS)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def create_rotating_log(name, path):
    """
    Creates a rotating log

    :param name: log label
    :type name: str
    :param path: log file path
    :type path: str
    :returns: logger object
    :rtype: logging
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create file handler which logs even debug messages
    fh = logging.handlers.RotatingFileHandler(path, mode='a',  maxBytes=2 * 1024 * 1024, backupCount=2)
    fh.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s\t%(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    fh.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)

    return logger


def options():
    """
    Define command line arguments and help

    :returns: arguments list
    :rtype: bool, str
    """
    parser = ArgumentParser()

    # Command line options
    parser.add_argument("-d",
                        "--daemon",
                        action="store_true",
                        dest="daemon",
                        help="enable multi-thread version running as daemon"
                        )
    parser.add_argument("-m",
                        "--method",
                        dest="method",
                        choices=['check-alive',
                                 'get-emeter'],
                        help="call a specific method",
                        )
    parser.add_argument("-r",
                        "--release",
                        action="store_true",
                        dest="release",
                        help="show robot release and exit"
                        )

    args = parser.parse_args()

    daemon = args.daemon
    method = args.method
    release = args.release

    if release:
        print("$Id: %s v%s %s (%s %s) $" % (config.__project__, config.__version__, config.__date__, config.__author__, config.__email__))
        print("This robot use http protocol to get info from Shelly Energy Meter REST API.")
        sys.exit()

    if daemon and method:
        print("Cannot you use option \"method\" with option \"daemon\". Option \"method\" is for running robot in stand-alone mode. You can use only option \"daemon\" or \"method\".")
        sys.exit(1)

    if not daemon:
        print("[DEBUG] Option -d|--daemon: %s" % str(daemon))
        print("[DEBUG] Option -m|--method: %s" % str(method))
        print("[DEBUG] Option -r|--release: %s" % str(release))

        if not method:
            print("You must specify the option -m")
            sys.exit(1)

    return daemon, method


def check_alive(emsrv, emport, log):
    """
    Check status of the Shelly EM

    :param emsrv: ip address of a specific Shelly EM Server
    :type emsrv: str
    :param emport: TCP port of Shelly EM Server
    :type emport: int
    :param log: enable logging
    :type log: logger object
    :returns: HTTP response code, response body and current timestamp
    :rtype: int, string, datetime
    """
    now = datetime.datetime.utcnow()
    response = None

    log.info("*** Check status of Shelly EM ***")

    url = 'http://' + emsrv + ':' + str(emport) + '/status'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    log.debug("URI: %s [HTTP GET]" % url)

    try:
        response = requests.get(url, verify=False, headers=headers, timeout=urllib3.Timeout(connect=1.0, read=1.0))
        response.raise_for_status()
    except requests.exceptions.ConnectionError as errc:
        log.error("Error connecting: %s" % errc)
    except requests.exceptions.Timeout as errt:
        log.error("Timeout error: %s" % errt)
    except requests.exceptions.HTTPError as errh:
        log.error("HTTP error: %s" % errh)

    # For successful call, response code will be 200 (OK)
    if response:
        if response.ok:
            body_resp = json.loads(response.content)
            log.debug("The response contains {0} properties".format(len(body_resp)))
            log.debug("Body response: JSON %s" % json.dumps(body_resp))

            return response.status_code, response.content, now
    else:
        # Generic error calling web server
        return 500, "", now


def get_emeter(emsrv, emport, emidx, log):
    """
    Get Shelly Energy Meter data

    :param emsrv: ip address of a specific Shelly EM Server
    :type emsrv: str
    :param emport: TCP port of Shelly EM Server
    :type emport: int
    :param emidx: measurement channel used by Shelly EM
    :type emidx: int
    :param log: enable logging
    :type log: logger object
    :returns: HTTP response code, response body and current timestamp
    :rtype: int, string, datetime
    """
    now = datetime.datetime.utcnow()
    response = None

    log.info("*** Get Shelly Energy Meter data ***")

    url = 'http://' + emsrv + ':' + str(emport) + '/emeter/' + str(emidx)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    log.debug("URI: %s [HTTP GET]" % url)

    try:
        response = requests.get(url, verify=False, headers=headers, timeout=urllib3.Timeout(connect=1.0, read=1.0))
        response.raise_for_status()
    except requests.exceptions.ConnectionError as errc:
        log.error("Error connecting: %s" % errc)
    except requests.exceptions.Timeout as errt:
        log.error("Timeout error: %s" % errt)
    except requests.exceptions.HTTPError as errh:
        log.error("HTTP error: %s" % errh)

    # For successful call, response code will be 200 (OK)
    if response:
        if response.ok:
            body_resp = json.loads(response.content)
            log.debug("The response contains {0} properties".format(len(body_resp)))
            log.debug("Body response: JSON %s" % json.dumps(body_resp))

            return response.status_code, response.content, now
    else:
        # Generic error calling web server
        return 500, "", now


def store2influx(measurement, timestamp, fields, log):
    """
    Store data into time series database

    :param measurement: type of metric
    :type measurement: str
    :param timestamp: UTC time
    :type timestamp: datetime
    :param fields: value of metric
    :type fields: dict
    :param log: enable logging
    :type log: logger object
    """
    # Connection to the InfluxDB instance
    host = config.influxdb_host
    port = config.influxdb_port
    user = config.influxdb_user
    password = config.influxdb_pwd
    dbname = config.influxdb_repo
    json_body = [
        {
            "measurement": measurement,
            "tags": {
                "hostname": "shellyem",
                "poller": "pyshelly"
            },
            "time": timestamp,
            "fields": fields
        }
    ]

    log.info("Store data into database")

    client = InfluxDBClient(host, port, user, password, dbname)
    json_dump = json.dumps(json_body)

    log.debug("Write points: {0}".format(json_dump))

    try:
        result = client.write_points(json_body)
        if result:
            log.info("Writing data to InfluxDB is successfully")
    except:
        log.error("Cannot write data to InfluxDB!")
