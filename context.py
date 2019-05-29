
import copy

import opcode_express


class opcode_object :

    def __init__(self,address,opcode,opcode_data = []) :
        self.address = address
        self.opcode = opcode
        self.opcode_data = opcode_data

    def get_address(self) :
        return self.address

    def get_opcode(self) :
        return self.opcode

    def has_opcode_data(self) :
        if len(self.opcode_data) :
            return True
        else :
            return False

    def get_opcode_data(self,data_offset = -1) :
        if not -1 == data_offset and self.has_opcode_data() :
            return self.opcode_data[data_offset]
        else :
            return self.opcode_data

    def __str__(self) :
        opcode_data = ''

        for opcode_data_index in self.opcode_data :
            opcode_data += str(opcode_data_index) + ','

        if len(opcode_data) :
            opcode_data = opcode_data[ : -1 ]

        return '%s %s' % (self.opcode,opcode_data)

    def __repe__(self) :
        return self.__str__()

class disassmbly_object :

    def __init__(self,disassmbly_data,bytecode_data) :
        self.disassmbly_data = disassmbly_data
        self.bytecode_data = bytecode_data
        self.disassmbly_address_list = self.sort_disassmbly_address()
        self.bytecode_address_list = self.sort_bytecode_address()

    def get_bytecode(self,index) :
        return self.bytecode_data[index]

    def get_bytecode_data(self,start,length) :
        bytecode_data_address_list = self.bytecode_address_list
        new_bytecode_address_list = bytecode_data_address_list[ start : start + length ]
        result = []

        for index in new_bytecode_address_list :
            result.append(self.bytecode_data[bytecode_data_address_list[index]])

        return result

    def sort_bytecode_address(self,is_reverse = False) :
        return sorted(self.bytecode_data.keys(),reverse = is_reverse)

    def get_disassmbly_data(self) :
        return self.disassmbly_data

    def get_disassmbly_data_length(self) :
        return len(self.disassmbly_data)

    def sort_disassmbly_address(self,is_reverse = False) :
        return sorted(self.disassmbly_data.keys(),reverse = is_reverse)

    def get_disassmbly_address_list(self) :
        return self.disassmbly_address_list

    def get_disassmbly_address_list_length(self) :
        return len(self.disassmbly_address_list)

    def get_disassmbly_by_index(self,index) :
        return self.disassmbly_data.values()[index]

    def get_disassmbly_by_address(self,address) :
        if not address in self.disassmbly_address_list :
            return False

        return self.disassmbly_data[address]

    def get_disassmbly_by_address_index(self,address_index) :
        if address_index >= len(self.disassmbly_address_list) :
            return False

        return self.disassmbly_data[self.disassmbly_address_list[address_index]]

    def split_bytecode(self,start_offset,end_offset = -1) :
        disassmbly_address_list = self.disassmbly_address_list

        if not start_offset in disassmbly_address_list :
            return False

        if 0 < end_offset :
            if not end_offset in disassmbly_address_list or start_offset >= end_offset:
                return False
        else :
            end_offset = disassmbly_address_list[-1]

        address_list_start_offset = disassmbly_address_list.index(start_offset)
        address_list_end_offset = disassmbly_address_list.index(end_offset)
        new_disassmbly_address_list = disassmbly_address_list[address_list_start_offset : address_list_end_offset + 1]
        new_disassmbly_data = {}

        for index in new_disassmbly_address_list :
            new_disassmbly_data[index - start_offset] = opcode_object(self.disassmbly_data[index].get_address() - start_offset,
                                                                      self.disassmbly_data[index].get_opcode(),
                                                                      self.disassmbly_data[index].get_opcode_data())

        bytecode_data_address_list = self.bytecode_address_list
        new_bytecode_address_list = bytecode_data_address_list[start_offset : end_offset + 1]
        new_bytecode_data = {}

        for index in bytecode_data_address_list :
            new_bytecode_data[index] = self.bytecode_data[index]

        return disassmbly_object(new_disassmbly_data,new_bytecode_data)

    def append_bytecode(self,new_disassmbly_data) :
        disassmbly_address_list = self.disassmbly_address_list

        if len(disassmbly_address_list) :
            last_offset = disassmbly_address_list[-1]
            last_opcode = self.disassmbly_data[last_offset].get_opcode()

            if last_opcode.startswith('PUSH') :  #  only PUSH will takes more byte-length,other bytecode length is 1
                push_length = int(last_opcode[ 4 : ])
                last_offset += 1 + push_length
            else :
                last_offset += 1
        else :
            last_offset = 0

        new_disassmbly_address_list = new_disassmbly_data.get_disassmbly_address_list()
        new_disassmbly_start_offset = new_disassmbly_address_list[0]

        for index in new_disassmbly_address_list :
            fix_new_disassmbly_offset = index - new_disassmbly_start_offset
            new_opcode_object = opcode_object(index,
                                              new_disassmbly_data.get_disassmbly_by_address(index).get_opcode(),
                                              new_disassmbly_data.get_disassmbly_by_address(index).get_opcode_data())
            self.disassmbly_data[last_offset + fix_new_disassmbly_offset] = new_opcode_object

        self.disassmbly_address_list = self.sort_disassmbly_address()

    def print_code(self) :
        disassmbly_address_list = self.get_disassmbly_address_list()

        for address_index in disassmbly_address_list :
            opcode = self.disassmbly_data[address_index]

            print hex(address_index),':',opcode.get_opcode(),opcode.get_opcode_data()
    
    def get_all_code(self) :
        temp = ''
        disassmbly_address_list = self.get_disassmbly_address_list()

        for address_index in disassmbly_address_list :
            opcode = self.disassmbly_data[address_index]

            temp += hex(address_index) + ':' + str(opcode.get_opcode()) + str(opcode.get_opcode_data()) + '\n'
        return temp

class memory :

    MEMORY_ALIGNMENT = 32

    def __init__(self,init_size = 0x80) :
        self.memory_data = {}

    def set_real_data(self,address,data,length) :
        pass

    def set(self,address,data,length) :
        if type(data) == int :
            number_data = hex(data)[ 2 : ]
            data = []

            for fill_zero_index in range(32) :
                data.append(0)

            while len(number_data) :
                if len(number_data) == 1 :
                    data[fill_zero_index] = int(number_data[ -1 ],16)
                    number_data = []
                else :
                    data[fill_zero_index] = int(number_data[ -2 : ],16)
                    number_data = number_data[ : -2 ]

                fill_zero_index -= 1

        memory_address_map = self.memory_data.keys()
        left_pollute_memory_address = -1
        right_pollute_memory_address = -1

        for memory_address_index in memory_address_map :
            if memory_address_index <= address and address < (memory_address_index + length) :
                left_pollute_memory_address = memory_address_index
            elif memory_address_index <= (address + length - 1) and \
                 (address + length - 1) < (memory_address_index + length) :
                right_pollute_memory_address = memory_address_index

        if not left_pollute_memory_address == -1 :
            self.memory_data[left_pollute_memory_address] = \
                opcode_express.opcode_shr(self.memory_data[left_pollute_memory_address],
                                          address - left_pollute_memory_address)

        if not right_pollute_memory_address == -1 :
            end_distance = address + length - right_pollute_memory_address
            self.memory_data[right_pollute_memory_address + end_distance] = \
                opcode_express.opcode_and(self.memory_data[right_pollute_memory_address],
                                          length - end_distance)
            self.memory_data.__delitem__(right_pollute_memory_address)

        self.memory_data[address] = data

    def set_32byte(self,address,data) :
        self.set(address,data,memory.MEMORY_ALIGNMENT)

    def get(self,address,length) :
        left_access_memory_address = -1
        right_access_memory_address = -1
        memory_address_map = self.memory_data.keys()

        if address in self.memory_data.keys() :
            if type(self.memory_data[address]) == list :
                data = '0x'

                for index in self.memory_data[address] :
                    data += hex(index)[ 2 : ]

                return data

            return self.memory_data[address]

        for memory_address_index in memory_address_map :
            if memory_address_index <= address and address < (memory_address_index + length) :
                left_access_memory_address = memory_address_index
            elif memory_address_index <= (address + length - 1) and \
                 (address + length - 1) < (memory_address_index + length) :
                right_access_memory_address = memory_address_index

        data = 0

        if not left_access_memory_address == -1 :
            left_access_memory_length = left_access_memory_address + length - address
            data = opcode_express.opcode_shl(opcode_express.opcode_and(
                                                self.memory_data[left_access_memory_address],
                                                0x100 ** left_access_memory_length - 1),
                                             left_access_memory_length)

        if not right_access_memory_address == -1 :
            right_access_memory_length = address + length - right_access_memory_address
            data = opcode_express.opcode_add(data,opcode_express.opcode_shl(
                                                self.memory_data[right_access_memory_length],
                                                right_access_memory_length))

        return data

    def get_32byte(self,address) :
        return self.get(address,memory.MEMORY_ALIGNMENT)

    def get_64byte(self,address) :
        return self.get(address,memory.MEMORY_ALIGNMENT * 2)

    def print_memory(self) :
        print '>--- print_memory() ---<'
        print self.memory_data
        print '<--- print_memory() --->'

class stack :

    def __init__(self,init_size = 0x80):
        self.memory_data = {}
        self.point = -1

    def push_data(self,data) :
        self.point += 1
        self.memory_data[self.point] = data

    def pop_data(self) :
        old_stack_data = self.memory_data[self.point]
        self.memory_data[self.point] = -1
        self.point -= 1

        return old_stack_data

    def dup_data(self,dup_number) :
        if dup_number > self.point :
            return

        copy_data = self.memory_data[self.point - dup_number]

        self.push_data(copy_data)

    def swap_data(self,swap_number) :
        if swap_number > self.point :
            return

        old_data = self.memory_data[self.point]
        self.memory_data[self.point] = self.memory_data[self.point - swap_number]
        self.memory_data[self.point - swap_number] = old_data

    def print_stack(self) :
        print '>--- print_stack(%X) ---<' % id(self.memory_data)
        print self.memory_data
        print self.point
        print '<--- print_stack(%X) --->' % id(self.memory_data)

class store :

    MEMORY_ALIGNMENT = 64

    def __init__(self):
        self.store_data = {}
        self.store_init = {}

    def set_init_data(self,init_data) :
        self.store_data = init_data
        self.store_init = init_data

    def set(self,address,data) :
        self.store_data[address] = data

    def get(self,address) :
        if address in self.store_data.keys() :
            return self.store_data[address]

        return 0

    def get_init_data(self) :
        return self.store_init

    def print_store(self) :
        print '>--- print_store ---<'
        print self.store_data
        print '<--- print_store --->'

    def print_store_make_express(self) :
        print '>--- print_store ---<'

        for address,data in self.store_data.items() :
            if 'make_express' in dir(address) :
                address = address.make_express()

            if 'make_express' in dir(data) :
                data = data.make_express()

            print 'Addr %s => %s' % (address,data)

        print '<--- print_store --->'

    def get_all_store_express(self) :
        result = []

        for address,data in self.store_data.items() :
            if 'make_express' in dir(address) :
                address = address.make_express()

            if 'make_express' in dir(data) :
                data = data.make_express()

            result.append((address,data))

        return result

class state_object :

    class execute_state_value :

        UNRUNNING = 0
        RUNNING = 1
        ACTIVE_PATH = 2  #  is a valid path
        DEAD_PATH = 3    #  is a unvalid path

    def __init__(self) :
        self.memory = memory()
        self.stack = stack()
        self.store = store()
        self.code_record = []
        self.express_list = []
        self.execute_state = state_object.execute_state_value.UNRUNNING

    def set_execute_state(self,value) :
        self.execute_state = value

    def get_execute_state(self,) :
        return self.execute_state

    def clean_stack_and_memory(self) :
        self.memory = memory()
        self.stack = stack()

    def add_execute_code(self,opcode_object) :
        self.code_record.append((opcode_object,copy.deepcopy(self.stack.memory_data)))

    def add_express(self,express_object) :
        self.express_list.append(express_object)

    def show_code_stream(self,is_output_stack = False) :
        print '<<<< state_object::show_code_stream() <<<<'

        for code_index,stack_record in self.code_record :
            if is_output_stack :
                print 'Stack :' , stack_record

            print hex(code_index.get_address()),code_index.get_opcode(),code_index.get_opcode_data()

        print '>>>> state_object::show_code_stream() >>>>'

    def show_express(self) :
        print '<<<< state_object::show_express() <<<<'

        import z3

        z3_init_list = opcode_express.make_z3_init()

        for init_index in z3_init_list :
            exec(init_index)

        solver = z3.Solver()

        for express_index in self.express_list :
            express_data = express_index.make_express()

            exec('solver.add(%s)' % (express_data))

            print express_data

        if z3.sat == solver.check() :
            print 'Sat : '

            model_data = solver.model()

            for key_index in model_data :
                print '>>',key_index,hex(int(str(model_data[key_index])))
        else :
            print 'No Sat ...'

        print '>>>> state_object::show_express() >>>>'

class execute_context :

    def __init__(self) :
        self.instrutment_count = 0
        self.branch_count = 0

    def get_branch_count(self) :
        return self.branch_count

    def get_instrutment_count(self) :
        return self.instrutment_count

    def add_branch_count(self) :
        self.branch_count += 1

    def add_instrutment_count(self) :
        self.instrutment_count += 1

