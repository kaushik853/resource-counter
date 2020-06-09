import click
import boto3
import sys
import botocore
import json
from test1 import except_decor
#pip install -U botocore==1.12.135 boto3==1.9.135
# added and saved not printed yet

global session
global resource_counts
global resource_totals

resource_counts = {}
resource_totals = {}
mperm = {}
session = boto3.session.Session(profile_name='adi_security')

@except_decor
def sagemaker_counter():
    region_list = session.get_available_regions(service_name='sagemaker')

    total_sagemaker_endpoints = 0

    for region in region_list:
        resource_counts[region] = {}
        sagemaker_cli = session.client(service_name='sagemaker', region_name=region)
        sagemaker_endpoint_counter = 0
        sagemaker_paginator = sagemaker_cli.get_paginator('list_endpoints')
        sagemaker_iterator = sagemaker_paginator.paginate()
        for sagemaker_ep in sagemaker_iterator:
            sagemaker_endpoint_counter += len(sagemaker_ep['Endpoints'])
        total_sagemaker_endpoints += sagemaker_endpoint_counter
        resource_counts[region]['Sagemaker'] = sagemaker_endpoint_counter
    resource_totals['Sagemaker'] = total_sagemaker_endpoints


sagemaker_counter()

print(resource_counts)
print(resource_totals)