

import subprocess

import executor
import context



def disassmbly_contract(evm_bytecode_file_path) :
    popen_object = subprocess.Popen(['./evm','disasm',evm_bytecode_file_path],stdout = subprocess.PIPE,stderr = subprocess.PIPE)
    disassmbly_data = popen_object.stdout.read()

    if  not -1 == disassmbly_data.find('invalid') or \
        not -1 == disassmbly_data.find('encoding/hex') or \
        not len(disassmbly_data.strip()) :
        return False

    disassmbly_data = disassmbly_data.split('\n')
    source_bytecode_data = disassmbly_data[0].strip()
    disassmbly_data = disassmbly_data[ 1 : ]  #  first line is source bytecode print
    format_opcode_data = {}
    format_bytecode_data = {}

    for index in disassmbly_data :
        if not len(index) :
            continue

        opcode = index.split(' ')

        if 'Missing' == opcode[1] :
            continue

        opcode_address = int('0x' + opcode[0].split(':')[0],16)  #  clean the ":" in address common and convert hex number
        opcode_code = opcode[1]

        if 2 < len(opcode) :
            opcode_data = opcode[ 2 : ]
        else :
            opcode_data = []

        format_opcode_data[opcode_address] = context.opcode_object(opcode_address,opcode_code,opcode_data)

    for index in range(0,len(source_bytecode_data),2) :
        format_bytecode_data[index / 2] = int(source_bytecode_data[index],16) * 10 + int(source_bytecode_data[index + 1],16)

    return context.disassmbly_object(format_opcode_data,format_bytecode_data)

def split_contract_code(target_disassmbly_object) :  #  Return (Contract_init,Contract_runtime)
    disassmbly_address_list = target_disassmbly_object.get_disassmbly_address_list()
    disassmbly_address_list_length = target_disassmbly_object.get_disassmbly_address_list_length()
    runtime_entry = -1

    for index in range(disassmbly_address_list_length) :
        if  'PUSH1' == target_disassmbly_object.get_disassmbly_by_address_index(index).get_opcode() and \
            'PUSH1' == target_disassmbly_object.get_disassmbly_by_address_index(index + 1).get_opcode() and \
            'MSTORE' == target_disassmbly_object.get_disassmbly_by_address_index(index + 2).get_opcode() and \
            'PUSH1' == target_disassmbly_object.get_disassmbly_by_address_index(index + 3).get_opcode() and '0x04' == target_disassmbly_object.get_disassmbly_by_address_index(index + 3).get_opcode_data(0) and \
            'CALLDATASIZE' == target_disassmbly_object.get_disassmbly_by_address_index(index + 4).get_opcode() :
            runtime_entry = disassmbly_address_list[index]

            break
        elif 'PUSH1' == target_disassmbly_object.get_disassmbly_by_address_index(index).get_opcode() and \
            'PUSH1' == target_disassmbly_object.get_disassmbly_by_address_index(index + 1).get_opcode() and \
            'MSTORE' == target_disassmbly_object.get_disassmbly_by_address_index(index + 2).get_opcode() and \
            'CALLDATASIZE' == target_disassmbly_object.get_disassmbly_by_address_index(index + 3).get_opcode() :
            runtime_entry = disassmbly_address_list[index]

            break

    if runtime_entry > 0 :
        return (target_disassmbly_object.split_bytecode(0,runtime_entry - 1),
                target_disassmbly_object.split_bytecode(runtime_entry))

    return (False,target_disassmbly_object)

def try_audit(file_path) :
    contract_object = disassmbly_contract(file_path)
    contract_init_code,contract_runtime_code = split_contract_code(contract_object)

    #contract_init_code.print_code()
    #contract_runtime_code.print_code()

    state_object = context.state_object()

    '''
    if contract_init_code :
        contract_init_code_executor = executor.executor(contract_init_code,state_object,context.execute_context())

        contract_init_code_executor.run()
    '''
    
    contract_runtime_code_executor = executor.executor(contract_runtime_code,state_object,context.execute_context())

    contract_runtime_code_executor.run()

    branches_count = contract_runtime_code_executor.get_execute_branch_count() #contract_init_code_executor.get_execute_branch_count() + \
    instrutments_count = contract_runtime_code_executor.get_execute_instrutment_count()#contract_init_code_executor.get_execute_instrutment_count() + \

    print '\033[1;32mExecuting Branches :',branches_count,'\033[0m'
    print '\033[1;32mExecuting Instrutments :',instrutments_count,'\033[0m'
    print ''


if __name__ == '__main__' :
    #try_audit('./example/test_code_no_div_zero.txt')
    #try_audit('./example/test_code_no_overflow.txt')
    #try_audit('./example/test_code_overflow.txt')
    try_audit('./example/test_code_overflow2.txt')
    #try_audit('./example/test_code_selfdestruct.txt')
    #try_audit('./example/test_code_call_from_calldata.txt')
    #try_audit('./example/test_code_call_from_init_no_control.txt')
    #try_audit('./example/test_code_bec.txt')
    #try_audit('./example/test_code2.txt')