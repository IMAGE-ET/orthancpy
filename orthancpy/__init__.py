#!/bin/python

import requests
import simplejson
from .models import Patient, Study, Series

json = simplejson.JSONDecoder()

class NewOrthancData():
    """ Access recently chnaged data as seen 
        through /changes interface
    """
    def __init__(self,orthanc):
        self.orthanc = orthanc

    def _get(self, changetype):
        last = 0
        done = False
        while not done:
            c = self.orthanc.changes(since=last)
            for x in c['Changes']: 
                if  x['ChangeType'] == changetype:
                    yield x['ID']
            done = c['Done']
            last = c['Last']

    def patients(self):
        """ returns list of "new" patients """
        return [Patient(self.orthanc,x) for x in self._get("StablePatient")]

    def studies(self):
        return [Study(self.orthanc,x) for x in self._get("StableStudy")]

    def series(self):
        return self._get("StableSeries")


class Orthanc():
    """ Direct interface to Orthanc REST API"""
    _ready = None

    def __init__(self, host=None, user=None, password=None):
        self.host     = host
        self.user     = user
        self.password = password
        self.get_new  = NewOrthancData(self)

    def changes(self,limit=10,since=0):
        params = {'limit':limit, 'since':since}
        resp = self.get('/changes', params=params)
        return resp

    def reset_changes(self):
        resp = self.delete('/changes')
        return resp

    def get_url(self, path, auth=None, params=None):
        if self.user:
            auth = (self.user, self.password)
        return '{}{}'.format(self.host,path)

    def get(self, path, auth=None, params=None):
        if self.user:
            auth = (self.user,self.password)
        req = requests.get('{}{}'.format(self.host,path),
                            auth = auth,
                            params = params)
        if req.status_code == 200:
            return json.decode(req.content)
        else:
            # TODO: throw error?
            return None

    def post(self, path, data, auth=None):
        if self.user:
            auth = (self.user,self.password)
        req = requests.post('{}{}'.format(self.host,path),
                            data = simplejson.dumps(data),
                            auth = auth)
        if req.status_code == 200:
            return json.decode(req.content)
        else:
            # TODO: throw error?
            return None

    def delete(self, path, auth=None):
        if self.user:
            auth = (self.user,self.password)
        req = requests.delete('{}{}'.format(self.host,path),
                            auth = auth)
        if req.status_code == 200:
            return True
        else:
            # TODO: throw error?
            return None

    def put(self, path, data):
        # TODO
        pass

    def patient(self, id):
        return Patient(self, id)

    def study(self, id):
        return Study(self, id)

    def series(self, id):
        return Series(self, id)

    def init_app(self, app):
        self.host = app.config['ORTHANC_URI']

    def ready(self):
        """ tests if connection is good """
        if self._ready is None:
            self._ready = False if self.get('/system') is None else True
        return self._ready

    @property
    def modalities(self):
        return self.get('/modalities')

