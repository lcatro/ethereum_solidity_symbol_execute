import requests

class web3 :

    def __init__(self,source) :
        if not source :
            print 'need web3 source'
            return
        self.web3_source = source

    def send(self,method,params) :
        payload = {'jsonrpc': '2.0','method':method,'params':params,'id':1}
        r = requests.post(self.web3_source, json=payload)
        if r.status_code == requests.codes.ok :
            return r.json()
        return False

    def get_code(self,address,tag='latest') :
        result = self.send('eth_getCode',[address,tag])
        if result and result['result']:
            return result['result']
        return '0x'
    
    def get_storage_at(self,address,position,tag='latest') :
        ps = position
        
        if type(position) == int:
            ps = hex(position)

        result = self.send('eth_getStorageAt',[address,ps,tag])
        if result and result['result']:
            return result['result']
        print 'get store error %s' % result
        return '0x0'