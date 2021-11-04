# Owned
__project__ = "shellyem"
__author__ = "Danilo Cilento"
__license__ = "MIT"
__version__ = "0.0.1"
__date__ = "28/06/2021"
__email__ = "<danilo.cilento@gmail.com>"

# Shelly EM API Rest
shelly_server = "192.168.1.11"
shelly_port = 80
shelly_emidx = 0        # first measuring channel with clamp by 120A

# InfluxDB Connection
influxdb_host = "localhost"
influxdb_port = 8086
influxdb_repo = "peimar"
influxdb_user = "peimar"
influxdb_pwd = "p31m4r"

# Log path
logdefaultpath = "/var/log/shellyem/default.log"
loginfopath = "/var/log/shellyem/info.log"
