import boto3
from pprint import pprint


session = boto3.session.Session(profile_name='adi_security')
region_list = session.get_available_regions('accessanalyzer')
acc_cli = session.client(service_name='accessanalyzer')
for i in acc_cli.list_analyzers()['analyzers']:
    print(i.get('arn'))