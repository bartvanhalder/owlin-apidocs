# -*- coding:utf-8 -*-
import json
import random
import string
import time
import requests
from hashlib import sha256

class owlin:
    
    def __init__(self, login):
        self.login = login
    
    def request(self, data):
        if 'args' not in data:
            data['args'] = {}
        if 'value' not in data:
            data['value'] = 'null'
        
        if "requireLogin" not in data or data['requireLogin'] == True:
            session = self.getSecretKey()
            if 'error' in session:
                return session
            
            nonce       = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
            t           = str(int(time.time()))
            access_key  = sha256(session['secret_key'] + nonce + t).hexdigest()
            
            data['args']['nonce']      = nonce
            data['args']['time']       = t
            data['args']['access_key'] = access_key
            data['args']['session_id'] = session['session_id']
        
        new_args = {}
        for key, value in data['args'].iteritems():
            if isinstance(value, dict):
                key = key+"[]"
                value = json.dumps(value)
            new_args[key] = value
        data["args"] = new_args
        
        content = requests.get("https://newsroom.owlin.com/api/v1/%s/%s" % (data['method'], data['value']), params=data['args'], verify=False)
        return json.loads(content.text)
    
    def getSecretKey(self):
        session = False
        try:
            f = file("/tmp/%s" % self.login['email'], "r")
            session = json.load(f)
            f.close()
        except Exception, err:
            print "Read Error:", str(err)
        if session == False or 'secret_key' not in session:
            print "generating secret key"
            session = self.request({
               "method"        : "generate_secret",
               "args"          : self.login,
               "requireLogin"  : False
            })
            try:
                f = file("/tmp/%s" % self.login['email'], "w")
                f.write(json.dumps(session))
                f.close()
            except Exception, err:
                print "Write Error:", str(err)
        return session

