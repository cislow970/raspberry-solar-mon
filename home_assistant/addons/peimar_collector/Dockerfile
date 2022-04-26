ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache python3 py3-pip
RUN pip3 install pytz
RUN pip3 install influxdb

# Copy data for add-on
RUN mkdir -p /usr/lib/python3.9/site-packages/peimar/inverter
RUN mkdir -p /var/log/peimar
COPY peimar/__init__.py /usr/lib/python3.9/site-packages/peimar/
COPY peimar/__main__.py /usr/lib/python3.9/site-packages/peimar/
COPY peimar/inverter/__init__.py /usr/lib/python3.9/site-packages/peimar/inverter/
COPY peimar/inverter/config.py /usr/lib/python3.9/site-packages/peimar/inverter/
COPY peimar/inverter/core.py /usr/lib/python3.9/site-packages/peimar/inverter/
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
