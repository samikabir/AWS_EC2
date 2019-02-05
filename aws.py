import boto3, sys, os
from boto3.session import Session
from flask import Flask, jsonify, request

class AWSManager:
    
    def getRegions(self, key, secret):
        session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
        client = session.client('ec2')
        regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
        return jsonify({'result':'success', 'data':regions})
    
    def getAllBuckets(self, key, secret):
        session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
        s3 = session.resource('s3')
        buckets = []
        for bucket in s3.buckets.all():
            buckets.append(bucket.name)
        return jsonify({'result':'success', 'data':buckets})
    
    def createBuckets(self, bucketName, bucketLocation, key, secret):
        print(key)
        print(secret)
        try:
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            s3 = session.client('s3', bucketLocation)
            response = s3.create_bucket(ACL='public-read-write',
                             Bucket=bucketName,
                             CreateBucketConfiguration={
                                 'LocationConstraint': bucketLocation
                             })
            return jsonify({'result':'success', 'data':response})
        except Exception as e:
            return e

    def deleteBucket(self, bucketName, bucketLocation, key, secret):
        try:
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            s3 = session.client('s3', bucketLocation)
            obj = session.resource('s3')
            obj.Bucket(bucketName).objects.delete()
            response = s3.delete_bucket(Bucket=bucketName)
        except Exception as e:
            return e
        return jsonify({'result':'success', 'data':response})

    def deleteAllObj(self, session, bucketName):
        obj = session.resource('s3')
        obj.Bucket(bucketName).objects.delete()
    
    def uploadObject(self, data, bucket, key, secret):
        try:
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            filename = data.filename
            bucketObj = session.resource('s3')
            response = bucketObj.Bucket(bucket).put_object(
                ACL= 'public-read-write',
                Body= data,
                Key=filename,
                Tagging='bucket upload by Krishna'
                )
            result = 'failed'

            my_bucket = bucketObj.Bucket(bucket)
            for file in my_bucket.objects.all():
                print(file.key)
                
            if str(response) is not None:
                result = 'success'
            return jsonify({'result':result})
        except Exception as e:
            print(e)
            return jsonify({'result':'failed'})

    def deleteObject(self, filename, bucketName, key, secret):
        try:
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            bucketObj = session.resource('s3')
            obj = bucketObj.Object(bucketName, filename)
            obj.delete()
            my_bucket = bucketObj.Bucket(bucketName)
            for file in my_bucket.objects.all():
                print(file.key)
            return jsonify({'result':'success'})    
        except Exception as e:
            print(e)
            return jsonify({'result':'failed'}) 
        
    def getObjectsOfBucket(self, bucketName, key, secret):
        session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
        s3 = session.resource('s3')
        files = []
        bucket = s3.Bucket(bucketName)
        for s3_file in bucket.objects.all():
            print(s3_file)
            files.append(s3_file.key)
        return jsonify({'result':'success', 'data':files})

    def downloadObject(self, filename, bucketName, saveName, key, secret):
        try:
            session = Session(aws_access_key_id=key, aws_secret_access_key=secret)
            bucketObj = session.resource('s3')
            response = bucketObj.Bucket(bucketName).download_file(filename, saveName)
            result = 'failed'
            if str(response) is not None:
                result = 'success'
            return jsonify({'result':result})
        except Exception as e:
            print(e)
            return jsonify({'result':'failed'}) 
