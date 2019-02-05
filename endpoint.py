from flask import Flask, render_template ,session, escape, request, Response
from flask import url_for, redirect, send_from_directory
from flask import send_file, make_response, abort, jsonify
import json
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from aws import AWSManager
from compute import computeManager
from libcloudMgr import libCloudManager

app = Flask(__name__)
app.secret_key="aws_demo_app"

app.url_map.strict_slashes = False

awsMgr = AWSManager()
computeMgr = computeManager()
libMgr = libCloudManager()

@app.route('/')
def basic_pages(**kwargs):
    return make_response(open('aws.html').read())

@app.route('/ec2')
def ec2(**kwargs):
    return make_response(open('ec2.html').read())

@app.route('/getCredentials', methods=['POST'])
def getCredentials():
    file = open("/Users/krishnavaddepalli/credentials.txt", "r") 
    credentials = jsonify({'accesskey':file.readlines()})
    return credentials, 200, {'content-Type': 'application/json'} 

@app.route('/getAllMetricsAvailable', methods=['POST'])
def getAllMetricsAvailable():
    try:
        with open('metrics.json') as file:
            data = json.load(file)
            resp = jsonify({'result':'success', 'data':data})
    except  Exception as e:
        print(e)
    return resp, 200, {'content-Type': 'application/json'}

@app.route('/getAllRegions', methods=['POST'])
def getAllRegions():
    key = request.json['key']
    secret = request.json['secret']
    return awsMgr.getRegions(key, secret), 200, {'Content-Type': 'application/json'}

@app.route('/changeMonitoringState', methods=['POST'])
def changeMonitoringState():
    key = request.json['key']
    secret = request.json['secret']
    instanceId = request.json['instanceId']
    region = request.json['region']
    to = request.json['to']
    return computeMgr.changeMonitoringState(key, secret, instanceId, region, to), 200, {'Content-Type': 'application/json'}

@app.route('/createSecurityGroup', methods=['POST'])
def createSecurityGroup():
    key = request.json['key']
    secret = request.json['secret']
    region = request.json['region']
    name = request.json['name']
    description = request.json['description']
    return computeMgr.createSecurityGroup(key, secret, region, name, description), 200, {'Content-Type': 'application/json'}


@app.route('/addSecurityGroupRules', methods=['POST'])
def addSecurityGroupRules():
    key = request.json['key']
    secret = request.json['secret']
    region = request.json['region']
    groupId = request.json['groupId']
    protocol = request.json['protocol']
    fromPort = request.json['fromPort']
    toPort = request.json['toPort']
    return computeMgr.addSecurityGroupRules(key, secret, region, groupId, protocol, fromPort, toPort), 200, {'Content-Type': 'application/json'}

@app.route('/getSecurityGroups', methods=['POST'])
def getSecurityGroups():
    key = request.json['key']
    secret = request.json['secret']
    region = request.json['region']
    return computeMgr.getSecurityGroups(key, secret, region), 200, {'Content-Type': 'application/json'}

#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.create_key_pair
@app.route('/createInstance', methods=['POST'])
def createInstance():
    key = request.json['key']
    secret = request.json['secret']
    ami = request.json['ami']
    count = int(request.json['count'])
    deleteOnTermination = False
    if request.json['deleteOnTermination'] == 'True':
        deleteOnTermination = True
    instanceName = request.json['instanceName']
    instanceType = request.json['instanceType']
    keyname = request.json['keyname']
    monitoring = False
    keyCreate = request.json['keyCreate']
    if request.json['monitoring'] == 'True':
        monitoring = True
    region = request.json['region']
    securityGroup = request.json['securityGroup']
    volumeSize = int(request.json['volumeSize'])
    return computeMgr.createInstance(keyname, keyCreate, region, instanceType, instanceName, deleteOnTermination, volumeSize, ami, count, monitoring, securityGroup, key, secret), 200, {'Content-Type': 'application/json'}

@app.route('/getkeyPairs', methods=['POST'])
def getkeyPairs():
    key = request.json['key']
    secret = request.json['secret']
    region = request.json['region']
    return computeMgr.getKeyPairs(key, secret, region), 200, {'Content-Type': 'application/json'}

@app.route('/showInstances', methods=['POST'])
def showInstances():
    key = request.json['key']
    secret = request.json['secret']
    return computeMgr.showInstances(key, secret), 200, {'Content-Type': 'application/json'}


@app.route('/changeInstanceState', methods=['POST'])
def changeInstanceState():
    key = request.json['key']
    secret = request.json['secret']
    instanceId = request.json['instanceId']
    region = request.json['region']
    toState = request.json['toState']
    return computeMgr.changeInstanceState(key, secret, instanceId, toState, region), 200, {'Content-Type': 'application/json'}

@app.route('/createBuckets', methods=['POST'])
def createBuckets():
    key = request.json['key']
    secret = request.json['secret']
    location = request.json['location']
    name = request.json['name']
    return libMgr.createContainer(key, secret, name), 200, {'Content-Type':'application/json'}
#    return awsMgr.createBuckets(name, location, key, secret), 200, {'Content-Type': 'application/json'}

@app.route('/getAllBuckets', methods=['POST'])
def getAllBuckets():
    key = request.json['key']
    secret = request.json['secret']
    region = request.json['location']
    return awsMgr.getAllBuckets(key, secret), 200, {'Content-Type': 'application/json'}
    
@app.route('/deleteBucket', methods=['POST'])
def deleteBucket():
    key = request.json['key']
    secret = request.json['secret']
    location = request.json['location']
    name = request.json['name']
    return awsMgr.deleteBucket(name, location, key, secret), 200, {'Content-Type': 'application/json'}

@app.route('/uploadObject', methods=['POST'])
def uploadObject():
    filedata = request.files['file']
    objArr = request.form['objArr']
    jsonConvert = json.loads(objArr)
    key = jsonConvert['key']
    secret = jsonConvert['secret']
    bucketName = jsonConvert['bucketName']
    #return libMgr.uploadObject(key, secret, bucketName, filedata), 200, {'Content-Type': 'application/json'}
    return awsMgr.uploadObject(filedata, bucketName, key, secret), 200, {'Content-Type': 'application/json'}

@app.route('/getObjectsOfBucket', methods=['POST'])
def getObjectsOfBucket():
    key = request.json['key']
    secret = request.json['secret']
    bucketName = request.json['bucketName']
    return awsMgr.getObjectsOfBucket(bucketName, key, secret), 200, {'Content-Type': 'application/json'}

@app.route('/downloadObject', methods=['POST'])
def downloadObject():
    key = request.json['key']
    secret = request.json['secret']
    bucketName = request.json['bucketName']
    filename = request.json['fileName']
    saveName = request.json['saveName']
    return awsMgr.downloadObject(filename, bucketName, saveName, key, secret), 200, {'Content-Type': 'application/json'}

@app.route('/deleteObject', methods=['POST'])
def deleteObject():
    key = request.json['key']
    secret = request.json['secret']
    bucketName = request.json['bucketName']
    filename = request.json['fileName']
    return awsMgr.deleteObject(filename, bucketName, key, secret), 200, {'Content-Type': 'application/json'}

@app.route('/getAMIs', methods=['POST'])
def getAMIs():
    key = request.json['key']
    secret = request.json['secret']
    location = request.json['location']
    return computeMgr.getAMIs(location, key, secret), 200, {'Content-Type': 'application/json'}

@app.route('/getMetricData', methods=['POST'])
def getMetricData():
    key = request.json['key']
    secret = request.json['secret']
    region = request.json['region']
    nameSpace = request.json['nameSpace']
    metricName = request.json['metricName']
    dimensionName = request.json['dimensionName']
    dimensionValue = request.json['dimensionValue']
    timeInterval = request.json['timeInterval']
    statistic = request.json['statistic']
    fromTime = request.json['fromTime']
    toTime = request.json['toTime']
    return computeMgr.getMetricData(key, secret, region, nameSpace, metricName, dimensionName, dimensionValue, timeInterval, statistic, fromTime, toTime), 200, {'Content-Type': 'application/json'}

if __name__ == "__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 5000)))
