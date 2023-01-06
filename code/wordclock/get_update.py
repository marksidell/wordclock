'''
Check S3 for an update. If found download and run it.

Updates are tar/gzip files. They may contain any content,
but must contain a file named "update", which we execute.
The S3 objects have names of the form:

  update/<username>/update-<yyyy><mm><dd><nn>.tgz

The <username> is the IAM username used by the clock to
authenticate to AWS, and are of the form "wordclock-<xx>".

We record which updates have been done, by creating local
directories with names of the form:

   /var/wordclock/updates/<yyyy><mm><dd><nn>

where the timestamp is the timestamp portion of the filename
downloaded from S3. We download a new update if its timestamp
is greater than the newest recorded timestamp.

The update process is:

1. List the objects in S3 and determine if there's a new update.
   Ignore object that are larger than 10MB.

2. Download the update tar object and save as a tmp file.

3. Verify that the hash of the file contents matches the S3
   object etag. Abandon any update that isn't valid.

4. Untar the file into "/var/wordclock/updates/<timestamp>/files".

5. Execute the "update" script.

6. Delete the "files" subdirectory and all of its contents,
   leaving just the timestamp directory to record that the update
   was processed.

7. Upload a log recording the result to S3.
'''

import subprocess
import os
import stat
import re
import tarfile
import traceback
import datetime
import tempfile
import shutil
from argparse import ArgumentParser
from hashlib import md5
from collections import namedtuple
import boto3
from wordclock.s3config import S3_BUCKET
from wordclock.username import get_username

UPDATES_DIR = '/var/wordclock/updates'
MAX_UPDATE_FILESIZE = 10000000
MIN_OBJ_CHUNK_SIZE = 1<<20
FILES_SUBDIR = 'files'
SCRIPT = 'update'


def parse_filename(item):
    ''' Parse an S3 object filename and return a corresponding tuple
    '''
    size = item['Size']

    if size > MAX_UPDATE_FILESIZE:
        return None

    fullname = item['Key']
    basename = fullname.split('/')[-1]
    match = re.match(r'update-(?P<timestamp>\d{10})\.tgz$', basename)

    if not match:
        return None

    return namedtuple('FilenameParts', 'fullname basename timestamp etag size')(
        fullname, basename, match.group('timestamp'), item['ETag'], size)


def download_update(s3_client, s3_filename):
    ''' Download an update file
    '''
    name = None

    try:
        with tempfile.NamedTemporaryFile(delete=False) as fil:
            name = fil.name
            shutil.copyfileobj(s3_client.get_object(Bucket=S3_BUCKET, Key=s3_filename)['Body'], fil)

    except Exception as err: #pylint: disable=broad-except
        if name and os.path.isfile(name):
            os.remove(name)

        raise RuntimeError('Unable to download file: {}'.format(err))

    return name


def verify_file(tmp_tarfile, s3_file):
    ''' Verify that the hash of the contents of the downloaded file matches the S3
        object's etag.
    '''
    etag = s3_file.etag[1:-1]     # remove enclosing quotes
    etag_split = etag.split('-')  # the format is either "<hasn>" or "<hash>-<nchunks>"

    if len(etag_split) == 1:
        with open(tmp_tarfile, 'rb') as fil:
            if etag == md5(fil.read()).hexdigest():
                return

    else:
        obj_hash = etag_split[0]
        n_chunks = int(etag_split[1])

        for chunk_size in (
                size for size in range(MIN_OBJ_CHUNK_SIZE, s3_file.size, MIN_OBJ_CHUNK_SIZE)
                if (s3_file.size + size - 1) // size == n_chunks):

            if obj_hash == chunked_hash(tmp_tarfile, chunk_size):
                return

    raise RuntimeError('File hash is not {}'.format(etag))


def chunked_hash(tmp_tarfile, chunk_size):
    ''' Calculate the etag hash of an S3 object for a given chunk size.
    '''
    concatenated_chunk_hashes = bytes()

    with open(tmp_tarfile, 'rb') as fil:
        while True:
            chunk = fil.read(chunk_size)

            if not chunk:
                break

            concatenated_chunk_hashes += md5(chunk).digest()

    return md5(concatenated_chunk_hashes).hexdigest()


def untar_file(tmp_tarfile, timestamp):
    ''' Untar the downloaded file and return the directory and script.
    '''
    try:
        target_dir = os.path.join(UPDATES_DIR, timestamp, FILES_SUBDIR)
        os.makedirs(target_dir)

        with tarfile.open(name=tmp_tarfile, mode='r:gz') as fil:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner) 
                
            
            safe_extract(fil, path=target_dir)

        script = os.path.join(target_dir, SCRIPT)

        if not os.path.isfile(script):
            raise RuntimeError('The tar file contains no script')

        os.chmod(script, stat.S_IRWXU)
        return namedtuple('Target', 'dir script')(target_dir, script)

    except Exception as err: #pylint: disable=broad-except
        raise RuntimeError('Unable to untar file: {}'.format(err))


def do_update(script):
    ''' Execute an update script
    '''
    try:
        return subprocess.check_output([script], stderr=subprocess.STDOUT).decode()

    except subprocess.CalledProcessError as err: #pylint: disable=broad-except
        raise RuntimeError('Script error: {}\n{}'.format(err.returncode, err.output.decode()))


def parse_args():
    ''' Parse command line args
    '''
    parser = ArgumentParser(
        prog='get-update',
        description='Download and process any update')

    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='Print verbose debugging statements')

    return parser.parse_args()


def main():
    ''' do it
    '''
    args = parse_args()
    s3_client = boto3.client('s3')
    username = None
    result = None
    newest_update = None
    tmp_tarfile = None
    target = None

    try:
        username = get_username()

        avail_updates = {
            filename_parts.timestamp: filename_parts
            for filename_parts in (
                parse_filename(item)
                for page in s3_client.get_paginator('list_objects_v2').paginate(
                    Bucket=S3_BUCKET,
                    Prefix='update/{}/'.format(username))
                for item in page.get('Contents', []))
            if filename_parts}

        dirname_re = re.compile(r'\d{10}$')

        have_update_timestamps = [
            dirname for dirname in os.listdir(UPDATES_DIR)
            if os.path.isdir(os.path.join(UPDATES_DIR, dirname)) and dirname_re.match(dirname)]

        if avail_updates:
            newest_update = avail_updates[max(avail_updates.keys())]

            if not have_update_timestamps or newest_update.timestamp > max(have_update_timestamps):
                tmp_tarfile = download_update(s3_client, newest_update.fullname)
                verify_file(tmp_tarfile, newest_update)
                target = untar_file(tmp_tarfile, newest_update.timestamp)
                result = do_update(target.script)

    except Exception as err: #pylint: disable=broad-except
        result = 'Exception: {}\n{}'.format(err, traceback.format_exc())

    finally:
        try:
            if tmp_tarfile and os.path.isfile(tmp_tarfile):
                os.remove(tmp_tarfile)

            if target and os.path.isdir(target.dir):
                shutil.rmtree(target.dir, ignore_errors=True)

        except Exception as err: #pylint: disable=broad-except
            print('Exception cleaning up: {}'.format(err))

    if args.debug:
        print(username, newest_update, tmp_tarfile, target, result)

    if result and username:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key='logs/{}/update-{}.txt'.format(username, datetime.datetime.utcnow().isoformat()),
            Body='{}\n{}'.format(newest_update.fullname if newest_update else 'unknown', result))
