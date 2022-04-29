# Home Assistant configuration

### Enable Samba

You need to enable Samba Service in the Add-ons section to upload files of Peimar Inverter Collector. To install add-ons, navigate to the Configuration > Add-ons & Backups panel in your Home Assistant frontend.

![Samba Service](https://github.com/cislow970/raspberry-solar-mon/tree/main/home_assistant/home_assistant/images/ha01.png)

### Enable File Editor

You need to enable the File Editor in the Add-ons section to edit configuration files. To install add-ons, navigate to the Configuration > Add-ons & Backups panel in your Home Assistant frontend.

### Enable InfluxDB and configure database

You need to enable the InfluxDB in the Add-ons section to create time series database to store metrics of Peimar Inverter. To install add-ons, navigate to the Configuration > Add-ons & Backups panel in your Home Assistant frontend.

After, you must create database "peimar" and user for connect to database.

![Create database]()

![Configuration database user]()




### Build Docker container for Peimar Inverter Collector

You must connect to Microsoft Share of Home Assistant (```\\<IP_YOUR_HA_INSTALLATION>```) and copy to folder "addons" (if not exists then create it before) all folder !["peimar_collector"](https://github.com/cislow970/raspberry-solar-mon/tree/main/home_assistant/addons/peimar_collector).




### Add configuration for custom sensors

Edit Home Assistant configuration file "configuration.yaml" by ***File Editor*** and add at end of file the following configuration:

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


### Create dashboard to show custom sensors

Add to Energy dashboard the custom sensors for Peimar Inverter metrics.

Example:

