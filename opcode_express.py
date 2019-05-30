

INPUT_MEMORY = 'memory'
INPUT_CALL_DATA = 'calldata'
INPUT_CALL_SIZE = 'callsize'
INPUT_CALL_VALUE = 'callvalue'
INPUT_CALL_CALLER = 'caller'
INPUT_CODESIZE = 'codesize'
INPUT_CODE = 'code'
INPUT_EXTCODESIZE = 'extcodesize'
INPUT_EXTCODE = 'extcode'
INPUT_GAS = 'gas'
INPUT_GASPRICE = 'gasprice'
INPUT_GASLIMIT = 'gaslimit'
INPUT_DIFFICULTY = 'difficulty'
INPUT_BLOCKNUMBER = 'blocknumber'
INPUT_ORIGIN = 'origin'
INPUT_COINBASE = 'coinbase'
INPUT_ADDRESS = 'address'
INPUT_RETURNDATASIZE = 'returndatasize'

DEFAULT_INPUT_ADDRESS = '0xca35b7d915458ef540ade6068dfe2f44e8fa733c'
DEFAULT_INPUT_CONTRACT_ADDRESS = '0x14723a09acff6d2a60dcdf7aa4aff308fddc160c'


def replace_input(opcode_data) :
    if opcode_data.__class__ == opcode_call_caller :
        return INPUT_CALL_CALLER
    elif opcode_data.__class__ == opcode_call_value :
        return INPUT_CALL_VALUE
    elif opcode_data.__class__ == opcode_call_data :
        return opcode_data.make_express()
    elif opcode_data.__class__ == opcode_call_size :
        return INPUT_CALL_SIZE
    elif opcode_data.__class__ == opcode_code_size :
        return INPUT_CODESIZE
    elif opcode_data.__class__ == opcode_extcode_size :
        return INPUT_EXTCODESIZE
    elif opcode_data.__class__ == opcode_gas :
        return INPUT_GAS
    elif opcode_data.__class__ == opcode_gaslimit :
        return INPUT_GASLIMIT
    elif opcode_data.__class__ == opcode_gasprice :
        return INPUT_GASPRICE
    elif opcode_data.__class__ == opcode_blocknumber :
        return INPUT_BLOCKNUMBER
    elif opcode_data.__class__ == opcode_difficulty :
        return INPUT_DIFFICULTY
    elif opcode_data.__class__ == opcode_origin :
        return INPUT_ORIGIN
    elif opcode_data.__class__ == opcode_coinbase :
        return INPUT_COINBASE
    elif opcode_data.__class__ == opcode_address :
        return INPUT_ADDRESS
    elif opcode_data.__class__ == opcode_returndatasize :
        return INPUT_RETURNDATASIZE

    return opcode_data

def make_z3_init() :
    z3_init_list = [
        "callsize       = z3.BitVec('callsize',opcode_express.opcode_call_size.LENGTH * 8)" ,
        #"calldata       = z3.BitVec('calldata',opcode_express.opcode_call_data.LENGTH * 8)" ,
        "calldata       = z3.Array('calldata',z3.BitVecSort(opcode_express.opcode_call_data.LENGTH),z3.BitVecSort(8))" ,
        "callvalue      = z3.BitVec('callvalue',opcode_express.opcode_call_value.LENGTH * 8)" ,
        "caller         = z3.BitVec('caller',opcode_express.opcode_call_caller.LENGTH * 8)" ,
        "codesize       = z3.BitVec('codesize',opcode_express.opcode_code_size.LENGTH * 8)" ,
        "extcodesize    = z3.BitVec('extcodesize',opcode_express.opcode_extcode_size.LENGTH * 8)" ,
        "gas            = z3.BitVec('gas',opcode_express.opcode_gas.LENGTH * 8)" ,
        "gasprice       = z3.BitVec('gasprice',opcode_express.opcode_gasprice.LENGTH * 8)" ,
        "gaslimit       = z3.BitVec('gaslimit',opcode_express.opcode_gaslimit.LENGTH * 8)" ,
        "difficulty     = z3.BitVec('difficulty',opcode_express.opcode_difficulty.LENGTH * 8)" ,
        "blocknumber    = z3.BitVec('blocknumber',opcode_express.opcode_blocknumber.LENGTH * 8)" ,
        "origin         = z3.BitVec('origin',opcode_express.opcode_origin.LENGTH * 8)" ,
        "coinbase       = z3.BitVec('coinbase',opcode_express.opcode_coinbase.LENGTH * 8)" ,
        "address        = z3.BitVec('address',opcode_express.opcode_address.LENGTH * 8)" ,
        "returndatasize = z3.BitVec('returndatasize',opcode_express.opcode_returndatasize.LENGTH * 8)" ,
        "memory = z3.Array('memory',z3.BitVecSort(opcode_express.opcode_memory.LENGTH),z3.BitVecSort(8))" ,
    ]

    return z3_init_list

def is_input(opcode_data) :
    if  opcode_data.__class__ in [ opcode_call_caller , opcode_call_value , \
                                   opcode_call_data , opcode_call_size , \
                                   opcode_code_size , opcode_extcode_size ,\
                                   opcode_gas , opcode_gaslimit , \
                                   opcode_gasprice , opcode_blocknumber , \
                                   opcode_difficulty , opcode_origin , \
                                   opcode_coinbase , opcode_address , \
                                   opcode_returndatasize, opcode_memory ] :
        return True

    return False

def is_take_input(opcode_data) :
    result = False

    if 'opcode_data1' in dir(opcode_data) :
        if is_input(opcode_data.opcode_data1) :
            return True
        else :
            result = is_take_input(opcode_data.opcode_data1)

            if result :
                return True

    if 'opcode_data2' in dir(opcode_data) :
        if is_input(opcode_data.opcode_data2) :
            return True
        else :
            result = is_take_input(opcode_data.opcode_data2)

            if result :
                return True

    return result

def is_iszero(opcode_data) :
    if opcode_data.__class__ == opcode_iszero :
        return True

    return False

def has_iszero_inside(opcode_data) :
    result = False

    if is_iszero(opcode_data) :
        return True

    if 'opcode_data1' in dir(opcode_data) :
        if is_iszero(opcode_data.opcode_data1) :
            return True
        else :
            result = has_iszero_inside(opcode_data.opcode_data1)

            if result :
                return True

    if 'opcode_data2' in dir(opcode_data) :
        if is_iszero(opcode_data.opcode_data2) :
            return True
        else :
            result = has_iszero_inside(opcode_data.opcode_data2)

            if result :
                return True

    return result

def is_opcode_object(check_object) :
    if 'make_express' in dir(check_object) :
        return True
    
    return False

def can_make_express(opcode_data) :
    if 'make_express' in dir(opcode_data) :
        return True

    return False

def recurse_make_express(opcode_data) :
    if can_make_express(opcode_data) :
        return opcode_data.make_express()
    
    return opcode_data

def replace_express_to_logic_express(express_data) :
    express_data = express_data.replace('z3.Not','isZero')
    express_data = express_data.replace('z3.UDiv','div')

    return express_data


class opcode_call_caller :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_CALL_CALLER

class opcode_call_value :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_CALL_VALUE

class opcode_memory :
    LENGTH = 256 #2MB
    # LENGTH = 0x200000 #2MB
    ALIGNMENT = 32
    BYTE_LENGTH = 8

    def __init__(self,data_offset) :
        self.data_offset = data_offset

    def make_express(self) :  
        import z3
        parts = []
        memory = z3.Array('memory',z3.BitVecSort(opcode_memory.LENGTH),z3.BitVecSort(8))
        for i in range(32) :
            index = recurse_make_express(opcode_add(self.data_offset, i))
            if not is_take_input(self.data_offset) :
                exec('index = %s' % index)
                # print index
                # if index.__class__ == int :
                #     index = z3.BitVecVal(index, opcode_memory.LENGTH)         
            else:
                exec('index = z3.simplify(%s)' % index)
            if not index.__class__ == int :
                print index.sort()
            parts.append(memory[index])
        print 'end'
        express = z3.Concat(parts)
        express = z3.simplify(express)
        express = '%s' % express
        express = express.replace('z3.Concat','Concat')
        express = express.replace('Concat','z3.Concat')
        return express

class opcode_call_data :

    LENGTH = 256
    ALIGNMENT = 32
    BYTE_LENGTH = 8

    def __init__(self,data_offset) :
        self.data_offset = data_offset

    def make_express(self) :  
        # alignment_byte = opcode_mul(opcode_call_data.ALIGNMENT,opcode_call_data.BYTE_LENGTH)
        # end_offset = opcode_add(opcode_mul(self.data_offset,opcode_call_data.BYTE_LENGTH),alignment_byte)
        # shr_count = opcode_sub(opcode_call_data.LENGTH * opcode_call_data.BYTE_LENGTH,end_offset)
        # fill_data = 0x100 ** opcode_call_data.ALIGNMENT - 1
        # return opcode_and(opcode_shr(INPUT_CALL_DATA,shr_count),fill_data).make_express()
        import z3
        parts = []
        calldata = z3.Array('calldata',z3.BitVecSort(opcode_call_data.LENGTH),z3.BitVecSort(8))
        for i in range(32) :
            index = recurse_make_express(opcode_add(self.data_offset, i))
            
            if not is_take_input(self.data_offset) :
                exec('index = %s' % index)
                if index.__class__ == int :
                    index = z3.BitVecVal(index, opcode_call_data.LENGTH)               
            else:
                exec('index = z3.simplify(%s)' % index)

            parts.append(calldata[index])

        express = 'z3.Concat(%s)' % (parts)
        express = express.replace('z3.Concat','Concat')
        express = express.replace('Concat','z3.Concat')

        return express

class opcode_call_size :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_CALL_SIZE

class opcode_code_size :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_CODESIZE

class opcode_extcode_size :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_EXTCODESIZE

class opcode_gas :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_GAS

class opcode_gasprice :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_GASPRICE

class opcode_gaslimit :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_GASLIMIT

class opcode_difficulty :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_DIFFICULTY

class opcode_blocknumber :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_NUMBER

class opcode_origin :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_ORIGIN

class opcode_coinbase :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_COINBASE

class opcode_address :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_ADDRESS

class opcode_returndatasize :

    LENGTH = 32

    def __init__(self) :
        pass

    def make_express(self) :
        return INPUT_RETURNDATASIZE

class opcode_lt :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s < %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_gt :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s > %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_iszero :

    def __init__(self,opcode_data1) :
        self.opcode_data1 = opcode_data1
        self.is_disable_not = False     #  if nesting iszero for check ,let inside iszero to empty ,do not let it convert to not ..

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        if can_make_express(opcode_data1):
            return opcode_logic_not(opcode_data1).make_express()
        return '(%s == 0)' % (recurse_make_express(opcode_data1))

    def set_disale(self) :
        self.is_disable_not = True

class opcode_eq :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)
        return '(%s == %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_add :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s + %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_sub :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)
        return '(%s - %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_mul :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)
        
        return '(%s * %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_div :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        if  is_input(self.opcode_data1) or is_take_input(self.opcode_data1) or \
            is_input(self.opcode_data2) or is_take_input(self.opcode_data2) :

            return 'z3.UDiv(%s,%s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))
        calculate_express = 'div(%s,%s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))
        calculate_express = replace_express_to_logic_express(calculate_express)
        
        def div(number1,number2) :
            return number1 / number2

        def isZero(number1) :
            if number1 == 0 :
                return 1
            return 0

        print 'opcode_data1', recurse_make_express(opcode_data1)
        print 'opcode_data2', recurse_make_express(opcode_data2)
        exec('condition_temp_value = (%s)' % calculate_express)

        return condition_temp_value

class opcode_mod :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s %% %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_exp :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s ** %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_logic_not :

    def __init__(self,opcode_data1) :
        self.opcode_data1 = opcode_data1

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        return 'z3.Not(%s)' % (recurse_make_express(opcode_data1))

class opcode_arithmetic_not :

    def __init__(self,opcode_data1) :
        self.opcode_data1 = opcode_data1

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)

        return '~(%s)' % (recurse_make_express(opcode_data1))

class opcode_and :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s & %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_or :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s | %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_xor :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s ^ %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_shl :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s << %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_shr :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s >> %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

class opcode_sha3 :

    def __init__(self,memory_object) :  #  opcode sha3 take data_address,data_length .but we can conver it to memory object
        self.opcode_data1 = memory_object

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        
        return recurse_make_express(opcode_data1)

