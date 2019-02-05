import boto3, sys, os
from boto3.session import Session
from flask import Flask, jsonify, request
from datetime import datetime, timedelta

class computeManager:
    
    def getSecurityGroups(self, key, secret, region):
        try:
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            client = session.client('ec2',region)
            securityGroup = client.describe_security_groups()
        except Exception as e:
            print(e)
        return jsonify({'result':'success', 'data':securityGroup})

    def getKeyPairs(self, key, secret, region):
        try:
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            client = session.client('ec2',region)
            keyPairs = client.describe_key_pairs()
        except Exception as e:
            print(e)
        return jsonify({'result':'success','data':keyPairs})
    
    def getAMIs(self, region, key, secret):
        session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
        client = session.client('ec2', region_name=region)
        response = client.describe_images(Owners=['self','amazon'])
        data = {}
        for ami in response['Images']:
            id = ami['ImageId']
            desc = 'none'
            if 'Description' in ami:
                desc = ami['Description']
            data[id] = desc
        return jsonify({'result':'success', 'data':data})

    def showInstances(self, key, secret):
        try:
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            client = session.client('ec2')
            ec2_regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
            instanceId = {}
            for region in ec2_regions:
                conn = boto3.resource('ec2', aws_access_key_id=key, aws_secret_access_key=secret, region_name=region)
                instances = conn.instances.filter()
                for instance in instances:
                    if instance.state["Name"] == "running" or instance.state["Name"] == "stopped":
                        instanceInfo = {}
                        if instance.tags:
                            for tag in instance.tags:
                                if tag['Key'] == 'Name':
                                    instanceInfo['name'] = tag['Value']
                        instanceInfo['privateIP'] = instance.private_ip_address
                        instanceInfo['publicIP'] = instance.public_ip_address
                        instanceInfo['keyPair'] = instance.key_name
                        instanceInfo['platform'] = instance.platform
                        instanceInfo['monitoring'] = (instance.monitoring['State'])
                        instanceInfo['state'] = instance.state["Name"]
                        instanceInfo['region'] = region
                        instanceId[instance.id] = instanceInfo
        except Exception as e:
            return e
        return jsonify({'result':'success', 'data':instanceId})


    def createInstance(self, keyname, keyCreate, region, instanceType, instanceName, deleteOnTermination, volumeSize, ami, count, monitoring, securityGroup, key, secret):
        try:
            keyPairOut = 'none'
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            client = session.client('ec2', region_name=region)
            if keyCreate == 'yes':
                outfile = open(keyname, 'w')
                key_pair = client.create_key_pair(KeyName = keyname)
                keyPairOut = str(key_pair['KeyMaterial'])
                fileData = outfile.write(keyPairOut)
            response = client.run_instances(
                BlockDeviceMappings=[
                    {
                        'DeviceName': '/dev/xvda',
                        'Ebs': {
                            'DeleteOnTermination': deleteOnTermination,
                            'VolumeSize': volumeSize,
                            'VolumeType': 'gp2'
                        },
                    },
                ],
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': instanceName
                            },{
                                'Key': 'By',
                                'Value' : 'krifersam'
                            }
                        ]
                    },
                ],
                ImageId = ami,
                KeyName = keyname,
                InstanceType = instanceType,
                MaxCount = count,
                MinCount = count,
                Monitoring={
                    'Enabled': monitoring
                },
                SecurityGroupIds=[
                    securityGroup,
                ],
            )
            print(response)
        except Exception as e:
            return jsonify({'result':'success', 'data':str(e), 'keypair': keyPairOut})
        return jsonify({'result':'success', 'data':response, 'keypair': keyPairOut})

    def getStatus(self, region, id):
        try:
            client = boto3.client('ec2', region_name=region)
            response = client.describe_instance_status(InstanceIds=[id])
        except Exception as e:
            return e
        return jsonify({'result':'success', 'data':response})

    def changeInstanceState(self, key, secret, id, toState, region):
        session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
        client = session.client('ec2', region_name=region)
        response = 'none'
        try:
            if toState == 'stop':
                response = client.stop_instances(InstanceIds=[id])
            elif toState == 'start':
                response = client.start_instances(InstanceIds=[id])
            elif toState == 'terminate':
                response = client.terminate_instances(InstanceIds=[id])
        except Exception as e:
            print(e)
            return e
        return jsonify({'result':'success', 'data':response})

    def getMetricData(self, key, secret, region, nameSpace, metricName, dimensionName, dimensionValue, timeInterval, statistic, fromTime, toTime):
        try:
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            client = session.client('cloudwatch', region_name=region)

            stats = client.get_metric_statistics(
                Namespace=nameSpace,
                MetricName=metricName,
                StartTime=datetime.now() - timedelta(seconds=int(fromTime)),
                EndTime=datetime.now() - timedelta(seconds=int(toTime)),
                Statistics=[statistic],
                Period=int(timeInterval),
                Dimensions=[
                    {
                        'Name': dimensionName,
                        'Value': dimensionValue
                    },
                ],
            )
        except Exception as e:
            print(e)
            return e
        return jsonify({'result':'success', 'data':stats})

    def createSecurityGroup(self, key, secret, region, name, description):
        try:
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            client = session.client('ec2', region_name=region)
            securityGroup = client.create_security_group(
                Description=description,
                GroupName=name,
            )
        except Exception as e:
            print(e)
            return e
        return jsonify({'result':'success','data':securityGroup})

    def changeMonitoringState(self, key, secret, instanceId, region, to):
        try:
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            client = session.client('ec2', region_name=region)
            if to == 'enable':
                response = client.monitor_instances(InstanceIds=[instanceId])
            else:
                response = client.unmonitor_instances(InstanceIds=[instanceId])
        except Exception as e:
            print(e)
            return e
        return jsonify({'result':'success', 'data':response})

    def addSecurityGroupRules(self, key, secret, region, groupId, protocol, fromPort, toPort):
        try:
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            client = session.client('ec2', region_name=region)
            response = client.authorize_security_group_ingress(
                GroupId=groupId,
                IpPermissions=[
                    {'IpProtocol': protocol,
                     'FromPort': fromPort,
                     'ToPort': toPort,
                     }
                ],
            )
        except Exception as e:
            print(e)
            return e
        return jsonify({'result':'success','data':response})