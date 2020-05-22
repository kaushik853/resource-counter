import boto3
from pprint import pprint
import botocore

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

def eks_counter():
    region_list = session.get_available_regions(service_name='s3')
    region_list.remove('us-west-1')
    region_list.remove('us-west-2')

    total_eks_clusters = 0

    for region in region_list:
        resource_counts[region] = {}
        eks_cli = session.client(service_name='eks', region_name=region)
        eks_cluster_counter = 0
        eks_paginator = eks_cli.get_paginator('list_clusters')
        eks_iterator = eks_paginator.paginate()
        for eks_cls in eks_iterator:
            eks_cluster_counter += len(eks_cls['clusters'])
        total_eks_clusters += eks_cluster_counter
        resource_counts[region]['EKS'] = eks_cluster_counter
    resource_totals['EKS'] = total_eks_clusters

#eks_counter()

try:
     eks_counter()
except botocore.exceptions.ClientError as e:
    op = e.__dict__['operation_name']
    code = e.__dict__['response']['Error']['Code']
    msg = e.__dict__['response']['Error']['Message']
    print('{0} {1} Operation: {2}'.format(code,msg,op))
    mperm[op] = {'Code':code,'Message':msg}
print(resource_counts)
print(resource_totals)