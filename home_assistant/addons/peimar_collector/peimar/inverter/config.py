import array as arr
import pytz


# Owned
__project__ = "peimar"
__author__ = "Danilo Cilento"
__license__ = "MIT"
__version__ = "0.0.4"
__date__ = "02/11/2021"
__email__ = "<danilo.cilento@gmail.com>"

# Inverter Web Server
inverter_server = "192.168.1.8"
inverter_port = 80

# Inverter metric decimals
cf = arr.array('I', [0, 2, 1, 2, 1, 1, 2, 1, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 1, 2, 1, 2, 1, 2, 1, 1, 1])

# Inverter timezone
timezone = pytz.timezone("Europe/Rome")

# Production time slot
start_hour = '07'
start_minute = '30'
end_hour = '19'
end_minute = '00'
dst_start_hour = '06'
dst_start_minute = '00'
dst_end_hour = '21'
dst_end_minute = '30'

# InfluxDB Connection
influxdb_host = "192.168.1.54"
influxdb_port = 8086
influxdb_repo = "peimar"
influxdb_user = "peimar"
influxdb_pwd = "p31m4r"

# Log path
logdefaultpath = "/var/log/peimar/default.log"
loginfopath = "/var/log/peimar/info.log"
