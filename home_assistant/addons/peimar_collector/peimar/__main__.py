import time
import datetime
import signal
import threading
from threading import Thread
from peimar.inverter import config
from peimar.inverter import core


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
                result = core.check_alive(config.inverter_server, config.inverter_port, loggerbase)
                if result[0] != 200:
                    loggerbase.error("Inverter Web Server is offline or unreachable")

                    # Store data to database
                    utctime = result[1].strftime("%Y-%m-%dT%H:%M:%S.000Z")

                    data = {
                        "value": 0
                    }
                    core.store2influx("alive", utctime, data, loggerbase)

                    # Check night time hourly
                    now = datetime.datetime.now()

                    # Check daylight savings time
                    current_date = datetime.datetime(now.year, now.month, now.day)
                    if core.is_dst(current_date, config.timezone):
                        start_time = int(config.dst_start_hour) * 60 + int(config.dst_start_minute)
                        end_time = int(config.dst_end_hour) * 60 + int(config.dst_end_minute)
                    else:
                        start_time = int(config.start_hour) * 60 + int(config.start_minute)
                        end_time = int(config.end_hour) * 60 + int(config.end_minute)

                    current_time = now.hour * 60 + now.minute

                    if current_time >= end_time or current_time <= start_time:
                        loggerbase.info("Night time slot, no production (all production parameters are set to zero)")

                        data = {
                            "dc_in_pv1_voltage": 0.0,
                            "dc_in_pv1_current": 0.0,
                            "ac_out_grid_power": 0.0,
                            "ac_out_grid_frequency": 0.0,
                            "line1_voltage": 0.0,
                            "line1_current": 0.0,
                            "bus_voltage": 0.0,
                            "device_temperature": 0.0
                        }
                        core.store2influx("device_status", utctime, data, loggerbase)

                    time.sleep(20)      # delay before retry check status
                else:
                    loggerbase.info("Inverter Web Server is online!")

                    # Store data into database
                    utctime = result[1].strftime("%Y-%m-%dT%H:%M:%S.000Z")

                    data = {
                        "value": 1
                    }
                    core.store2influx("alive", utctime, data, loggerbase)
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
            result = core.device_status(config.inverter_server, config.inverter_port, loggerinfo)

            if result[0] == 200:
                metrics = result[1].split(",")

                tot_generated = int(metrics[1])/pow(10, int(config.cf[1]))
                tot_running_time = int(metrics[2])/pow(10, int(config.cf[2]))
                today_generated = int(metrics[3])/pow(10, int(config.cf[3]))
                today_running_time = int(metrics[4])/pow(10, int(config.cf[4]))
                dc_in_pv1_voltage = int(metrics[5])/pow(10, int(config.cf[5]))
                dc_in_pv1_current = int(metrics[6])/pow(10, int(config.cf[6]))
                ac_out_grid_power = int(metrics[23])/pow(10, int(config.cf[23]))
                ac_out_grid_frequency = int(metrics[24])/pow(10, int(config.cf[24]))
                line1_voltage = int(metrics[25])/pow(10, int(config.cf[25]))
                line1_current = int(metrics[26])/pow(10, int(config.cf[26]))
                bus_voltage = int(metrics[31])/pow(10, int(config.cf[31]))
                device_temperature = int(metrics[32])/pow(10, int(config.cf[32]))
                co2_reduction = int(metrics[33])/pow(10, int(config.cf[33]))
                running_state = int(metrics[34])

                loggerinfo.debug("Total generated (KWh): %s" % str(tot_generated))
                loggerinfo.debug("Total Running Time (h): %s" % str(tot_running_time))
                loggerinfo.debug("Today generated (KWh): %s" % str(today_generated))
                loggerinfo.debug("Today Running Time (h): %s" % str(today_running_time))
                loggerinfo.debug("DC Input - PV1 Voltage (V): %s" % str(dc_in_pv1_voltage))
                loggerinfo.debug("DC Input - PV1 Current (A): %s" % str(dc_in_pv1_current))
                loggerinfo.debug("AC Output - Grid-connected Power (W): %s" % str(ac_out_grid_power))
                loggerinfo.debug("AC Output - Grid-connected Frequency (Hz): %s" % str(ac_out_grid_frequency))
                loggerinfo.debug("Line1 Voltage (V): %s" % str(line1_voltage))
                loggerinfo.debug("Line1 Current (A): %s" % str(line1_current))
                loggerinfo.debug("Bus Voltage (V): %s" % str(bus_voltage))
                loggerinfo.debug("Device Temperature (%sC): %s" % (chr(176), str(device_temperature)))
                loggerinfo.debug("CO2 emission reduction (Kg): %s" % str(co2_reduction))
                loggerinfo.debug("Running State (1 = Waiting, 2 = Normal, 3 = Error): %s" % str(running_state))

                # Store data into database
                utctime = result[2].strftime("%Y-%m-%dT%H:%M:%S.000Z")

                data = {
                    "tot_generated": tot_generated,
                    "tot_running_time": tot_running_time,
                    "today_generated": today_generated,
                    "today_running_time": today_running_time,
                    "dc_in_pv1_voltage": dc_in_pv1_voltage,
                    "dc_in_pv1_current": dc_in_pv1_current,
                    "ac_out_grid_power": ac_out_grid_power,
                    "ac_out_grid_frequency": ac_out_grid_frequency,
                    "line1_voltage": line1_voltage,
                    "line1_current": line1_current,
                    "bus_voltage": bus_voltage,
                    "device_temperature": device_temperature,
                    "co2_reduction": co2_reduction,
                    "running_state": running_state
                }
                core.store2influx("device_status", utctime, data, loggerinfo)
            else:
                loggerinfo.error("No data acquired by the inverter")

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
            core.check_alive(config.inverter_server, config.inverter_port, loggerbase)

        if method == "device-status":
            core.device_status(config.inverter_server, config.inverter_port, loggerinfo)
    else:
        j1 = None
        j2 = None

        # Register the signal handlers
        signal.signal(signal.SIGTERM, service_shutdown)
        signal.signal(signal.SIGINT, service_shutdown)

        # print("\nInverter Collector: Starting main program\n")

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

        # print("\nInverter Collector: Exiting main program\n")


if __name__ == "__main__":
    main()
