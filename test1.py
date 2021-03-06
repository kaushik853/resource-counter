import boto3
from pprint import pprint
import botocore

def except_decor(func):
    def _except_decor(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}
            return mperm[op]
    return _except_decor


global session
global resource_counts
global resource_totals

resource_counts = {}
resource_totals = {}
mperm = {}
session = boto3.session.Session(profile_name='adi_security')
#region_list = session.get_available_regions(service_name='s3')
#print(region_list)
#region_list1 = session.get_available_regions('rds')
#print(region_list1)

# region_list = session.get_available_regions('accessanalyzer')
# acc_cli = session.client(service_name='accessanalyzer')
# for i in acc_cli.list_analyzers()['analyzers']:
#     print(i.get('arn'))

# ec2_re = session.resource(service_name='ec2')
# x = ec2_re.instances.all()
# print(len(list(x)))

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

#eks_counter()


sagemaker_counter()

print(resource_counts)
print(resource_totals)