import click
import boto3
import sys
import botocore
import json
#pip install -U botocore==1.12.135 boto3==1.9.135
# added and saved not printed yet
mperm = {}


resource_counts = {}
resource_totals = {}

@click.command()
@click.option('--access', help='AWS Access Key. Otherwise will use the standard credentials path for the AWS CLI.')
@click.option('--secret', help='AWS Secret Key')
@click.option('--profile', help='If you have multiple credential profiles, use this option to specify one.')
@click.option('--region', help='Choose the region to test for (example: us-east-1, us-west-1), you can provide comma seperated list, like so: us-east-1,me-south-1,us-west-2')
@click.option('--show-regions', help='Show available regions',default=False,is_flag=True)
@click.option('--save-json','savejson', help='Save result regions as json',default=False,is_flag=True)
def controller(access, secret, profile, region,show_regions, savejson):
    global session
    global args
    cregion = region
    args = {'region':None}

    # lets addup a region flag
    if cregion:
        args['region']=cregion
    if access:
        click.echo('Access Key specified')
        if not secret:
            click.echo('Secret key not specified. A secret key must be provided when the command line access key option is provided.')
        else:
            click.echo('Establishing AWS session using the provided access key...')
            try:
                session = boto3.session.Session(aws_access_key_id=access, aws_secret_access_key=secret)
            except:
                click.echo('Error establishing AWS connection. Likely bad credentials provided.')
                sys.exit()
    elif profile:
        click.echo('Establishing AWS session using the profile- ' + profile)
        try:
            session = boto3.session.Session(profile_name=profile)
        except:
            click.echo('Error establishing AWS connection. Likely bad credentials provided.')
            sys.exit()
    else:
        click.echo('Establishing AWS session using default path credentials...')
        try:
            session = boto3.session.Session()
        except:
            click.echo('Error establishing AWS connection. Likely bad credentials provided.')
            sys.exit()

    # pull the account ID for use when needed for filtering
    sts_cli = session.client('sts')

    # account_id = iam.CurrentUser().arn.split(':')[4]
    account_id = sts_cli.get_caller_identity()["Account"]
    click.echo('Current account ID: ' + account_id)

    # Initialize dictionary to hold the counts. Pull the regions using EC2, since that is in every region.
    # Then build out the master list of regions to then fill in the service counts
    # Also build a separate dictionary for cross-region totals

    if show_regions:
        print('Available regions:')
        region_list = session.get_available_regions('ec2')
        for region in region_list:
            print(region)
        sys.exit(0)

    if args['region'] != None:
        if cregion.find(',') != -1:
            res = cregion.split(',')
            region_list = res
        else:
            region_list = [cregion]
            resource_counts[cregion] = {}
      #  print('Region: {0}'.format(args['region']))

    else:
        region_list = session.get_available_regions('ec2')
        for region in region_list:
            resource_counts[region] = {}
            #print('Region: {0}'.format(region))


    # iterate through the various services to build the counts
    click.echo('Counting resources across regions. This will take a few minutes...')
    click.echo(' ')
    ec2_counter(account_id,cregion)
    try:
        autoscaling_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
        balancer_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
        s3_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
        iam_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
        lambda_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}

    try:
        glacier_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
        cloudwatch_rules_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
        config_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
        cloudtrail_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
        sns_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
        kms_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
        dynamo_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
        rds_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
        workspace_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}
    try:
     eks_counter()
    except botocore.exceptions.ClientError as e:
        op = e.__dict__['operation_name']
        code = e.__dict__['response']['Error']['Code']
        msg = e.__dict__['response']['Error']['Message']
        print('{0} {1} Operation: {2}'.format(code,msg,op))
        mperm[op] = {'Code':code,'Message':msg}

    # show results
    #click.echo('Resources by region')
    click.echo(resource_counts)
    for key in sorted(resource_counts.keys()):
        click.echo(' ')
        click.echo('Ressources in {0}'.format(key))
        click.echo('-----------------------')
        for kitem, vitem in sorted(resource_counts[key].items()):
            click.echo("{} : {}".format(kitem, vitem))

    click.echo(' ')
    click.echo('Resource totals across all regions')
    click.echo('----------------------------------')
    for key, value in sorted(resource_totals.items()):
        click.echo("{} : {}".format(key, value))
    total = sum(resource_totals.values())
    click.echo('')
    click.echo('Total resources: ' + str(total))

    if savejson:
        click.echo('Saving json results in rc.json')
        click.echo('------------------------------')
        jd = json.dumps(resource_counts)
        fw = open('rc.json','w')
        fw.write(jd)
        fw.close()

# ec2 = boto3.client('ec2', region_name='us-west-2')

# ec2 = session.client('ec2', region_name='us-west-2')


def ec2_counter(account_id, cregion):
    # get list of regions supported by EC2 endpoint
    if cregion != None:
        if cregion.find(',') != -1:
            res = cregion.split(',')
            region_list = res
            for ncregion in region_list:
                resource_counts[ncregion] = {}
        else:
            region_list = [cregion]
            resource_counts[cregion] = {}

#        print('Choosen Region: {0}'.format(args['region']))
    else:
        region_list = session.get_available_regions('ec2')



    # initialize cross region totals
    total_instances = 0
    total_groups = 0
    total_volumes = 0
    total_snapshots = 0
    total_images = 0
    total_vpcs = 0
    total_subnets = 0
    total_peering_connections = 0
    total_acls = 0
    total_IPs = 0
    total_NAT = 0
    total_endpoints = 0

    for region in region_list:
        ec2 = session.resource('ec2', region_name=region)
        ec2client = session.client('ec2', region_name=region)
        print("Checking Region: {0}".format(region))

        # build the collections to count
        instance_iterator = ec2.instances.all()
        volume_iterator = ec2.volumes.all()
        security_group_iterator = ec2.security_groups.all()
        snapshot_iterator = ec2.snapshots.filter(OwnerIds=[account_id])
        image_iterator = ec2.images.filter(Owners=[account_id])
        vpc_iterator = ec2.vpcs.all()
        subnet_iterator = ec2.subnets.all()
        vpc_peering_connection_iterator = ec2.vpc_peering_connections.all()
        network_acl_iterator = ec2.network_acls.all()
        vpc_address_iterator = ec2.vpc_addresses.all()

        try:
            nat_gateways = ec2client.get_paginator('describe_nat_gateways')
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}

        try:
            nat_gateway_iterator = nat_gateways.paginate()
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}

        try:
            endpoints = ec2client.describe_vpc_endpoints()
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}

        # count resources
        # try to get instances
        try:
            instance_counter = len(list(instance_iterator))
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}
            instance_counter = 0
            
        try:
            group_counter = len(list(security_group_iterator))
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}
            group_counter = 0

        try:
            volume_counter = len(list(volume_iterator))
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}
            volume_counter = 0

        try:
            snapshot_counter = len(list(snapshot_iterator))
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}
            snapshot_counter = 0

        try:
            image_counter = len(list(image_iterator))
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}
            image_counter = 0

        try:
            vpc_counter = len(list(vpc_iterator))
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}
            vpc_counter = 0

        try:
            subnet_counter = len(list(subnet_iterator))
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}
            subnet_counter = 0

        try:
            peering_counter = len(list(vpc_peering_connection_iterator))
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}
            peering_counter = 0


        try:
            acl_counter = len(list(network_acl_iterator))
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}
            acl_counter = 0

        try:
            ip_counter = len(list(vpc_address_iterator))
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}
            ip_counter = 0

        gateway_counter = 0
        try:
            for gateway in nat_gateway_iterator:
                try:
                    gateway_counter += len(gateway['NatGateways'])
                except botocore.exceptions.ClientError as e:
                    op = e.__dict__['operation_name']
                    code = e.__dict__['response']['Error']['Code']
                    msg = e.__dict__['response']['Error']['Message']
                    print('{0} {1} Operation: {2}'.format(code,msg,op))
                    mperm[op] = {'Code':code,'Message':msg}
            endpoint_counter = len(endpoints['VpcEndpoints'])
        except botocore.exceptions.ClientError as e:
            op = e.__dict__['operation_name']
            code = e.__dict__['response']['Error']['Code']
            msg = e.__dict__['response']['Error']['Message']
            print('{0} {1} Operation: {2}'.format(code,msg,op))
            mperm[op] = {'Code':code,'Message':msg}
            endpoint_counter = 0 

        # add to the cross region totals
        total_instances = total_instances + instance_counter
        total_groups += group_counter
        total_volumes += volume_counter
        total_snapshots += snapshot_counter
        total_images += image_counter
        total_vpcs += vpc_counter
        total_subnets += subnet_counter
        total_peering_connections += peering_counter
        total_acls += acl_counter
        total_IPs += ip_counter
        total_NAT += gateway_counter
        total_endpoints += endpoint_counter

        # Add the counts to the per-region counter
        resource_counts[region]['instances'] = instance_counter
        resource_counts[region]['volumes'] = volume_counter
        resource_counts[region]['security_groups'] = group_counter
        resource_counts[region]['snapshots'] = snapshot_counter
        resource_counts[region]['images'] = image_counter
        resource_counts[region]['vpcs'] = vpc_counter
        resource_counts[region]['subnets'] = subnet_counter
        resource_counts[region]['peering connections'] = peering_counter
        resource_counts[region]['network ACLs'] = acl_counter
        resource_counts[region]['elastic IPs'] = ip_counter
        resource_counts[region]['NAT gateways'] = gateway_counter
        resource_counts[region]['VPC Endpoints'] = endpoint_counter


    resource_totals['Instances'] = total_instances
    resource_totals['Volumes'] = total_volumes
    resource_totals['Security Groups'] = total_groups
    resource_totals['Snapshots'] = total_snapshots
    resource_totals['Images'] = total_images
    resource_totals['VPCs'] = total_vpcs
    resource_totals['Subnets'] = total_subnets
    resource_totals['VPC Peering Connections'] = total_peering_connections
    resource_totals['Network ACLs'] = total_acls
    resource_totals['Elastic IP Addresses'] = total_IPs
    resource_totals['NAT Gateways'] = total_NAT
    resource_totals['VPC Endpoints'] = total_endpoints

def iam_counter():
    iam = session.resource('iam', region_name='us-west-2')

    user_iterator = iam.users.all()
    group_iterator = iam.groups.all()
    role_iterator = iam.roles.all()
    policy_iterator = iam.policies.filter(Scope='Local')
    saml_provider_iterator = iam.saml_providers.all()

    total_users = len(list(user_iterator))
    total_groups = len(list(group_iterator))
    total_roles = len(list(role_iterator))
    total_policies = len(list(policy_iterator))
    total_saml = len(list(saml_provider_iterator))

    resource_totals['Users'] = total_users
    resource_totals['Groups'] = total_groups
    resource_totals['Roles'] = total_roles
    resource_totals['Policies'] = total_policies
    resource_totals['SAML Providers'] = total_saml

def autoscaling_counter():
    # get list of supported regions
    region_list = session.get_available_regions('autoscaling')

    # initialize cross region totals
    total_autoscaling_groups = 0
    total_launch_configurations = 0

    # iterate through regions and count
    for region in region_list:
        client = session.client('autoscaling', region_name=region)

        # pull data using paginators
        autoscaling = client.get_paginator('describe_auto_scaling_groups')
        configurations = client.get_paginator('describe_launch_configurations')
        autoscale_iterator = autoscaling.paginate()
        configurations_iterator = configurations.paginate()

        # initialize region counts
        autoscale_count = 0
        configuration_count = 0

        for autoscale in autoscale_iterator:
            autoscale_count += len(autoscale['AutoScalingGroups'])
        for configuration in configurations_iterator:
            configuration_count += len(configuration['LaunchConfigurations'])

        total_autoscaling_groups += autoscale_count
        total_launch_configurations += configuration_count


        resource_counts[region]['autoscale groups'] = autoscale_count
        resource_counts[region]['launch configurations'] = configuration_count


    resource_totals['Autoscale Groups'] = total_autoscaling_groups
    resource_totals['Launch Configurations'] = total_launch_configurations

def balancer_counter():
    # get list of supported regions
    elb_region_list = session.get_available_regions('elb')
    elbv2_region_list = session.get_available_regions('elbv2')

    # initalize cross region totals
    elb_total = 0
    elbv2_total = 0

    # First count up the classic ELBs
    for region in elb_region_list:
        elb = session.client('elb', region_name=region)

        # pull data using paginator
        elb_paginator = elb.get_paginator('describe_load_balancers')
        elb_iterator = elb_paginator.paginate()

        #initialize region count
        elb_counter = 0

        for balancer in elb_iterator:
            elb_counter += len(balancer['LoadBalancerDescriptions'])

        elb_total += elb_counter
        resource_counts[region]['classic load balancers'] = elb_counter

    # Now count up the application and network load balancers
    for region in elbv2_region_list:
        elb = session.client('elbv2', region_name=region)

        # pull data using paginator
        elb_paginator = elb.get_paginator('describe_load_balancers')
        elb_iterator = elb_paginator.paginate()

        #initialize region count
        elb_counter = 0

        for balancer in elb_iterator:
            elb_counter += len(balancer['LoadBalancers'])

        elbv2_total += elb_counter
        resource_counts[region]['application and network load balancers'] = elb_counter
    resource_totals['Classic Load Balancers'] = elb_total
    resource_totals['Application and Network Load Balancers'] = elbv2_total

def s3_counter():
    total_buckets = 0
    # S3 gives you a full count no matter what the region setting
    s3 = session.resource('s3', region_name='us-west-2')
    bucket_iterator = s3.buckets.all()
    bucket_counter = len(list(bucket_iterator))
    total_buckets += bucket_counter
    # resource_counts[region]['s3 buckets'] = bucket_counter
    resource_totals['S3 Buckets'] = total_buckets

def lambda_counter():
    region_list = session.get_available_regions('lambda')

    total_functions = 0

    for region in region_list:
        aws_lambda = session.client('lambda', region_name=region)
        function_counter = 0
        function_paginator = aws_lambda.get_paginator('list_functions')
        function_iterator = function_paginator.paginate()
        for function in function_iterator:
            function_counter += len(function['Functions'])
        total_functions += function_counter
        resource_counts[region]['lambdas'] = function_counter
    resource_totals['Lambda Functions'] = total_functions

def glacier_counter():
    region_list = session.get_available_regions('glacier')

    total_vaults = 0

    for region in region_list:
        glacier = session.resource('glacier', region_name=region)
        vault_iterator = glacier.vaults.all()
        vault_counter = len(list(vault_iterator))
        total_vaults += vault_counter
        resource_counts[region]['glacier vaults'] = vault_counter
    resource_totals['Glacier Vaults'] = total_vaults

def cloudwatch_rules_counter():
    region_list = session.get_available_regions('events')

    total_events = 0

    for region in region_list:
        cloudwatch = session.client('events', region_name=region)
        rules = cloudwatch.list_rules()
        events_counter = len(rules['Rules'])
        total_events += events_counter
        resource_counts[region]['cloudwatch rules'] = events_counter
    resource_totals['Cloudwatch Rules'] = total_events

def config_counter():
    region_list = session.get_available_regions('config')

    total_config_rules = 0

    for region in region_list:
        config = session.client('config', region_name=region)
        config_rules_counter = 0
        config_rules_paginator = config.get_paginator('describe_config_rules')
        config_rules_iterator = config_rules_paginator.paginate()
        for rule in config_rules_iterator:
            config_rules_counter += len(rule['ConfigRules'])
        total_config_rules += config_rules_counter
        resource_counts[region]['config rules'] = config_rules_counter
    resource_totals['Config Rules'] = total_config_rules

def cloudtrail_counter():
    region_list = session.get_available_regions('cloudtrail')

    total_trails = 0

    for region in region_list:
        cloudtrail = session.client('cloudtrail', region_name=region)
        trails = cloudtrail.describe_trails()
        trails_counter = len(trails['trailList'])
        total_trails += trails_counter
        resource_counts[region]['cloudtrail trails'] = trails_counter
    resource_totals['CloudTrail Trails'] = total_trails

def sns_counter():
    region_list = session.get_available_regions('sns')

    total_topics = 0

    for region in region_list:
        sns = session.resource('sns', region_name=region)
        topic_iterator = sns.topics.all()
        topic_counter = len(list(topic_iterator))
        total_topics += topic_counter
        resource_counts[region]['sns topics'] = topic_counter
    resource_totals['SNS Topics'] = total_topics

def kms_counter():
    region_list = session.get_available_regions('kms')

    total_keys = 0

    for region in region_list:
        kms = session.client('kms', region_name=region)
        keys_counter = 0
        kms_paginator = kms.get_paginator('list_keys')
        kms_iterator = kms_paginator.paginate()
        for key in kms_iterator:
            keys_counter += len(key['Keys'])
        total_keys += keys_counter
        resource_counts[region]['kms keys'] = keys_counter
    resource_totals['KMS Keys'] = total_keys

def dynamo_counter():
    region_list = session.get_available_regions('dynamodb')

    total_tables = 0

    for region in region_list:
        dynamodb = session.resource('dynamodb', region_name=region)
        table_iterator = dynamodb.tables.all()
        table_counter = len(list(table_iterator))
        total_tables += table_counter
        resource_counts[region]['dynamo tables'] = table_counter
    resource_totals['Dynamo Tables'] = total_tables

def rds_counter():
    region_list = session.get_available_regions('rds')
    #print(region_list)

    total_dbinstances = 0

    for region in region_list:
        print(region)
        rds = session.client('rds', region_name=region)
        dbinstances_counter = 0
        rds_paginator = rds.get_paginator('describe_db_instances')
        rds_iterator = rds_paginator.paginate()
        for instance in rds_iterator:
            dbinstances_counter += len(instance['DBInstances'])
        total_dbinstances += dbinstances_counter
        resource_counts[region]['rds instances'] = dbinstances_counter
    resource_totals['RDS Instances'] = total_dbinstances

def workspace_counter():
    region_list = session.get_available_regions(service_name='workspaces')

    total_workspaces = 0

    for region in region_list:
        work_cli = session.client(service_name='workspaces', region_name=region)
        workspace_counter = 0
        workspace_paginator = work_cli.get_paginator('describe_workspaces')
        workspace_iterator = workspace_paginator.paginate()
        for workspace in workspace_iterator:
            workspace_counter += len(workspace['Workspaces'])
        total_workspaces += workspace_counter
        resource_counts[region]['workspace'] = workspace_counter
    resource_totals['Workspaces'] = total_workspaces

def eks_counter():
    region_list = session.get_available_regions(service_name='s3')
    region_list.remove('us-west-1')
    region_list.remove('us-west-2')

    total_eks_clusters = 0

    for region in region_list:
        #resource_counts[region] = {}
        eks_cli = session.client(service_name='eks', region_name=region)
        eks_cluster_counter = 0
        eks_paginator = eks_cli.get_paginator('list_clusters')
        eks_iterator = eks_paginator.paginate()
        for eks_cls in eks_iterator:
            eks_cluster_counter += len(eks_cls['clusters'])
        total_eks_clusters += eks_cluster_counter
        resource_counts[region]['EKS'] = eks_cluster_counter
    resource_totals['EKS'] = total_eks_clusters

if __name__ == "__main__":
    controller()