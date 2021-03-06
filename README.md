# Word Clock

*View a 
<a href="https://www.youtube.com/watch?v=zEZTya65sJE" target="_blank">
video tour</a> of the word clock at YouTube.*

*Read all about the project on the
<a href="https://github.com/marksidell/wordclock/wiki" target="_blank">
wiki</a>.*

<a href="https://docs.google.com/spreadsheets/d/e/2PACX-1vQStdv3OZqONGQ3K7h9tHB2eYP5Ft4sCtjWJ84ZjRLP-8blSC_7sYkqp4zAAOey4n2pG4VfOC5HdfLr/pubhtml" target="_blank">
Bill of Materials</a>

## Repo Contents

### Directories

See the `README` file in each directory for more information.

| Directory | Description |
|------|-------------|
| <a href="https://github.com/marksidell/wordclock/tree/main/carbide3d" target="_blank">carbide3d</a> | Carbide Create designs for various clock components. |
| <a href="https://github.com/marksidell/wordclock/tree/main/code" target="_blank">code</a> | The code that needs to be copied to the Pi. |
| <a href="https://github.com/marksidell/wordclock/tree/main/code" target="_blank">docs</a> | The manual and other printed material. |
| <a href="https://github.com/marksidell/wordclock/tree/main/face" target="_blank">face</a> | Adobe Illustrator face designs for the clocks I've built. |
| <a href="https://github.com/marksidell/wordclock/tree/main/pcbs" target="_blank">pcbs</a> | KiCad printed circuit board designs. |

### Files

| File | Description |
|------|-------------|
| <a href="https://github.com/marksidell/wordclock/blob/main/aws-s3-policy-example.json" target="_blank">aws-s3-policy-example.json</a> | An example AWS IAM policy file for granting the word clock S3 permissions. |
| <a href="https://github.com/marksidell/wordclock/blob/main/manual.docx" target="_blank">manual.docx</a> | The user manual. |
| <a href="https://github.com/marksidell/wordclock/blob/main/pi-pinouts.md" target="_blank">pi-pinouts.md</a> | What passes for a schematic. |

## How It Works

### The Clock Program

The clock program, `wc`, runs as a systemd service. It must run as root to be able to
access the I2C hardware. The program uses the Python `asyncio` framework
for orchestrating real-time processes. You can also run the program from the command line,
with options to display verbose debugging messages.

### Calibrating the Compass

Each clock's magnetometer must be calibrated. The result of the calibration is stored
as a JSON file, `/var/wordclock/compass.json`. The word clock program reads the file
on startup. To perform a calibration, start the `calibrate` program and then slowly
rotate the magnetometer through all possible orientations.

### Phoning Home

The clock can be configured to phone home periodically, to upload systemd logs for
the clock service, and to download and install new software. The clock phones home
simply by reading and writing an AWS S3 bucket.

The clock uploads a log file daily, and saves it as `logs/<username>/log-<timestamp>.txt`,
where `<username>` is the IAM user name you'll create, as described below.

The clock checks for updates hourly. See the documentation in `wordclock/get_update.py`
for more information.

Here's what you'll need to do to make the phone-home feature work:

1. Create an S3 bucket.
2. Create an IAM User for your clock and grant it permission to access the bucket.
The file `aws-s3-policy-example.json` is an example IAM policy.
3. Create AWS API credentials for the user. Download the credential strings and store
them on the Pi, in the `[default]` section of file `/root/.aws/credentials`.

### Test Programs

The Python package includes several test programs:

| Program | Description
|---|---|
| tneo | Send test patterns to the neopixels. |
| tsense | Test and report values for the sensors: magnetometer, accelerometer, and light sensor. |
| calibrate | Calibrate the magnetometer. |

## Setting up the Pi

Notes to myself:

- Add my own ssh public key to `/home/pi/.ssh/authorized_keys`.

- Allow ssh agent forwarding when root by creating a sudoers file.
  This will allow me to use ssh to access github.

  ```
  visudo -f /etc/sudoers.d/ssh_agent_forwarding
  ```

  In VI add this line and save the file:

  ```
  Defaults env_keep += "SSH_AUTH_SOCK"
  ```

- Add this line to `/root/.ssh.config` so that I can ssh to other servers when root:

  ```
  User <my-username>
  ```

- Add wordclock-<xx> AWS credentials to `/root/.aws/credentials`:

  ```
  [default]
  aws_access_key_id = <key>
  aws_secret_access_key = <secret>
  ```


## Installation

1. Using `raspi-config`, enable `i2c`.

2. Get the contents of this repo onto the Pi.

   ```
   cd /home/pi
   git clone git@github.com:marksidell/wordclock.git
   ```

3. Create a custom `config-<xx>.py` file for your particular clock. The config files are stored
in the `config` directory.

4. Do one-time setup. This assumes you've modified the authorized_keys file to
permit login with your own key pair.

   ```bash
   cd <repo>/code
   sudo make config_sshd
   sudo make setup
   ```

5. Install everything:

   ```bash
   cd <repo>/code
   sudo make all [CONFIG=<config-file-base-name>] [S3_BUCKET=<s3-bucket-name>]
   ```
