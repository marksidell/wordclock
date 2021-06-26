## The Source Code

### Directories

See the `README` file in each directory for more information.

| Directory | Description |
|------|-------------|
| <a href="https://github.com/marksidell/wordclock/tree/main/code/config" target="_blank">config</a> | Software config files, used to customize each clock. You'll have to write a config file for your particular clock. |
| <a href="https://github.com/marksidell/wordclock/tree/main/code/cron" target="_blank">cron</a> | cron scripts for uploading logs and downloading updates. |
| <a href="https://github.com/marksidell/wordclock/tree/main/code/website" target="_blank">website</a> | Source files for the clock's web page. |
| <a href="https://github.com/marksidell/wordclock/tree/main/code/wordclock" target="_blank">wordclock</a> | The word clock software, as a Python package. |

### Files

| File | Description |
|------|-------------|
| <a href="https://github.com/marksidell/wordclock/blob/main/code/authorized_keys" target="_blank">authorized_keys</a> | SSH public keys for logging into the Raspberry Pi. You'll have to change these, of course. |
| <a href="https://github.com/marksidell/wordclock/blob/main/code/dnsmasq.conf" target="_blank">dnsmasq.conf</a> | A tweaked version of `/etc/dnsmasq.conf`, for configuring the Pi's DHCP service. |
| <a href="https://github.com/marksidell/wordclock/blob/main/code/makefile" target="_blank">makefile</a> | For installing the software. |
| <a href="https://github.com/marksidell/wordclock/blob/main/code/setup.py" target="_blank">setup.py</a> | The Python package installation script. |
| <a href="https://github.com/marksidell/wordclock/blob/main/code/wc.service" target="_blank">setup.py</a> | The systemd service config file. |


