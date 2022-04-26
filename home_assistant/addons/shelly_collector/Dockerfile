ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache python3 py3-pip
RUN pip3 install influxdb

# Copy data for add-on
RUN mkdir -p /usr/lib/python3.9/site-packages/shelly/emeter
RUN mkdir -p /var/log/shellyem
COPY shelly/__init__.py /usr/lib/python3.9/site-packages/shelly/
COPY shelly/__main__.py /usr/lib/python3.9/site-packages/shelly/
COPY shelly/emeter/__init__.py /usr/lib/python3.9/site-packages/shelly/emeter/
COPY shelly/emeter/config.py /usr/lib/python3.9/site-packages/shelly/emeter/
COPY shelly/emeter/core.py /usr/lib/python3.9/site-packages/shelly/emeter/
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
