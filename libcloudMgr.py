from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver
from flask import Flask, jsonify, request
from libcloud.storage.types import Provider, ContainerDoesNotExistError
from libcloud.storage.providers import get_driver
import subprocess
from datetime import datetime



class libCloudManager:
    def createContainer(self, key, secret, name):
        cls = get_driver(Provider.S3)
        driver = cls(key, secret)
        create = driver.create_container(name)
        print(create)
        return jsonify({'status':'success','data':str(create)})

    def uploadObject(self, key, secret, name, file):
        cls = get_driver(Provider.S3)
        driver = cls(key, secret)
        try:
            container = driver.get_container(name)
        except ContainerDoesNotExistError:
            container = driver.create_container(name)
        cmd = 'tar cvzpf - %s' % (file)
        pipe = subprocess.Popen(cmd, bufsize=0, shell=True, stdout=subprocess.PIPE)
        return_code = pipe.poll()
        object_name = 'backup-%s.tar.gz' % (datetime.now().strftime('%Y-%m-%d'))
        print('Uploading object...')
        while return_code is None:
            obj = container.upload_object_via_stream(iterator=pipe.stdout, object_name=object_name)
            print(obj)
            return_code = pipe.poll()
        return jsonify({'status':'success', 'data':str(obj)})