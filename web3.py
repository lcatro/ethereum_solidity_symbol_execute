import requests
import json
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
        if result and result.has_key('result'):
            return result['result']
        return '0x'
    
    def get_storage_at(self,address,position,tag='latest') :
        ps = position
        
        if type(position) == int:
            ps = hex(position)

        result = self.send('eth_getStorageAt',[address,ps,tag])
        if result and result.has_key('result'):
            return result['result']
        print 'get store error %s' % result
        return '0x0'
    
    def send_transaction(self,fm,to,data,gas,gasPrice,value,nonce) :
        payload = {
            'from': fm,
        }

        if to :
            payload['to'] = to
        if gas :
            payload['gas'] = gas    
        if gasPrice :
            payload['gasPrice'] = gasPrice    
        if value :
            payload['value'] = value    
        if data :
            payload['data'] = data    
        if nonce :
            payload['nonce'] = nonce

        result = self.send('eth_sendTransaction',[payload])
        if result and result.has_key('result'):
            return True,result['result']
        return False,result

    def deploy_contract(self,fm,code,gas=hex(6000000),value=False,gasPrice=False,nonce=False) :
        return self.send_transaction(fm,False,'0x%s' % code,gas,value,gasPrice,nonce)
    
    def call_contract(self,fm,contract,data,gas=hex(6000000),value=False,gasPrice=False,nonce=False) :
        return self.send_transaction(fm,contract,data,gas,value,gasPrice,nonce)

    def get_transaction_receipt(self,hash) :
        result = self.send('eth_getTransactionReceipt',[hash])
        if result and result.has_key('result') and result['result']:
            return True,result['result']
        return False,result