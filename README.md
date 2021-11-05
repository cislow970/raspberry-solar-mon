# raspberry-solar-mon
Home solar infrastructure (with ***Peimar Inverter***) monitoring based on Raspberry Pi 3 B+ using Grafana, InfluxDB, Custom Python Collector and Shelly EM.

### My solar infrastructure:

* 3KW solar panels system
* 3KW solar inverter monophase [Peimar](http://www.peimar.com/) model [PSI-J3000-TL](https://www.peimar.com/datasheet/Peimar_IT_Inverter_UNICUS_LINE.pdf)

### My monitoring system:

* [Shelly EM + 120A Clamp](https://www.shellyitalia.com/shelly-em/?gclid=Cj0KCQjw5oiMBhDtARIsAJi0qk1ZhzE05fYDJvK6hMz7YsG91ZkCaSz4PSUUMzi_Cpwu_yXUYV1bfTcaAoiFEALw_wcB) to measure the electrical consumption of my house
* [Raspberry Pi 3 B+](https://it.rs-online.com/web/p/raspberry-pi/1373331) with Raspbian OS
* Grafana 7.5.5
* InfluxDB 1.8.5
* Telegraf 1.18.2
* Custom python multithread collector for get metrics from _Peimar Inverter_ and _Shelly EM_ (compliant with Python 3)

Inverter Peimar, Shelly EM and Raspberry are connected to wifi network of my house.  
 
![EMDev1](https://github.com/cislow970/raspberry-solar-mon/blob/main/images/shellyem_dev1.jpg)
![EMDev2](https://github.com/cislow970/raspberry-solar-mon/blob/main/images/shellyem_dev2.jpg)
![Inverter1](https://github.com/cislow970/raspberry-solar-mon/blob/main/images/inverter1.png)
![Inverter2](https://github.com/cislow970/raspberry-solar-mon/blob/main/images/inverter2.png)
![EM](https://github.com/cislow970/raspberry-solar-mon/blob/main/images/shellyem.png)
![Analysis1](https://github.com/cislow970/raspberry-solar-mon/blob/main/images/solar-analysis1.png)
![Analysis2](https://github.com/cislow970/raspberry-solar-mon/blob/main/images/solar-analysis2.png)
![Analysis3](https://github.com/cislow970/raspberry-solar-mon/blob/main/images/solar-analysis3.png)
![Analysis4](https://github.com/cislow970/raspberry-solar-mon/blob/main/images/solar-analysis4.png)
![Trend](https://github.com/cislow970/raspberry-solar-mon/blob/main/images/solar-trend.png)

### Environment installation

* Install Raspbian OS on your Raspberry Pi 3 B+
* Install Grafana, InfluxDB and Telegraf on your Raspbian and enable services to starting automatically at system boot.
* Install Python 3.7 if it's missing on your system.

### InfluxDB configuration

* Login via SSH with username pi.
* Add to **.bashrc** of the user pi the following alias: ``alias influx='influx -precision rfc3339'``
* Reload **.bashrc** with the following command: ``source .bashrc``
* Copy configuration file **influxdb.conf** from repository folder **influxdb** to **/etc/influxdb/** path of your installation.
* Edit file **influxdb.conf** and disable authetication in [http] section: ``auth-enabled = false``
* Restart service and launch influxdb client with following command: ``influx``
* Create databases and users with grants:

	``CREATE DATABASE peimar``  
	``CREATE DATABASE telegraf``  
  
	``CREATE USER admin WITH PASSWORD p4ssw0rd WITH ALL PRIVILEGES``  
	``CREATE USER peimar WITH PASSWORD p31m4r``  
	``CREATE USER telegraf WITH PASSWORD t3l3gr4f``  
  
	``GRANT ALL ON peimar TO peimar``  
	``GRANT ALL ON telegraf TO telegraf``  
  
	``CREATE RETENTION POLICY "one_month" ON "telegraf" DURATION 4w REPLICATION 1``  
	``CREATE RETENTION POLICY "ten_years" ON "peimar" DURATION 520w REPLICATION 1``  
  
	``ALTER RETENTION POLICY "one_month" ON "telegraf" DURATION 4w REPLICATION 1 DEFAULT``  
	``ALTER RETENTION POLICY "ten_years" ON "peimar" DURATION 520w REPLICATION 1 DEFAULT``  
  
* Edit file **influxdb.conf** and enable authetication in [http] section: ``auth-enabled = true``
* Restart InfluxDB service: ``sudo systemctl restart influxdb.service``

The database ***peimar*** contains the metrics of the Inverter and Shelly EM.  
The database ***telegraf*** contains the metrics of Raspberry Pi and weather forecast from [OpenWeather](https://openweathermap.org/).  

### Telegraf configuration

* Copy configuration file **telegraf.conf** from repository folder **telegraf** to **/etc/telegraf/** path of your installation.
* Copy configuration file **openweather.conf** from repository folder **telegraf/telegraf.d** to **/etc/telegraf/telegraf.d** path of your installation.
* Register your account on OpenWeather, then insert infrastructure location and your id in **openweather.conf**.
* Restart Telegraf service: ``sudo systemctl restart telegraf.service``

### Python collector configuration

* Copy folder **peimar** from repository folder **python_collector** to **/usr/lib/python3.7** path in your installation.
* Copy folder **shelly** from repository folder **python_collector** to **/usr/lib/python3.7** path in your installation.
* Install python module for connection to Influx databases: ``sudo pip install influxdb``
* Copy all files from repository folder **init.d** to **/etc/init.d** path in your installation.
* Make the script **peimar-inverter** in the init.d directory executable by changing its permission: ``sudo chmod +x peimar-inverter``
* Make the script **shelly-em** in the init.d directory executable by changing its permission: ``sudo chmod +x shelly-em``
* Create folder **peimar** in **/var/log** path of your installation (owner: pi, group: pi).
* Create folder **shellyem** in **/var/log** path of your installation (owner: pi, group: pi).
* Enable all daemons at boot system:
  
	``sudo update-rc.d peimar-inverter defaults``  
	``sudo update-rc.d shelly-em defaults``  
  
* Change the IPs of the Inverter and Shelly EM to those of your network in the **config.py** files:
  
	**/usr/lib/python3.7/peimar/inverter/config.py**  
	**/usr/lib/python3.7/shelly/emeter/config.py**  
  
* Change timezone of your infrastructure in **config.py** file of peimar daemon:
  
	``timezone = pytz.timezone("Europe/Rome")``  
  
* Reboot system.
  
For the management of daemons:  
**sudo /etc/init.d/peimar-inverter {start|stop|forcekill|status|restart|reload}**  
**sudo /etc/init.d/shelly-em {start|stop|forcekill|status|restart|reload}**  
 
### Grafana configuration

* Copy configuration file **grafana.ini** from repository folder **grafana** to **/etc/grafana/** path of your installation.
* Copy image file **how_solar_power_works.png** from repository folder **grafana/images** to **/usr/share/grafana/public/img** path of your installation.
* Install Grafana plugins **grafana-clock-panel** and **larona-epict-panel** with following command:
  
	``sudo grafana-cli plugins install grafana-clock-panel``  
	``sudo grafana-cli plugins install larona-epict-panel``  
	``cd /var/lib/grafana/plugins/``  
	``sudo chown -R grafana:grafana grafana-clock-panel``  
	``sudo chown -R grafana:grafana larona-epict-panel``  
  
* Restart Grafana service: ``sudo systemctl restart grafana-server.service``
* Import all dashboards from repository folder **grafana/dashboards**.

