import time
import signal
import threading
import json
from threading import Thread
from shelly.emeter import config
from shelly.emeter import core


threadlock = threading.Lock()


class Alive(Thread):
    def __init__(self, name, freeze):
        Thread.__init__(self)

        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()

        self.name = name
        self.freeze = freeze

    def run(self):
        loggerbase = core.create_rotating_log('default', config.logdefaultpath)
        loggerbase.debug("Thread #" + str(self.ident) + " '" + self.name + "': started")
        # print("\nThread #" + str(self.ident) + " '" + self.name + "': started\n")

        while not self.shutdown_flag.is_set():
            # Freeze time
            time.sleep(self.freeze)

            # Acquire lock
            threadlock.acquire()
            loggerbase.debug("Thread #" + str(self.ident) + " '" + self.name + "': acquire lock")

            # Core operations
            while True:
                result = core.check_alive(config.shelly_server, config.shelly_port, loggerbase)
                if result[0] != 200:
                    loggerbase.error("Shelly EM is offline or unreachable")

                    # Store data to database
                    utctime = result[2].strftime("%Y-%m-%dT%H:%M:%S.000Z")

                    data = {
                        "reachable": 0
                    }
                    core.store2influx("status", utctime, data, loggerbase)

                    time.sleep(20)      # delay before retry check status
                else:
                    loggerbase.info("Shelly EM is online!")

                    # Store data into database
                    utctime = result[2].strftime("%Y-%m-%dT%H:%M:%S.000Z")

                    # Loading the response data into a dict variable
                    http_resp = json.loads(result[1])

                    uptime = round((http_resp["uptime"] / (3600 * 24)), 2)
                    wifi_conn = http_resp["wifi_sta"]["connected"]
                    cloud_conn = http_resp["cloud"]["connected"]
                    ram_total = http_resp["ram_total"]
                    ram_free = http_resp["ram_free"]
                    fs_size = http_resp["fs_size"]
                    fs_free = http_resp["fs_free"]
                    update = http_resp["update"]["has_update"]

                    loggerbase.debug("Uptime (days): %s" % uptime)
                    loggerbase.debug("Wifi Connected: %s" % wifi_conn)
                    loggerbase.debug("Cloud Connected: %s" % cloud_conn)
                    loggerbase.debug("RAM Total (bytes): %s" % ram_total)
                    loggerbase.debug("RAM Free (bytes): %s" % ram_free)
                    loggerbase.debug("FS Size (bytes): %s" % fs_size)
                    loggerbase.debug("FS Free (bytes): %s" % fs_free)
                    loggerbase.debug("Update Available: %s" % update)

                    data = {
                        "reachable": 1,
                        "uptime": uptime,
                        "wifi_conn": int(wifi_conn),
                        "cloud_conn": int(cloud_conn),
                        "ram_total": ram_total,
                        "ram_free": ram_free,
                        "fs_size": fs_size,
                        "fs_free": fs_free,
                        "update": int(update)
                    }
                    core.store2influx("status", utctime, data, loggerbase)
                    break

            # Release lock
            threadlock.release()
            loggerbase.debug("Thread #" + str(self.ident) + " '" + self.name + "': release lock")

        loggerbase.debug("Thread #" + str(self.ident) + " '" + self.name + "': stopped")
        # print("\nThread #" + str(self.ident) + " '" + self.name + "': stopped\n")


class Collector(Thread):
    def __init__(self, name, freeze):
        Thread.__init__(self)

        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()

        self.name = name
        self.freeze = freeze

    def run(self):
        loggerinfo = core.create_rotating_log('devdata', config.loginfopath)
        loggerinfo.debug("Thread #" + str(self.ident) + " '" + self.name + "': started")
        # print("\nThread #" + str(self.ident) + " '" + self.name + "': started\n")

        while not self.shutdown_flag.is_set():
            # Freeze time
            time.sleep(self.freeze)

            # Acquire lock
            threadlock.acquire()
            loggerinfo.debug("Thread #" + str(self.ident) + " '" + self.name + "': acquire lock")

            # Core operations
            result = core.get_emeter(config.shelly_server, config.shelly_port, config.shelly_emidx, loggerinfo)

            if result[0] == 200:
                # Store data into database
                utctime = result[2].strftime("%Y-%m-%dT%H:%M:%S.000Z")

                # Loading the response data into a dict variable
                http_resp = json.loads(result[1])

                power = http_resp["power"]
                reactive = http_resp["reactive"]
                voltage = http_resp["voltage"]
                total = http_resp["total"]

                loggerinfo.debug("Energy Meter Index: %s" % config.shelly_emidx)
                loggerinfo.debug("Instantaneous power (Watt): %s" % power)
                loggerinfo.debug("Instantaneous reactive power (Watt): %s" % reactive)
                loggerinfo.debug("RMS voltage (Volt): %s" % voltage)
                loggerinfo.debug("Total consumed energy (Wh): %s" % total)

                data = {
                    "idx": config.shelly_emidx,
                    "power": power,
                    "reactive": reactive,
                    "voltage": voltage,
                    "total": total
                }
                core.store2influx("emeter", utctime, data, loggerinfo)
            else:
                loggerinfo.error("No data acquired by the Shelly EM")

            # Release lock
            threadlock.release()
            loggerinfo.debug("Thread #" + str(self.ident) + " '" + self.name + "': release lock")

        loggerinfo.debug("Thread #" + str(self.ident) + " '" + self.name + "': stopped")
        # print("\nThread #" + str(self.ident) + " '" + self.name + "': stopped\n")


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


def service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ServiceExit


# Main
def main():
    arguments = core.options()

    daemon = arguments[0]
    method = arguments[1]

    if not daemon:
        loggerbase = core.create_rotating_log('default', config.logdefaultpath)
        loggerinfo = core.create_rotating_log('devdata', config.loginfopath)

        if method == "check-alive":
            core.check_alive(config.shelly_server, config.shelly_port, loggerbase)

        if method == "get-emeter":
            core.get_emeter(config.shelly_server, config.shelly_port, config.shelly_emidx, loggerinfo)
    else:
        j1 = None
        j2 = None

        # Register the signal handlers
        signal.signal(signal.SIGTERM, service_shutdown)
        signal.signal(signal.SIGINT, service_shutdown)

        # print("\nEnergy Meter Collector: Starting main program\n")

        # Start the job threads
        try:
            j1 = Alive("alive", 20)
            j2 = Collector("collector", 5)
            j1.start()
            j2.start()

            # Keep the main thread running, otherwise signals are ignored.
            while True:
                time.sleep(0.5)
        except ServiceExit:
            # Terminate the running threads.
            # Set the shutdown flag on each thread to trigger a clean shutdown of each thread.
            j1.shutdown_flag.set()
            j2.shutdown_flag.set()
            # Wait for the threads to close...
            j1.join()
            j2.join()

        # print("\nEnergy Meter Collector: Exiting main program\n")


if __name__ == "__main__":
    main()
