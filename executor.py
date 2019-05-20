

import copy

import context
import opcode_express


class execute_revert :

    def __init__(self) :
        pass

class execute_stop :

    def __init__(self) :
        pass

class execute_return :

    def __init__(self) :
        pass

class execute_selfdestruct :

    def __init__(self) :
        pass

class execute_death_path :

    def __init__(self) :
        pass

def execute_value_express(opcode_express_object) :
    import z3

    temp = z3.BitVec('temp',64 * 8)
    solver = z3.Solver()

    z3_opcode_express = opcode_express_object.make_express()
    
    exec('solver.add(temp == %s)' % (z3_opcode_express))

    if z3.sat == solver.check() :
        temp = str(solver.model())
        temp = temp[ temp.find('=') + 1 : -1 ].strip()

        return temp

    return False

def execute_real_express(opcode_express_object) :
    condition_temp_value = False
    condition_express = opcode_express_object.make_express()
    condition_express = opcode_express.replace_express_to_logic_express(condition_express)

    def div(number1,number2) :
            return number1 / number2

    def isZero(number1) :
        return number1 - 1

    exec('condition_temp_value = (%s)' % condition_express)

    return condition_temp_value

def build_express_list(express_list) :
    import z3

    z3_init_list = opcode_express.make_z3_init()

    for init_index in z3_init_list :
        exec(init_index)

    solver = z3.Solver()

    for express_index in express_list :
        express_data = express_index.make_express()

        exec('solver.add(%s)' % (express_index))

    return solver


class executor :

    def __init__(self,code_object,state_object,execute_context) :
        self.code_object = code_object
        self.state_object = state_object
        self.execute_context = execute_context

    def copy_executor(self) :
        new_executor = executor(copy.deepcopy(self.code_object),
                                copy.deepcopy(self.state_object),
                                self.execute_context)

        return new_executor

    def get_state_object(self) :
        return self.state_object

    def fork_branch(self,condition) :
        import z3

        z3_init_list = opcode_express.make_z3_init()

        for init_index in z3_init_list :
            exec(init_index)

        solver_true  = z3.Solver()
        solver_false = z3.Solver()

        for express_index in self.state_object.express_list :
            express_data = express_index.make_express()

            #print 'solver.add(%s)' % (express_data)

            exec('solver_true.add(%s)' % (express_data))
            exec('solver_false.add(%s)' % (express_data))

        condition_express = condition.make_express()
        not_condition_express = opcode_express.opcode_logic_not(condition).make_express()

        if not opcode_express.is_take_input(condition) :  #  this express don't using z3 to resolver it .
                                                          #  see example : z3.Not((z3.Not((0x03 < (0x01 + 0x02)))))
            condition_value = execute_real_express(condition)

            if condition_value :
                true_condition_check_success = True
                false_condition_check_success = False
            else :
                true_condition_check_success = False
                false_condition_check_success = True            
        else :
            exec('solver_true.add(%s)' % (condition_express))
            exec('solver_false.add(%s)' % (not_condition_express))

            if z3.sat == solver_true.check() :
                true_condition_check_success = True
            else :
                true_condition_check_success = False

            if z3.sat == solver_false.check() :
                false_condition_check_success = True
            else :
                false_condition_check_success = False

        #print solver_true.model(),solver_false.model()

        return true_condition_check_success,false_condition_check_success

    def execute_opcode(self,opcode_object) :
        opcode_name = opcode_object.get_opcode()
        next_pc = -1

        self.state_object.add_execute_code(opcode_object)
        self.execute_context.add_instrutment_count()

        if opcode_name.startswith('PUSH') :
            self.state_object.stack.push_data(opcode_object.get_opcode_data(0))

            push_size = int(opcode_name[ 4 : ])
            next_pc = opcode_object.get_address() + push_size + 1
        elif opcode_name.startswith('DUP') :
            dup_offset = int(opcode_name[ 3 : ]) - 1

            self.state_object.stack.dup_data(dup_offset)

            next_pc = opcode_object.get_address() + 1
        elif opcode_name.startswith('SWAP') :
            swap_offset = int(opcode_name[ 4 : ])

            self.state_object.stack.swap_data(swap_offset)

            next_pc = opcode_object.get_address() + 1
        elif 'POP' == opcode_name :
            self.state_object.stack.pop_data()

            next_pc = opcode_object.get_address() + 1
        elif 'MSTORE' == opcode_name :
            mstore_target_address = self.state_object.stack.pop_data()
            mstore_target_data = self.state_object.stack.pop_data()

            if not type(mstore_target_address) == str :
                mstore_target_address = execute_value_express(mstore_target_address)

            try :
                mstore_target_address = int(mstore_target_address)
            except :
                mstore_target_address = int(mstore_target_address,16)

            if type(mstore_target_data) == str :
                try :
                    mstore_target_data = int(mstore_target_data)
                except :
                    mstore_target_data = int(mstore_target_data,16)

            self.state_object.memory.set_32byte(mstore_target_address,mstore_target_data)

            next_pc = opcode_object.get_address() + 1
        elif 'MLOAD' == opcode_name :
            mstore_target_address = self.state_object.stack.pop_data()

            try :
                mstore_target_address = int(mstore_target_address)
            except :
                mstore_target_address = int(mstore_target_address,16)

            self.state_object.stack.push_data(
                self.state_object.memory.get_32byte(mstore_target_address))

            next_pc = opcode_object.get_address() + 1
        elif 'SSTORE' == opcode_name :
            sstore_target_address = self.state_object.stack.pop_data()
            sstore_target_data = self.state_object.stack.pop_data()

            self.state_object.store.set(sstore_target_address,sstore_target_data)

            if opcode_express.is_input(sstore_target_address) or opcode_express.is_take_input(sstore_target_address) :
                vuln_checker.transfer_overflow_check(self.state_object,sstore_target_address,sstore_target_data)

            next_pc = opcode_object.get_address() + 1
        elif 'SLOAD' == opcode_name :
            sstore_target_address = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(self.state_object.store.get(sstore_target_address))

            next_pc = opcode_object.get_address() + 1
        elif 'CALLER' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_call_caller())

            next_pc = opcode_object.get_address() + 1
        elif 'CALLVALUE' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_call_value())

            next_pc = opcode_object.get_address() + 1
        elif 'CALLDATASIZE' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_call_size())

            next_pc = opcode_object.get_address() + 1
        elif 'CALLDATALOAD' == opcode_name :
            calldata_offset = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_call_data(calldata_offset))

            next_pc = opcode_object.get_address() + 1
        elif 'CODESIZE' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_code_size())

            next_pc = opcode_object.get_address() + 1
        elif 'EXTCODESIZE' == opcode_name :
            address = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_extcode_size())

            next_pc = opcode_object.get_address() + 1
        elif 'GAS' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_gas())

            next_pc = opcode_object.get_address() + 1
        elif 'GASPRICE' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_gasprice())

            next_pc = opcode_object.get_address() + 1
        elif 'GASLIMIT' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_gaslimit())

            next_pc = opcode_object.get_address() + 1
        elif 'NUMBER' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_blocknumber())

            next_pc = opcode_object.get_address() + 1
        elif 'DIFFICULTY' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_difficulty())

            next_pc = opcode_object.get_address() + 1
        elif 'ORIGIN' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_origin())

            next_pc = opcode_object.get_address() + 1
        elif 'COINBASE' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_coinbase())

            next_pc = opcode_object.get_address() + 1
        elif 'ADDRESS' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_address())

            next_pc = opcode_object.get_address() + 1
        elif 'LT' == opcode_name :
            lt_right_data = self.state_object.stack.pop_data()
            lt_left_data = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_lt(lt_left_data,lt_right_data))

            next_pc = opcode_object.get_address() + 1
        elif 'GT' == opcode_name :
            gt_right_data = self.state_object.stack.pop_data()
            gt_left_data = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_gt(gt_left_data,gt_right_data))

            next_pc = opcode_object.get_address() + 1
        elif 'EQ' == opcode_name :
            eq_right_data = self.state_object.stack.pop_data()
            eq_left_data = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_eq(eq_left_data,eq_right_data))

            next_pc = opcode_object.get_address() + 1
        elif 'ISZERO' == opcode_name :
            check_data = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_iszero(check_data))

            next_pc = opcode_object.get_address() + 1
        elif 'JUMPI' == opcode_name :
            jump_next_pc_address = self.state_object.stack.pop_data()
            check_condition = self.state_object.stack.pop_data()
            nojump_next_pc_address = opcode_object.get_address() + 1

            try :
                jump_next_pc_address = int(jump_next_pc_address)
            except :
                jump_next_pc_address = int(jump_next_pc_address,16)

            if not 'JUMPDEST' == self.code_object.get_disassmbly_by_address(jump_next_pc_address).get_opcode() :
                print 'JUMP Target Opcode Except ..'

                exit()

            self.execute_context.add_branch_count()

            true_condition,false_condition = self.fork_branch(check_condition)

            if False == true_condition == false_condition :
                #self.state_object.add_express(check_condition)
                #self.state_object.show_code_stream()
                #self.state_object.show_express()
                
                return execute_death_path()

            #print check_condition.make_express()
            #print true_condition,false_condition,check_condition.make_express()

            if not opcode_express.is_take_input(check_condition) :  #  check is real true/false condition ..
                if true_condition :
                    true_branch_executor = self.copy_executor()

                    true_branch_executor.run(jump_next_pc_address)
                elif false_condition :
                    false_branch_executor = self.copy_executor()

                    false_branch_executor.run(nojump_next_pc_address)
            else :
                if true_condition :
                    true_branch_executor = self.copy_executor()

                    true_branch_executor.state_object.add_express(check_condition)
                    true_branch_executor.run(jump_next_pc_address)

                if false_condition :
                    false_branch_executor = self.copy_executor()

                    false_branch_executor.state_object.add_express(opcode_express.opcode_logic_not(check_condition))
                    false_branch_executor.run(nojump_next_pc_address)

            return -1
        elif 'JUMP' == opcode_name :
            jump_next_pc_address = self.state_object.stack.pop_data()

            try :
                jump_next_pc_address = int(jump_next_pc_address)
            except :
                jump_next_pc_address = int(jump_next_pc_address,16)

            if not 'JUMPDEST' == self.code_object.get_disassmbly_by_address(jump_next_pc_address).get_opcode() :
                print 'JUMP Target Opcode Except ..'

                exit()

            next_pc = jump_next_pc_address
        elif 'CALL' == opcode_name or 'CALLCODE' == opcode_name or 'DELEGATECALL' == opcode_name or 'STATICCALL' == opcode_name :
            call_gas     = self.state_object.stack.pop_data()
            call_address = self.state_object.stack.pop_data()
            call_value   = self.state_object.stack.pop_data()
            call_inaddr  = self.state_object.stack.pop_data()
            call_insize  = self.state_object.stack.pop_data()
            call_outaddr = self.state_object.stack.pop_data()
            call_outsize = self.state_object.stack.pop_data()

            vuln_checker.arbitrarily_call(self.state_object,call_address)

            next_pc = opcode_object.get_address() + 1
        elif 'JUMPDEST' == opcode_name :
            next_pc = opcode_object.get_address() + 1
        elif 'ADD' == opcode_name :
            number1 = self.state_object.stack.pop_data()
            number2 = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_add(number1,number2))

            next_pc = opcode_object.get_address() + 1
        elif 'SUB' == opcode_name :
            number1 = self.state_object.stack.pop_data()
            number2 = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_sub(number1,number2))

            next_pc = opcode_object.get_address() + 1
        elif 'MUL' == opcode_name :
            number1 = self.state_object.stack.pop_data()
            number2 = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_mul(number1,number2))

            next_pc = opcode_object.get_address() + 1
        elif 'DIV' == opcode_name :
            number1 = self.state_object.stack.pop_data()
            number2 = self.state_object.stack.pop_data()

            vuln_checker.div_zero_check(self.state_object,number2)

            self.state_object.stack.push_data(opcode_express.opcode_div(number1,number2))

            next_pc = opcode_object.get_address() + 1
        elif 'EXP' == opcode_name :
            number1 = self.state_object.stack.pop_data()
            number2 = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_exp(number1,number2))

            next_pc = opcode_object.get_address() + 1
        elif 'MOD' == opcode_name :
            number1 = self.state_object.stack.pop_data()
            number2 = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_mod(number1,number2))

            next_pc = opcode_object.get_address() + 1
        elif 'AND' == opcode_name :
            number1 = self.state_object.stack.pop_data()
            number2 = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_and(number1,number2))

            next_pc = opcode_object.get_address() + 1
        elif 'OR' == opcode_name :
            number1 = self.state_object.stack.pop_data()
            number2 = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_or(number1,number2))

            next_pc = opcode_object.get_address() + 1
        elif 'XOR' == opcode_name :
            number1 = self.state_object.stack.pop_data()
            number2 = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_xor(number1,number2))

            next_pc = opcode_object.get_address() + 1
        elif 'NOT' == opcode_name :
            number1 = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_arithmetic_not(number1))

            next_pc = opcode_object.get_address() + 1
        elif 'SHL' == opcode_name :
            number1 = self.state_object.stack.pop_data()
            number2 = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_shl(number1,number2))

            next_pc = opcode_object.get_address() + 1
        elif 'SHR' == opcode_name :
            number1 = self.state_object.stack.pop_data()
            number2 = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_shr(number1,number2))

            next_pc = opcode_object.get_address() + 1
        elif 'RETURNDATASIZE' == opcode_name :
            self.state_object.stack.push_data(opcode_express.opcode_returndatasize)

            next_pc = opcode_object.get_address() + 1
        elif 'RETURNDATACOPY' == opcode_name :
            copy_to_addr   = self.state_object.stack.pop_data()
            copy_from_addr = self.state_object.stack.pop_data()
            copy_length    = self.state_object.stack.pop_data()

            try :
                copy_to_addr = int(copy_to_addr)
            except :
                copy_to_addr = int(copy_to_addr,16)

            try :
                copy_from_addr = int(copy_from_addr)
            except :
                copy_from_addr = int(copy_from_addr,16)

            self.state_object.memory.set_32byte(copy_to_addr,self.state_object.memory.get_32byte(copy_from_addr))

            next_pc = opcode_object.get_address() + 1
        elif 'CODESIZE' == opcode_name :
            self.state_object.stack.push_data(self.code_object.get_disassmbly_data_length())

            next_pc = opcode_object.get_address() + 1
        elif 'CODECOPY' == opcode_name :
            target_memory = self.state_object.stack.pop_data()
            code_offset = self.state_object.stack.pop_data()
            code_length = self.state_object.stack.pop_data()

            try :
                target_memory = int(target_memory)
            except :
                target_memory = int(target_memory,16)

            try :
                code_offset = int(code_offset)
            except :
                code_offset = int(code_offset,16)

            try :
                code_length = int(code_length)
            except :
                code_length = int(code_length,16)

            code_data = self.code_object.get_bytecode_data(code_offset,code_length)

            self.state_object.memory.set_real_data(target_memory,code_data,code_length)

            next_pc = opcode_object.get_address() + 1
        elif 'CALLDATACOPY' == opcode_name :
            target_memory = self.state_object.stack.pop_data()
            call_offset = self.state_object.stack.pop_data()
            call_length = self.state_object.stack.pop_data()
            
            if 'make_express' in dir(target_memory) :
                if not opcode_express.is_take_input(target_memory) :
                    target_memory = execute_value_express(target_memory)

            try :
                target_memory = int(target_memory)
            except :
                target_memory = int(target_memory,16)

            self.state_object.memory.set_32byte(target_memory,opcode_express.opcode_call_data(call_offset))

            next_pc = opcode_object.get_address() + 1
        elif 'KECCAK256' == opcode_name or 'SHA3' == opcode_name :
            data_point = self.state_object.stack.pop_data()
            data_length = self.state_object.stack.pop_data()

            try :
                data_point = int(data_point)
            except :
                data_point = int(data_point,16)

            memory_object = self.state_object.memory.get_64byte(data_point)

            self.state_object.stack.push_data(opcode_express.opcode_sha3(memory_object))

            next_pc = opcode_object.get_address() + 1
        elif 'SELFDESTRUCT' == opcode_name :
            target_address = self.state_object.stack.pop_data()

            vuln_checker.arbitrarily_selfdestruct(self.state_object,target_address)

            return execute_selfdestruct()
        elif 'REVERT' == opcode_name :
            #self.state_object.show_code_stream()
            #self.state_object.show_express()
            #self.state_object.store.print_store_make_express()

            return execute_revert()
        elif 'RETURN' == opcode_name or 'INVALID' == opcode_name :
            #self.state_object.show_code_stream()
            #self.state_object.show_express()
            #self.state_object.store.print_store_make_express()
            
            return execute_return()
        elif 'STOP' == opcode_name :
            #self.state_object.show_code_stream()
            #self.state_object.show_express()
            #self.state_object.store.print_store_make_express()
            
            return execute_stop()
        elif opcode_name.startswith('LOG') :
            memory_start = self.state_object.stack.pop_data()
            memory_size = self.state_object.stack.pop_data()
            log_count = int(opcode_name[ 3 : ])
            for i in range(log_count) :
                self.state_object.stack.pop_data()

            next_pc = opcode_object.get_address() + 1
        else :
            print 'Unknow Opcode ..'
            print hex(opcode_object.get_address()),opcode_name,opcode_object.get_opcode_data()

            exit()

        #print hex(opcode_object.get_address()),opcode_name,opcode_object.get_opcode_data()

        #self.state_object.stack.print_stack()

        return next_pc

    def run(self,pc = 0) :
        opcode_address_list = self.code_object.get_disassmbly_address_list()

        while pc in opcode_address_list :
            current_opcode = self.code_object.get_disassmbly_by_address(pc)
            pc = self.execute_opcode(current_opcode)

            if not type(pc) == int :
                if pc.__class__ == execute_revert :
                    pass
                elif pc.__class__ == execute_revert :
                    pass

    def get_execute_branch_count(self) :
        return self.execute_context.get_branch_count()

    def get_execute_instrutment_count(self) :
        return self.execute_context.get_instrutment_count()


class vuln_checker :

    @staticmethod
    def transfer_overflow_check(state_object,address_object,check_object) :
        check_result = False

        if  not opcode_express.is_take_input(address_object) and \
            not opcode_express.is_input(address_object) :
            return False

        import z3

        z3_init_list = opcode_express.make_z3_init()

        for init_index in z3_init_list :
            exec(init_index)

        solver = z3.Solver()

        for express_index in state_object.express_list :
            express_data = express_index.make_express()

            exec('solver.add(%s)' % (express_data))

        if not opcode_express.is_take_input(check_object) and not opcode_express.is_input(check_object):
            condition_value = execute_real_express(check_object)
        else :
            address_express = address_object.make_express()
            check_express = check_object.make_express()

            exec('solver.add((%s) == %s)' % (address_express,opcode_express.DEFAULT_INPUT_ADDRESS))
            exec('solver.add(%s < 0)' % (check_express))

            if z3.sat == solver.check() :
                print '\033[1;31m---- Transfer Overflow Vuln Check ! ----\033[0m'
                print 'Auto Building Test Payload :'

                check_result = True
                model_data = solver.model()

                for key_index in model_data :
                    print '\033[1;34m>>',key_index,hex(int(str(model_data[key_index]))),'\033[0m'

        return check_result

    @staticmethod
    def arbitrarily_selfdestruct(state_object,address_object) :
        check_result = False

        if  not opcode_express.is_take_input(address_object) and \
            not opcode_express.is_input(address_object) :
            return False

        import z3

        z3_init_list = opcode_express.make_z3_init()

        for init_index in z3_init_list :
            exec(init_index)

        solver = z3.Solver()

        for express_index in state_object.express_list :
            express_data = express_index.make_express()

            exec('solver.add(%s)' % (express_data))

        check_express = address_object.make_express()

        exec('solver.add((%s) == %s)' % (check_express,opcode_express.DEFAULT_INPUT_ADDRESS))

        if z3.sat == solver.check() :
            print '\033[1;31m---- Arbitrarily Self-Destruct Vuln Check ! ----\033[0m'
            print 'Auto Building Test Payload :'

            check_result = True
            model_data = solver.model()

            for key_index in model_data :
                print '\033[1;34m>>',key_index,hex(int(str(model_data[key_index]))),'\033[0m'

        return check_result

    @staticmethod
    def arbitrarily_call(state_object,address_object) :
        check_result = False

        if  not opcode_express.is_take_input(address_object) and \
            not opcode_express.is_input(address_object) :
            return False

        import z3

        z3_init_list = opcode_express.make_z3_init()

        for init_index in z3_init_list :
            exec(init_index)

        solver = z3.Solver()

        for express_index in state_object.express_list :
            express_data = express_index.make_express()

            exec('solver.add(%s)' % (express_data))

        check_express = address_object.make_express()

        exec('solver.add((%s) == %s)' % (check_express,opcode_express.DEFAULT_INPUT_CONTRACT_ADDRESS))

        if z3.sat == solver.check() :
            print '\033[1;31m---- Arbitrarily CALL Vuln Check ! ----\033[0m'
            print 'Auto Building Test Payload :'

            check_result = True
            model_data = solver.model()

            for key_index in model_data :
                print '\033[1;34m>>',key_index,hex(int(str(model_data[key_index]))),'\033[0m'

        return check_result

    @staticmethod
    def div_zero_check(state_object,number_object) :
        check_result = False

        if  not opcode_express.is_take_input(number_object) and \
            not opcode_express.is_input(number_object) :
            if opcode_express.is_opcode_object(number_object) :
                if 0 == execute_value_express(number_object) :
                    check_result = True
            else :
                try :
                    number_object = int(number_object)
                except :
                    number_object = int(number_object,16)

                if 0 == number_object :
                    check_result = True

            return check_result

        import z3

        z3_init_list = opcode_express.make_z3_init()

        for init_index in z3_init_list :
            exec(init_index)

        solver = z3.Solver()

        for express_index in state_object.express_list :
            express_data = express_index.make_express()

            exec('solver.add(%s)' % (express_data))

        check_express = number_object.make_express()

        exec('solver.add((%s) == 0)' % (check_express))

        if z3.sat == solver.check() :
            print '\033[1;31m---- Div Zero Bug Check ! ----\033[0m'
            print 'Auto Building Test Payload :'

            check_result = True
            model_data = solver.model()

            for key_index in model_data :
                print '\033[1;34m>>',key_index,hex(int(str(model_data[key_index]))),'\033[0m'

        return check_result


