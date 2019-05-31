
import z3
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

DEFAULT_INPUT_ADDRESS = 0xca35b7d915458ef540ade6068dfe2f44e8fa733c
DEFAULT_INPUT_CONTRACT_ADDRESS = 0x14723a09acff6d2a60dcdf7aa4aff308fddc160c


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

def is_z3_express(express_data) :
    if  express_data.__class__ in [ int, bool, z3.z3.BitVecNumRef, unicode, str ] :
        return False

    return True

def format_to_int(data) :
    if type(data) == str or type(data) == bool or type(data) == unicode :
        try :
            data = int(data)
        except :
            data = int(data,16)
    
    if data.__class__ == z3.z3.BitVecNumRef :
        data = data.as_long()

    return data

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
        

def opcode_write_memory(memory,offset,data,length = 32) :
    parts = []
    if not is_z3_express(length) :
        length = format_to_int(length)
        for i in range(length) :
            index = opcode_add(offset, i)
            high = (length - i) * 8 - 1
            low = high - 7
            memory = z3.Store(memory, index, z3.Extract(high, low, data))

        return z3.simplify(memory)
    
    print length
    exit()
    return z3.Concat(parts)

def opcode_get_memory(memory,offset,length = 32) :
    parts = []
    if not is_z3_express(length) :
        for i in range(format_to_int(length)) :
            index = opcode_add(offset, i)
            parts.append(memory[index])
        return z3.simplify(z3.Concat(parts))
    
    print length
    exit()
    return z3.Concat(parts)

class opcode_memory :
    LENGTH = 256 #2MB
    # LENGTH = 0x200000 #2MB
    ALIGNMENT = 32
    BYTE_LENGTH = 8

    def __init__(self,data_offset) :
        self.data_offset = data_offset

    def make_express(self) :  
        import z3
        

def opcode_call_data(calldata,data_offset,data_length = 32) :
    parts = []
    print data_length
    if not is_z3_express(data_length) :
        for i in range(format_to_int(data_length)) :
            index = opcode_add(data_offset, i)
            parts.append(calldata[index])
        return z3.simplify(z3.Concat(parts))
    print data_length
    exit()    
    return z3.Concat(parts)

def opcode_call_data_copy(calldata,memory,target_memory,call_offset,call_length = 32) :
    if not is_z3_express(call_length) :
        for i in range(format_to_int(call_length)) :
            index = opcode_add(call_offset, i)
            memory = z3.Store(memory, index, calldata[index])

        return z3.simplify(memory)
    
    for i in range(opcode_memory.LENGTH) :
            check_write_express = z3.And(i >= target_memory, i < target_memory + call_length)

            pos = z3.If(check_write_express, call_offset + i - target_memory, -1)
            
            check_get_calldata = z3.If(pos > opcode_call_data_config.LENGTH, 0, calldata[pos])
            
            get_data = z3.If(check_write_express, check_get_calldata, memory[i])
            
            memory = z3.Store(memory, i, get_data)
    
    return z3.simplify(memory)

class opcode_call_data_config :

    LENGTH = 256
    ALIGNMENT = 32
    BYTE_LENGTH = 8

    def __init__(self,data_offset) :
        self.data_offset = data_offset

    # def make_express(self) :  
    #     # alignment_byte = opcode_mul(opcode_call_data.ALIGNMENT,opcode_call_data.BYTE_LENGTH)
    #     # end_offset = opcode_add(opcode_mul(self.data_offset,opcode_call_data.BYTE_LENGTH),alignment_byte)
    #     # shr_count = opcode_sub(opcode_call_data.LENGTH * opcode_call_data.BYTE_LENGTH,end_offset)
    #     # fill_data = 0x100 ** opcode_call_data.ALIGNMENT - 1
    #     # return opcode_and(opcode_shr(INPUT_CALL_DATA,shr_count),fill_data).make_express()
    #     import z3
    #     parts = []
    #     calldata = z3.Array('calldata',z3.BitVecSort(opcode_call_data.LENGTH),z3.BitVecSort(8))
    #     for i in range(32) :
    #         index = recurse_make_express(opcode_add(self.data_offset, i))
            
    #         if not is_take_input(self.data_offset) :
    #             exec('index = %s' % index)
    #             if index.__class__ == int :
    #                 index = z3.BitVecVal(index, opcode_call_data.LENGTH)               
    #         else:
    #             exec('index = z3.simplify(%s)' % index)

    #         parts.append(calldata[index])

    #     express = 'z3.Concat(%s)' % (parts)
    #     express = express.replace('z3.Concat','Concat')
    #     express = express.replace('Concat','z3.Concat')

    #     return express

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

def opcode_lt(opcode_data1,opcode_data2) :

    return z3.If(opcode_data1 < opcode_data2, z3.BitVecVal(1, 256), z3.BitVecVal(0, 256))

class opcode_lt_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s < %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

def opcode_gt(opcode_data1,opcode_data2) :
    
    if not is_z3_express(opcode_data1) and not is_z3_express(opcode_data2) :
        return int(opcode_data1 > opcode_data2)
    
    return z3.If(opcode_data1 > opcode_data2, z3.BitVecVal(1, 256), z3.BitVecVal(0, 256))

class opcode_gt_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s > %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

def opcode_iszero(opcode_data1) :

    return z3.If(opcode_data1 == 0, z3.BitVecVal(1, 256), z3.BitVecVal(0, 256))

class opcode_iszero_ :

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

def opcode_eq(opcode_data1,opcode_data2) :
    
    return z3.If(opcode_data1 == opcode_data2, z3.BitVecVal(1, 256), z3.BitVecVal(0, 256))

class opcode_eq_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)
        return '(%s == %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

def opcode_add(opcode_data1,opcode_data2) :
    
    return z3.simplify(opcode_data1 + opcode_data2)

class opcode_add_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s + %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

def opcode_sub(opcode_data1,opcode_data2) :
    
    return z3.simplify(opcode_data1 - opcode_data2)

class opcode_sub_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)
        return '(%s - %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

def opcode_mul(opcode_data1,opcode_data2) :

    return z3.simplify(opcode_data1 * opcode_data2)

class opcode_mul_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)
        
        return '(%s * %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

def opcode_div(opcode_data1,opcode_data2) :
    
    return z3.simplify(z3.UDiv(opcode_data1, opcode_data2))

class opcode_div_ :

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

def opcode_mod(opcode_data1,opcode_data2) :

    return z3.simplify(opcode_data1 % opcode_data2)

class opcode_mod_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s %% %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

def opcode_exp(opcode_data1,opcode_data2) :

    if not is_z3_express(opcode_data1) and not is_z3_express(opcode_data2) :
        op1 = format_to_int(opcode_data1)
        op2 = format_to_int(opcode_data2)
        result = op1 ** op2
        return z3.BitVecVal(result, 256) 

    size = 0
    if is_z3_express(opcode_data1) or opcode_data1.__class__ == z3.z3.BitVecNumRef:
        size = opcode_data1.size()
        opcode_data1 = z3.BV2Int(opcode_data1)
    
    if is_z3_express(opcode_data2) or opcode_data1.__class__ == z3.z3.BitVecNumRef:
        if opcode_data2.size() > size :
            size = opcode_data2.size()
        opcode_data2 = z3.BV2Int(opcode_data2)
    
    return (z3.simplify(z3.Int2BV(opcode_data1 ** opcode_data2, size)))

class opcode_exp_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s ** %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

def opcode_logic_not(opcode_data1) :
    
    return z3.If(opcode_data1 == 0, z3.BitVecVal(1, 256), z3.BitVecVal(0, 256))
    

class opcode_logic_not_ :

    def __init__(self,opcode_data1) :
        self.opcode_data1 = opcode_data1

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        return 'z3.Not(%s)' % (recurse_make_express(opcode_data1))


def opcode_arithmetic_not(opcode_data1) :
    
    return z3.simplify(~(opcode_data1))

class opcode_arithmetic_not_ :

    def __init__(self,opcode_data1) :
        self.opcode_data1 = opcode_data1

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)

        return '~(%s)' % (recurse_make_express(opcode_data1))

def opcode_and(opcode_data1,opcode_data2) :

    return z3.simplify(opcode_data1 & opcode_data2)

class opcode_and_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s & %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

def opcode_or(opcode_data1,opcode_data2) :
    
    return z3.simplify(opcode_data1 | opcode_data2)

class opcode_or_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s | %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

def opcode_xor(opcode_data1,opcode_data2) :
    
    return z3.simplify(opcode_data1 ^ opcode_data2)

class opcode_xor_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s ^ %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

def opcode_shl(opcode_data1,opcode_data2) :
    
    return z3.simplify(opcode_data1 << opcode_data2)

class opcode_shl_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s << %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))

def opcode_shr(opcode_data1,opcode_data2) :
    
    return z3.simplify(opcode_data1 >> opcode_data2)

class opcode_shr_ :

    def __init__(self,opcode_data1,opcode_data2) :
        self.opcode_data1 = opcode_data1
        self.opcode_data2 = opcode_data2

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        opcode_data2 = replace_input(self.opcode_data2)

        return '(%s >> %s)' % (recurse_make_express(opcode_data1),recurse_make_express(opcode_data2))


def opcode_sha3(opcode_data1) :
    #  opcode sha3 take data_address,data_length .but we can conver it to memory object
    return opcode_data1


class opcode_sha3_ :

    def __init__(self,memory_object) :  #  opcode sha3 take data_address,data_length .but we can conver it to memory object
        self.opcode_data1 = memory_object

    def make_express(self) :
        opcode_data1 = replace_input(self.opcode_data1)
        
        return recurse_make_express(opcode_data1)

