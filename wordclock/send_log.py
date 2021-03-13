'''
Upload the wc systemd service log to S3.
'''

import subprocess
import datetime
import boto3
from wordclock.s3config import S3_BUCKET
from wordclock.username import get_username


def main():
    ''' do it
    '''
    try:
        result = subprocess.check_output(
            ['journalctl', '-u', 'wc', '-n', '100'], stderr=subprocess.STDOUT).decode()

    except subprocess.CalledProcessError as err: #pylint: disable=broad-except
        result = 'Exception: {}\n{}'.format(err.returncode, err.output.decode())

    boto3.client('s3').put_object(
        Bucket=S3_BUCKET,
        Key='logs/{}/log-{}.txt'.format(get_username(), datetime.datetime.utcnow().isoformat()),
        Body=result.encode())
