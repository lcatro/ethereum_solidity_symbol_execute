

import subprocess
import web3
import executor
import context
import time

def create_contract(file_path,account,web3_req = False) :
    fopen_object = open(file_path, 'r')
    contract_code = fopen_object.read()
    status,contract_tx = web3_req.deploy_contract(account,contract_code)
    if not status :
      print 'send tx fail'
      print contract_tx
      exit()
    contract_address = False
    
    while(contract_address == False) :
      status,receipt = web3_req.get_transaction_receipt(contract_tx)
      if status :
        print receipt
        if receipt.has_key('contractAddress') and receipt['contractAddress'] :
          contract_address = receipt['contractAddress']
          print 'create contract success %s' % contract_address
          break
        else :
          print 'create contract fail!'
          print receipt
          break
      else :
        print 'tx pedding...%s' % contract_tx
        time.sleep(1)
    return contract_address

def test_contract(contract_address,payload,account,web3_req = False) :
    status,contract_tx = web3_req.call_contract(account,contract_address,payload)
     
    if not status :
      print 'send tx fail'
      print contract_tx
      exit()
    
    complete = False
    
    while(complete == False) :
      status,receipt = web3_req.get_transaction_receipt(contract_tx)
      if status :
        complete = True
        break
      else :
        print 'tx pedding...%s' % contract_tx
        time.sleep(1)
  
    return contract_tx

if __name__ == '__main__' :
    #req = web3.web3('https://mainnet.infura.io/')
    req = web3.web3('http://127.0.0.1:8545')
    account = '0xb0d74e9f9Ba20eEa9429649563bc745261e02De7'
    payload = '0x83f12fec000000000000000000000000000000000000000000000000000000000000002880000000000000000000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    contract_address = create_contract('./example/test_code_overflow2.txt',account,req)
    test_tx = test_contract(contract_address, payload, account, req)
    print 'send test tx complete %s' % test_tx
    #try_audit('./example/test_code_no_div_zero.txt')
    #try_audit('./example/test_code_no_overflow.txt')
    #try_audit('./example/test_code_overflow.txt')
    #try_audit('./example/test_code_overflow2.txt')
    #try_audit('./example/test_code_selfdestruct.txt')
    #try_audit('./example/test_code_call_from_calldata.txt')
    #try_audit('./example/test_code_call_from_init_no_control.txt')
    #try_audit('./example/test_code_bec.txt')
    #try_audit('./example/test_code2.txt')
