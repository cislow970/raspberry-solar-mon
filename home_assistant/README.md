# Home Assistant configuration

### Enable Samba

You need to enable ***Samba Share*** in the Add-ons section to upload files of Peimar Inverter Collector. To install add-ons, navigate to the **Configuration > Add-ons & Backups** panel in your Home Assistant frontend.

Remember to unlock access to shares from your LAN's IP addresses (allow_host in Samba configuration). You must also configure credentials for authentication to access to share.
At end of service configuration you need to restart Samba.

![Samba Share 1](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/images/ha01.png)

![Samba Share 2](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/images/ha02.png)

### Enable File Editor

You need to enable the ***File Editor*** in the Add-ons section to edit configuration files. To install add-ons, navigate to the **Configuration > Add-ons & Backups** panel in your Home Assistant frontend.

### Enable InfluxDB and configure database

You need to enable the ***InfluxDB*** in the Add-ons section to create time series database to store metrics of Peimar Inverter. To install add-ons, navigate to the **Configuration > Add-ons & Backups** panel in your Home Assistant frontend.

After, you must create database "peimar" with retention policy equal to 3650 days and configure user for connect to database (username = peimar / password = p31m4r).

![Create database](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/images/ha05.png)

![Configure database user](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/images/ha06.png)

### Build Docker container for Peimar Inverter Collector

1. You must connect to Microsoft Share of Home Assistant ```\\<IP_YOUR_HA_INSTALLATION>``` (login username = homeassistant / password = homeassistant) and copy to folder "addons" (if not exists then create it before) all folder ["peimar_collector"](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/addons/peimar_collector).

    ![Addons share](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/images/ha03.png)

    ![Copy collector to share](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/images/ha04.png)

2. After upload, you need to change ip address of Peimar Inverter in file **config.py** (path "addons/peimar_collector/peimar/inverter"):

    inverter_server = "IP_YOUR_PEIMAR_INVERTER"

3. Discovery the new local addon "Peimar Inverter PSI-J3000-TL" in **Configuration > Add-ons & Backups** panel in your Home Assistant frontend. 

    - Click on "Check for updates":

        ![Discovery local addons](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/images/ha07.png)

    - Select "Peimar Inverter PSI-J3000-TL" in Local add-ons section:

        ![Select local addons](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/images/ha08.png)

    - Build a docker container that includes python collector and start (configure auto start):

        ![Install local addons](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/images/ha09.png)

### Add configuration for custom sensors

Edit Home Assistant configuration file "configuration.yaml" by ***File Editor*** and add at end of file the following [configuration](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/config/configuration.yaml):


```
influxdb:
  host: 192.168.1.54
  ssl: false
  verify_ssl: false
  database: peimar
  username: peimar
  password: p31m4r
  exclude:
    entity_globs: "*"

sensor:
  - platform: influxdb
    host: 192.168.1.54
    ssl: false
    verify_ssl: false
    database: peimar
    username: peimar
    password: p31m4r
    queries:
      - name: Solar Power
        database: peimar
        measurement: '"peimar"."autogen"."device_status"'
        field: ac_out_grid_power
        where: 'time >= now() - 1d'
        unit_of_measurement: W
        group_function: last
      - name: Solar Total Energy
        database: peimar
        measurement: '"peimar"."autogen"."device_status"'
        field: tot_generated
        where: '"tot_generated" > 0 AND time >= now() - 30d'
        unit_of_measurement: kWh
        group_function: last
      - name: Solar Total Running
        database: peimar
        measurement: '"peimar"."autogen"."device_status"'
        field: tot_running_time
        where: '"tot_running_time" > 0 AND time >= now() - 30d'
        unit_of_measurement: Hours
        group_function: last
      - name: Solar Energy
        database: peimar
        measurement: '"peimar"."autogen"."device_status"'
        field: today_generated
        where: '"today_generated" >= 0 AND time >= now() - 1d'
        unit_of_measurement: kWh
        group_function: last
      - name: Solar Running
        database: peimar
        measurement: '"peimar"."autogen"."device_status"'
        field: today_running_time
        where: '"today_running_time" >= 0 AND time >= now() - 1d'
        unit_of_measurement: Hours
        group_function: last

homeassistant:
  customize_glob:
    sensor.solar_power:
      friendly_name: Peimar Power
      device_class: power
      state_class: measurement
      icon: mdi:solar-power
    sensor.solar_energy:
      friendly_name: Peimar Energy
      last_reset: '1970-01-01T00:00:00+00:00'
      device_class: energy
      state_class: total_increasing
      type: output
    sensor.solar_running:
      friendly_name: Peimar Running
      icon: mdi:clock-outline
    sensor.solar_total_energy:
      friendly_name: Peimar Total Energy
      last_reset: '1970-01-01T00:00:00+00:00'
      device_class: energy
      state_class: total_increasing
      type: output
    sensor.solar_total_running:
      friendly_name: Peimar Total Running
      icon: mdi:clock-outline
```

**Warning: you need to change value of key "host" with ip address assigned to Home Assistant in your installation.**

After modify of configuration you need to restart Home Assistant services.

### Verify inverter collector

Verify that the inverter collector is healty and that it stores data in the InfluxDB database. If everything is fine, you will see the value of the metrics in InfluxDB Explore.

![Verify collector](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/images/ha10.png)

### Create dashboard to show custom sensors

Result to mapping the custom sensors to Energy dashboard for Peimar Inverter metrics.

![Energy dashboard](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/images/ha12.png)

Create a custom dashboard, for example "SOLAR ENERGY" to show custom sensors:

Example:

![Custom dashboard](https://github.com/cislow970/raspberry-solar-mon/blob/main/home_assistant/images/ha11.png)

