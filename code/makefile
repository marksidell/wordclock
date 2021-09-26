SHELL = /usr/bin/bash

# The base filename of the clock-specific configuration
CONFIG = mb

# The name of the AWS S3 bucket for logging and updates.
# Undefine this to disable the cron jobs
S3_BUCKET = mfs-wordclock

APT_PACKAGES = emacs hostapd dnsmasq

PYTHON_PACKAGES = RPI.GPIO adafruit-blinka rpi_ws281x adafruit-circuitpython-neopixel \
	adafruit-circuitpython-veml7700 adafruit-circuitpython-mlx90393 sparkfun-qwiic-adxl313 \
	pylint aiohttp timezonefinder pytz astral boto3 geomag wpasupplicantconf

VARS_DIR = /var/wordclock
UPDATES_DIR = $(VARS_DIR)/updates
WEB_DIR = $(VARS_DIR)/website
WEB_STATIC_DIR = $(WEB_DIR)/static

WEB_STATIC_FILES = favicon.ico script.js jquery.min.js w3.css
WEB_TARGET_FILES = $(WEB_DIR)/body.html $(addprefix $(WEB_STATIC_DIR)/,$(WEB_STATIC_FILES))

PACKAGE = wordclock
CONFIG_SRC_FILE = config/config_$(CONFIG).py
CONFIG_FILE = $(PACKAGE)/config.py
S3_CONFIG_FILE = $(PACKAGE)/s3config.py

TIMESTAMP_FILE = $(PACKAGE)/timestamp.txt

AUTHORIZED_KEYS_FILE = /home/pi/.ssh/authorized_keys

SERVICE = wc
SERVICE_SRC_FILE = $(SERVICE).service
SERVICE_FILE = /etc/systemd/system/$(SERVICE_SRC_FILE)

ifdef S3_BUCKET
CRON_FILES = /etc/cron.daily/wc-send-log /etc/cron.hourly/wc-get-update
endif

HOTSPOT = /usr/local/sbin/hotspot


# Install the word clock software
#
.PHONY: all
all: $(TIMESTAMP_FILE) $(SERVICE_FILE) $(WEB_TARGET_FILES) $(CRON_FILES) $(UPDATES_DIR)

# Install all prerequisite packages and do other necessary configuration
#
.PHONY: setup
setup: python3 packages hostname /etc/dnsmasq.conf config_hotspot /root/.aws/credentials

# For debugging: (re)install the software and restart the systemd wc service
#
.PHONY: reload
reload: all
	systemctl restart $(SERVICE)

# Start the systemd wc service
#
.PHONY: start
start:
	systemctl start $(SERVICE)

# Stop the systemd wc service
#
.PHONY: stop
stop:
	systemctl stop $(SERVICE)

.PHONY: clean
clean:
	-rm $(TIMESTAMP_FILE) $(CONFIG_FILE) $(S3_CONFIG_FILE)

# Configure the sshd daemon. This assumes you've modified the authorized_keys file to
# permit login with your own key pair.
#   - Disable password login
#   - Disable root login
#
.PHONY: config_sshd
config_sshd: $(AUTHORIZED_KEYS_FILE)
	sed '/^#PasswordAuth/s/^#PasswordAuth.*/PasswordAuthentication no/' --in-place /etc/ssh/sshd_config
	sed '/^#PermitRootLogin/s/^#PermitRootLogin.*/PermitRootLogin no/' --in-place /etc/ssh/sshd_config
	systemctl restart sshd

.PHONY: python3
python3:
	if [[ ! "$$(python --version 2>&1)" =~ "Python 3".* ]]; then \
		pip3 install --upgrade setuptools; \
		update-alternatives --install /usr/bin/python python $$(which python2) 1; \
		update-alternatives --install /usr/bin/python python $$(which python2) 1; \
	fi

.PHONY: packages
packages:
	apt -y install $(APT_PACKAGES)
	pip3 install $(PYTHON_PACKAGES)

.PHONY: hostname
hostname:
	if ! hostname | grep wordclock; then hostname wordclock; fi
	if ! grep wordclock /etc/hostname; then echo wordclock > /etc/hostname; fi
	sed '/^127.0.1.1.*raspberrypi/s/127.*/127.0.1.1\twordclock/' --in-place /etc/hosts

$(HOTSPOT):
	cd /usr/local/sbin; \
	wget https://raw.githubusercontent.com/rudiratlos/hotspot/master/hotspot; \
	chmod +x hotspot

.PHONY: config_hotspot
config_hotspot: $(HOTSPOT)
	sed '/^ap_net/s/10.3.141/10.0.0/' --in-place $(HOTSPOT)
	hotspot modpar self aptaddinstlist ""
	hotspot setup
	hotspot modpar hostapd ssid wordclock
	hotspot modpar hostapd wpa_passphrase wordclock
	hotspot modpar hostapd country_code US
	hotspot modpar crda REGDOMAIN US

/root/.aws/credentials:
	mkdir -p /root/.aws
	chmod 750 /root/.aws
	cp aws_credentials /root/.aws/credentials
	chmod 600 /root/.aws/credentials

/etc/dnsmasq.conf: dnsmasq.conf
	cp -f $^ $@

AUTHORIZED_KEYS_FILE: authorized_keys
	cp -f $^ $@

$(TIMESTAMP_FILE): $(PACKAGE)/*.py $(CONFIG_FILE) $(S3_CONFIG_FILE)
	pip3 install -e .
	echo date > $@

$(VARS_DIR):
	mkdir -p $@

$(UPDATES_DIR):
	mkdir -p $@

$(CONFIG_FILE): $(CONFIG_SRC_FILE)
	cp -f $^ $@

$(S3_CONFIG_FILE):
	echo -e "S3_BUCKET = \"$(S3_BUCKET)\"" > $@

$(WEB_DIR)/body.html: website/body.html
	mkdir -p $(WEB_DIR)
	cp -f $^ $@

$(WEB_STATIC_DIR)/jquery.min.js:
	mkdir -p $(WEB_STATIC_DIR)
	cd $(WEB_STATIC_DIR); wget https://ajax.googleapis.com/ajax/libs/jquery/1.10.1/jquery.min.js

$(WEB_STATIC_DIR)/w3.css:
	mkdir -p $(WEB_STATIC_DIR)
	cd $(WEB_STATIC_DIR); wget https://www.w3schools.com/w3css/4/w3.css

$(WEB_STATIC_DIR)/favicon.ico: website/favicon.ico
	mkdir -p $(WEB_STATIC_DIR)
	cp -f $^ $@

$(WEB_STATIC_DIR)/script.js: website/script.js
	mkdir -p $(WEB_STATIC_DIR)
	cp -f $^ $@

$(SERVICE_FILE): $(SERVICE_SRC_FILE)
	cp -f $^ $@
	systemctl enable $(SERVICE)

/etc/cron.daily/wc-send-log: cron/wc-send-log
	cp -f $^ $@
	chmod 755 $@

/etc/cron.hourly/wc-get-update: cron/wc-get-update
	cp -f $^ $@
	chmod 755 $@
