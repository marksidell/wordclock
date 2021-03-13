'''
Get our AWS username
'''

import boto3


def get_username():
    ''' Return our AWS username
    '''
    return boto3.client('sts').get_caller_identity()['Arn'].split('/')[1]
