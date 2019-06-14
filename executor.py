

import copy
import z3

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
    # import z3

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
        if number1 == 0 :
            return 1
        return 0

    exec('condition_temp_value = (%s)' % condition_express)

    return condition_temp_value

def format_to_hex(express) :
    if opcode_express.is_z3_express(express) :
        return False

    if not express.__class__ == z3.z3.BitVecNumRef :
        try :
            express = int(express)
        except :
            express = int(express,16)
    else :
        express = express.as_long()
    
    express = hex(express)

    if express[-1:] == 'L' :
        express = express[:-1]
    
    return express

def format_to_bitVal(data, len = 256) :
    if type(data) == str or type(data) == bool or type(data) == unicode :
        try :
            data = int(data)
        except :
            data = int(data,16)
    
    if data.__class__ == z3.z3.BitVecNumRef :
        return data

    data = z3.BitVecVal(data, 256)
    return data

def format_to_bool(data) :

    return z3.If(data == 0, False, True)


def build_express_list(express_list) :
    # import z3

    z3_init_list = opcode_express.make_z3_init()

    for init_index in z3_init_list :
        exec(init_index)

    solver = z3.Solver()

    for express_index in express_list :
        express_data = express_index.make_express()

        exec('solver.add(%s)' % (express_index))

    return solver


class executor :

    def __init__(self,code_object,state_object,execute_context,contract_address = False,input_data = False,jump_count = False,init_data = False,vuln_data = False,explore_function = False) :
        self.code_object = code_object
        self.state_object = state_object
        self.execute_context = execute_context
        self.input_data = {}
        self.execute_path = []
        self.all_path_record = []
        self.explore_function = explore_function

        if vuln_data :
            self.vuln_data = vuln_data
        self.vuln_data = ''
        
        if type(jump_count) == dict :
            self.jump_count = jump_count
        else :
            self.jump_count = {}

        if type(input_data) == dict :
            self.input_data = input_data
        else :
            self.input_data['callsize']       = z3.BitVec('callsize',opcode_express.opcode_call_size.LENGTH * 8)
            self.input_data['calldata']       = z3.Array('calldata',z3.BitVecSort(opcode_express.opcode_call_data_config.LENGTH),z3.BitVecSort(8))
            self.input_data['callvalue']      = z3.BitVec('callvalue',opcode_express.opcode_call_value.LENGTH * 8)
            self.input_data['caller']         = z3.BitVec('caller',opcode_express.opcode_call_caller.LENGTH * 8)
            self.input_data['codesize']       = z3.BitVec('codesize',opcode_express.opcode_code_size.LENGTH * 8)
            self.input_data['extcodesize']    = z3.BitVec('extcodesize',opcode_express.opcode_extcode_size.LENGTH * 8)
            self.input_data['gas']            = z3.BitVec('gas',opcode_express.opcode_gas.LENGTH * 8)
            self.input_data['gasprice']       = z3.BitVec('gasprice',opcode_express.opcode_gasprice.LENGTH * 8)
            self.input_data['gaslimit']       = z3.BitVec('gaslimit',opcode_express.opcode_gaslimit.LENGTH * 8)
            self.input_data['difficulty']     = z3.BitVec('difficulty',opcode_express.opcode_difficulty.LENGTH * 8)
            self.input_data['blocknumber']    = z3.BitVec('blocknumber',opcode_express.opcode_blocknumber.LENGTH * 8)
            self.input_data['origin']         = z3.BitVec('origin',opcode_express.opcode_origin.LENGTH * 8)
            self.input_data['coinbase']       = z3.BitVec('coinbase',opcode_express.opcode_coinbase.LENGTH * 8)
            self.input_data['address']        = z3.BitVec('address',opcode_express.opcode_address.LENGTH * 8)
            self.input_data['returndatasize'] = z3.BitVec('returndatasize',opcode_express.opcode_returndatasize.LENGTH * 8)
            self.input_data['memory']         = z3.Array('memory',z3.BitVecSort(opcode_express.opcode_memory.LENGTH),z3.BitVecSort(8))
            self.input_data['memory']         = opcode_express.opcode_init_memory(self.input_data['memory'], opcode_express.opcode_memory.LENGTH)
            if init_data and init_data.has_key('calldata') :
                self.input_data['calldata'] = opcode_express.opcode_init_call_data(self.input_data['calldata'], init_data['calldata'])
        
        if type(contract_address) == str :
            self.contract_address = contract_address.lower()
        else :
            self.contract_address = opcode_express.opcode_address()

    def copy_executor(self) :
        new_executor = executor(copy.deepcopy(self.code_object),
                                copy.deepcopy(self.state_object),
                                self.execute_context,
                                self.contract_address,
                                copy.deepcopy(self.input_data),
                                copy.deepcopy(self.jump_count),
                                False,
                                self.vuln_data,
                                self.explore_function)

        return new_executor

    def check_infinite_loop(self,jump_src,jump_dst) :
        tag = '%s to %s' % (format_to_hex(jump_src), format_to_hex(jump_dst))
        
        if self.jump_count.has_key(tag) :
            self.jump_count[tag] += 1
        else :
            self.jump_count[tag] = 1
        
        #print 'jump count %s %s' % (tag,self.jump_count[tag])
        
        if self.jump_count[tag] < 10 :
            return False

        print 'find out infinite_loop at %s' % tag
        return True
   
    def get_state_object(self) :
        return self.state_object

    def fork_branch(self,condition) :
        import z3

        # z3_init_list = opcode_express.make_z3_init()

        # for init_index in z3_init_list :
        #     exec(init_index)

        solver_true  = z3.Solver()
        solver_false = z3.Solver()

        for express_data in self.state_object.express_list :
            # express_data = express_index.make_express()
            
            # print 'solver.add(%s)' % (express_data)
            solver_true.add(format_to_bool(express_data))
            solver_false.add(format_to_bool(express_data))
            # exec('solver_true.add(%s)' % (express_data))
            # exec('solver_false.add(%s)' % (express_data))

        condition_express = condition
        not_condition_express = opcode_express.opcode_logic_not(condition)

        if not opcode_express.is_z3_express(condition) :  #  this express don't using z3 to resolver it .
                                                          #  see example : z3.Not((z3.Not((0x03 < (0x01 + 0x02)))))
            # condition_value = execute_real_express(condition)
            condition = z3.simplify(format_to_bool(condition))
            #print condition
            if condition :
                true_condition_check_success = True
                false_condition_check_success = False
            else :
                true_condition_check_success = False
                false_condition_check_success = True            
        else :
            # print 'solver.add(%s)' % (condition_express)
            solver_true.add(format_to_bool(condition_express))
            solver_false.add(format_to_bool(not_condition_express))
            # exec('solver_true.add(%s)' % (condition_express))
            # exec('solver_false.add(%s)' % (not_condition_express))

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

    def check_is_transfer_function_entry_point(self,check_condition) :
        check_condition = str(check_condition)

        if  'Concat' in check_condition and \
            'calldata' in check_condition and \
            '2835717307' in check_condition :
            return True

        return False

    def execute_opcode(self,opcode_object,is_valid_vuln = True,debug_output = False) :
        opcode_name = opcode_object.get_opcode()
        next_pc = -1

        self.state_object.add_execute_code(opcode_object)
        self.execute_context.add_instrutment_count()

        if debug_output :
            print hex(opcode_object.get_address()),opcode_name,opcode_object.get_opcode_data()

        if opcode_name.startswith('PUSH') :
            data = opcode_object.get_opcode_data(0)
            
            self.state_object.stack.push_data(format_to_bitVal(data))

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
            # if not type(mstore_target_address) == str :
            #     print 'MSTORE',mstore_target_address.make_express()
            #     mstore_target_address = execute_value_express(mstore_target_address)
            
            # try :
            #     mstore_target_address = int(mstore_target_address)
            # except :
            #     mstore_target_address = int(mstore_target_address,16)

            # if type(mstore_target_data) == str :
            #     try :
            #         mstore_target_data = int(mstore_target_data)
            #     except :
            #         mstore_target_data = int(mstore_target_data,16)

            self.input_data['memory'] = opcode_express.opcode_write_memory(self.input_data['memory'],mstore_target_address,mstore_target_data)
            #print memory_express.make_express()
            # write_express = opcode_express.opcode_eq(memory_express,mstore_target_data)
            #print write_express.make_express()

            # self.state_object.add_express(write_express)

            # self.state_object.memory.set_32byte(mstore_target_address,mstore_target_data)

            next_pc = opcode_object.get_address() + 1
        elif 'MLOAD' == opcode_name :
            mstore_target_address = self.state_object.stack.pop_data()

            # if not type(mstore_target_address) == str :
            #     mstore_target_address = execute_value_express(mstore_target_address)

            # try :
            #     mstore_target_address = int(mstore_target_address)
            # except :
            #     mstore_target_address = int(mstore_target_address,16)
            
            # print 'mstore_target_address',mstore_target_address
            # #print self.state_object.memory.get_32byte(mstore_target_address).make_express()

            # self.state_object.stack.push_data(
            #     self.state_object.memory.get_32byte(mstore_target_address))
            express = opcode_express.opcode_get_memory(self.input_data['memory'],mstore_target_address)
            self.state_object.stack.push_data(express)

            next_pc = opcode_object.get_address() + 1
        elif 'SSTORE' == opcode_name :
            sstore_target_address = self.state_object.stack.pop_data()
            sstore_target_data = self.state_object.stack.pop_data()

            # print sstore_target_address.__class__

            if not opcode_express.is_z3_express(sstore_target_address) :
                sstore_target_address = format_to_hex(sstore_target_address)

            self.state_object.store.set(sstore_target_address,sstore_target_data)
            
            if opcode_express.is_z3_express(sstore_target_address) :
                if is_valid_vuln :
                    vulnable,vuln_data = vuln_checker.change_storage_check(self.state_object,sstore_target_address,sstore_target_data,self.input_data)
                    if vulnable :
                        self.vuln_data += vuln_data + '\n'
            #     vuln_checker.transfer_overflow_check(self.state_object,sstore_target_address,sstore_target_data)

            next_pc = opcode_object.get_address() + 1
        elif 'SLOAD' == opcode_name :
            sstore_target_address = self.state_object.stack.pop_data()

            
            if not opcode_express.is_z3_express(sstore_target_address) :
                sstore_target_address = format_to_hex(sstore_target_address)
            
            # not support get dym address data
            data = self.state_object.store.get(sstore_target_address)
            
            if not opcode_express.is_z3_express(data) :
                data = format_to_bitVal(data)

            self.state_object.stack.push_data(data)

            next_pc = opcode_object.get_address() + 1
        elif 'CALLER' == opcode_name :
            self.state_object.stack.push_data(self.input_data['caller'])

            next_pc = opcode_object.get_address() + 1
        elif 'CALLVALUE' == opcode_name :
            self.state_object.stack.push_data(self.input_data['callvalue'])

            next_pc = opcode_object.get_address() + 1
        elif 'CALLDATASIZE' == opcode_name :
            self.state_object.stack.push_data(self.input_data['callsize'])

            next_pc = opcode_object.get_address() + 1
        elif 'CALLDATALOAD' == opcode_name :
            calldata_offset = self.state_object.stack.pop_data()
            self.state_object.stack.push_data(opcode_express.opcode_call_data(self.input_data['calldata'],calldata_offset))

            next_pc = opcode_object.get_address() + 1
        elif 'CODESIZE' == opcode_name :
            self.state_object.stack.push_data(self.input_data['codesize'])

            next_pc = opcode_object.get_address() + 1
        elif 'EXTCODESIZE' == opcode_name :
            address = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(self.input_data['extcodesize'])

            next_pc = opcode_object.get_address() + 1
        elif 'GAS' == opcode_name :
            self.state_object.stack.push_data(self.input_data['gas'])

            next_pc = opcode_object.get_address() + 1
        elif 'GASPRICE' == opcode_name :
            self.state_object.stack.push_data(self.input_data['gasprice'])

            next_pc = opcode_object.get_address() + 1
        elif 'GASLIMIT' == opcode_name :
            self.state_object.stack.push_data(self.input_data['gaslimit'])

            next_pc = opcode_object.get_address() + 1
        elif 'NUMBER' == opcode_name :
            self.state_object.stack.push_data(self.input_data['blocknumber'])

            next_pc = opcode_object.get_address() + 1
        elif 'DIFFICULTY' == opcode_name :
            self.state_object.stack.push_data(self.input_data['difficulty'])

            next_pc = opcode_object.get_address() + 1
        elif 'ORIGIN' == opcode_name :
            self.state_object.stack.push_data(self.input_data['origin'])

            next_pc = opcode_object.get_address() + 1
        elif 'COINBASE' == opcode_name :
            self.state_object.stack.push_data(self.input_data['coinbase'])

            next_pc = opcode_object.get_address() + 1
        elif 'ADDRESS' == opcode_name :
            if type(self.contract_address) == str :
                address = format_to_bitVal(self.contract_address)
                self.state_object.stack.push_data(address)
            else :
                self.state_object.stack.push_data(self.input_data['address'])

            next_pc = opcode_object.get_address() + 1
        elif 'LT' == opcode_name :
            lt_left_data = self.state_object.stack.pop_data()
            lt_right_data = self.state_object.stack.pop_data()

            self.state_object.stack.push_data(opcode_express.opcode_lt(lt_left_data,lt_right_data))

            next_pc = opcode_object.get_address() + 1
        elif 'GT' == opcode_name :
            gt_left_data = self.state_object.stack.pop_data()
            gt_right_data = self.state_object.stack.pop_data()

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
            jump_next_pc_address = jump_next_pc_address.as_long()

            if not 'JUMPDEST' == self.code_object.get_disassmbly_by_address(jump_next_pc_address).get_opcode() :
                print 'JUMP Target Opcode Except ..'

                exit()

            if self.check_is_transfer_function_entry_point(check_condition) :
                if is_valid_vuln :
                    if not vuln_checker.transfer_check_fake_withdraw(self,jump_next_pc_address) :
                        print '\033[1;31m---- Transfer Fake Withdraw Check ! ----\033[0m'
                        print 'transfer_check_fake_withdraw : exist' + '\n'

            self.execute_context.add_branch_count()

            #print 'check_condition',check_condition
            #print 'simp',z3.simplify(check_condition)

            true_condition,false_condition = self.fork_branch(check_condition)

            if False == true_condition == false_condition :
                #self.state_object.add_express(check_condition)
                #self.state_object.show_code_stream()
                #self.state_object.show_express()
                
                return execute_death_path()

            #print true_condition,false_condition,check_condition.make_express()

            if not opcode_express.is_z3_express(check_condition) :  #  check is real true/false condition ..
                if true_condition :
                    #print 'jump true'
                    if not self.check_infinite_loop(opcode_object.get_address(), jump_next_pc_address) :
                        true_branch_executor = self.copy_executor()

                        true_branch_executor.run(jump_next_pc_address,is_valid_vuln = is_valid_vuln,debug_output = debug_output)

                        if true_branch_executor.all_path_record :
                            for path_index in true_branch_executor.all_path_record :
                                self.all_path_record.append(self.execute_path + path_index)
                        else :
                            self.all_path_record.append(self.execute_path + true_branch_executor.execute_path)
                elif false_condition :
                    #print 'jump false'
                    if not self.check_infinite_loop(opcode_object.get_address(), jump_next_pc_address) :
                        false_branch_executor = self.copy_executor()

                        false_branch_executor.run(nojump_next_pc_address,is_valid_vuln = is_valid_vuln,debug_output = debug_output)

                        if false_branch_executor.all_path_record :
                            for path_index in false_branch_executor.all_path_record :
                                self.all_path_record.append(self.execute_path + path_index)
                        else :
                            self.all_path_record.append(self.execute_path + false_branch_executor.execute_path)
            else :
                #print 'jump true and false:',true_condition,false_condition 
                if true_condition :
                    if not self.check_infinite_loop(opcode_object.get_address(), jump_next_pc_address) :
                        true_branch_executor = self.copy_executor()

                        true_branch_executor.state_object.add_express(check_condition)
                        true_branch_executor.run(jump_next_pc_address,is_valid_vuln = is_valid_vuln,debug_output = debug_output)

                        if true_branch_executor.all_path_record :
                            for path_index in true_branch_executor.all_path_record :
                                self.all_path_record.append(self.execute_path + path_index)
                        else :
                            self.all_path_record.append(self.execute_path + true_branch_executor.execute_path)

                if false_condition :
                    if not self.check_infinite_loop(opcode_object.get_address(), jump_next_pc_address) :
                        false_branch_executor = self.copy_executor()

                        false_branch_executor.state_object.add_express(opcode_express.opcode_logic_not(check_condition))
                        false_branch_executor.run(nojump_next_pc_address,is_valid_vuln = is_valid_vuln,debug_output = debug_output)

                        if false_branch_executor.all_path_record :
                            for path_index in false_branch_executor.all_path_record :
                                self.all_path_record.append(self.execute_path + path_index)
                        else :
                            self.all_path_record.append(self.execute_path + false_branch_executor.execute_path)

            return -1
        elif 'JUMP' == opcode_name :
            jump_next_pc_address = self.state_object.stack.pop_data()

            jump_next_pc_address = jump_next_pc_address.as_long()
                # try :
                #     jump_next_pc_address = int(jump_next_pc_address,16)
                # except :
                #     if 'make_express' in dir(jump_next_pc_address) :
                #         if not opcode_express.is_take_input(jump_next_pc_address) :
                #             jump_next_pc_address = execute_real_express(jump_next_pc_address)
            
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
            # todo push call result 0 success 1 fail
            self.state_object.stack.push_data(0)

            if is_valid_vuln :
                vulnable,vuln_data = vuln_checker.arbitrarily_call(self.state_object,call_address,self.input_data)

                if vulnable :
                    self.vuln_data += vuln_data + '\n'

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

            # vuln_checker.div_zero_check(self.state_object,number2)

            self.state_object.stack.push_data(opcode_express.opcode_div(number1,number2))

            # if 'make_express' in dir(number1):
            #     print 'div n1',number1.make_express()
            # else :
            #     print 'div n1',number1
            
            # if 'make_express' in dir(number2):
            #     print 'div n2',number2.make_express()
            # else :
            #     print 'div n2',number2    
            # print 'div rs', opcode_express.opcode_div(number1,number2).make_express()

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
            self.state_object.stack.push_data(self.input_data['returndatasize'])

            next_pc = opcode_object.get_address() + 1
        elif 'RETURNDATACOPY' == opcode_name :
            copy_to_addr   = self.state_object.stack.pop_data()
            copy_from_addr = self.state_object.stack.pop_data()
            copy_length    = self.state_object.stack.pop_data()

            if is_valid_vuln :
                vuln_checker.print_input(self.state_object,self.input_data)
            # self.input_data['memory'] = opcode_express.opcode_return_data_copy(self.input_data['calldata'],
            #                                      self.input_data['memory'],
            #                                      target_memory,
            #                                      call_offset,
            #                                      call_length)
            
            # try :
            #     copy_to_addr = int(copy_to_addr)
            # except :
            #     copy_to_addr = int(copy_to_addr,16)

            # try :
            #     copy_from_addr = int(copy_from_addr)
            # except :
            #     copy_from_addr = int(copy_from_addr,16)

            # self.state_object.memory.set_32byte(copy_to_addr,self.state_object.memory.get_32byte(copy_from_addr))

            next_pc = opcode_object.get_address() + 1
        elif 'CODESIZE' == opcode_name :
            self.state_object.stack.push_data(self.code_object.get_disassmbly_data_length())

            next_pc = opcode_object.get_address() + 1
        elif 'CODECOPY' == opcode_name :
            target_memory = self.state_object.stack.pop_data()
            code_offset = self.state_object.stack.pop_data()
            code_length = self.state_object.stack.pop_data()
            code_offset = opcode_express.format_to_int(code_offset)
            code_length = opcode_express.format_to_int(code_length)
            # try :
            #     target_memory = int(target_memory)
            # except :
            #     target_memory = int(target_memory,16)

            # try :
            #     code_offset = int(code_offset)
            # except :
            #     code_offset = int(code_offset,16)

            # try :
            #     code_length = int(code_length)
            # except :
            #     code_length = int(code_length,16)
            

            code_data = self.code_object.get_bytecode_data(code_offset,code_length)
            self.input_data['memory'] = opcode_express.opcode_write_memory(self.input_data['memory'], target_memory, code_data, code_length)


            # self.state_object.memory.set_real_data(target_memory,code_data,code_length)

            next_pc = opcode_object.get_address() + 1
        elif 'CALLDATACOPY' == opcode_name :
            target_memory = self.state_object.stack.pop_data()
            call_offset = self.state_object.stack.pop_data()
            call_length = self.state_object.stack.pop_data()
            # if 'make_express' in dir(target_memory) :
            #     if not opcode_express.is_take_input(target_memory) :
            #         target_memory = execute_value_express(target_memory)
            
            # try :
            #     target_memory = int(target_memory)
            # except :
            #     target_memory = int(target_memory,16)

            # self.state_object.memory.set_32byte(target_memory,opcode_express.opcode_call_data(call_offset))

            # write_express = memory_express,

            # self.state_object.add_express(write_express)
            self.input_data['memory'] = opcode_express.opcode_call_data_copy(self.input_data['calldata'],
                                                 self.input_data['memory'],
                                                 target_memory,
                                                 call_offset,
                                                 call_length)

            next_pc = opcode_object.get_address() + 1
        elif 'KECCAK256' == opcode_name or 'SHA3' == opcode_name :
            data_point = self.state_object.stack.pop_data()
            data_length = self.state_object.stack.pop_data()

            # try :
            #     data_point = int(data_point)
            # except :
            #     data_point = int(data_point,16)

            data = opcode_express.opcode_get_memory(self.input_data['memory'], data_point, data_length)

            self.state_object.stack.push_data(opcode_express.opcode_sha3(data))

            # memory_object = self.state_object.memory.get_64byte(data_point)

            # self.state_object.stack.push_data(opcode_express.opcode_sha3(memory_object))

            next_pc = opcode_object.get_address() + 1
        elif 'SELFDESTRUCT' == opcode_name :
            target_address = self.state_object.stack.pop_data()

            if is_valid_vuln :
                vulnable,vuln_data = vuln_checker.arbitrarily_selfdestruct(self.state_object,target_address,self.input_data)

                if vulnable :
                    self.vuln_data += vuln_data + '\n'

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
            #if len(self.vuln_data) > 0 :
            #    print self.vuln_data
        
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

            value = 0
            topic = 0

            if log_count == 3 :
                value = opcode_express.opcode_get_memory(self.input_data['memory'],memory_start,memory_size)
            
            for i in range(log_count) :
                temp = self.state_object.stack.pop_data()
                if log_count == 3 and i == 0 :
                    topic = temp
                if log_count == 4 and i == 3 :
                    value = temp
            
            if is_valid_vuln :
                vuln_checker.add_balance_check(self.state_object,topic,value,self.input_data)
            
            next_pc = opcode_object.get_address() + 1
        else :
            print 'Unknow Opcode ..'
            print hex(opcode_object.get_address()),opcode_name,opcode_object.get_opcode_data()

            exit()

        #print hex(opcode_object.get_address()),opcode_name,opcode_object.get_opcode_data()

        #self.state_object.stack.print_stack()

        return next_pc

    '''

    explore is a function 

    def explore(executor,pc,current_opcode) :  # return True/False
        ...
        return True

    '''

    def run(self,pc = 0,explore = False,is_valid_vuln = True,debug_output = False) :
        opcode_address_list = self.code_object.get_disassmbly_address_list()

        if explore :
            self.explore_function = explore

        is_explore_success = False
        execute_opcode_record = []

        while pc in opcode_address_list :
            current_opcode = self.code_object.get_disassmbly_by_address(pc)

            execute_opcode_record.append(current_opcode)
            self.execute_path.append(current_opcode)

            if self.explore_function and not is_explore_success :
                if self.explore_function(self,pc,current_opcode) :
                    is_explore_success = True

            try :
                pc = self.execute_opcode(current_opcode,is_valid_vuln = is_valid_vuln,debug_output = debug_output)
            except KeyboardInterrupt:
                raise
            except :
                #vuln_checker.print_input(self.state_object)
                raise
            
            # self.state_object.stack.print_stack()

            if not type(pc) == int :
                if pc.__class__ == execute_revert :
                    pass
                elif pc.__class__ == execute_revert :
                    pass

        if not is_explore_success :
            return []

        return execute_opcode_record

    def get_execute_branch_count(self) :
        return self.execute_context.get_branch_count()

    def get_execute_instrutment_count(self) :
        return self.execute_context.get_instrutment_count()


class vuln_checker :

    @staticmethod
    def change_storage_check(state_object,address_object,data_object,input_data) :
        check_result = False

        if  not opcode_express.is_z3_express(address_object) :
            return False,''

        # import z3

        # z3_init_list = opcode_express.make_z3_init()

        # for init_index in z3_init_list :
        #     exec(init_index)

        solver = z3.Solver()

        for express_data in state_object.express_list :
            # express_data = express_index.make_express()
            solver.add(format_to_bool(express_data))
            # exec('solver.add(%s)' % (express_data))

        address_express = address_object
        data_express = data_object
        solver.add(input_data['caller'] == opcode_express.DEFAULT_INPUT_ADDRESS)
        solver.add(data_express > 0)
        # exec('solver.add((%s) == %s)' % (address_express,opcode_express.DEFAULT_INPUT_ADDRESS))
        # exec('solver.add(%s > 0)' % (data_express))
        payload_result = ''
        if z3.sat == solver.check() :
            payload_result += '\033[1;31m---- change storage Vuln Check ! ----\033[0m' + '\n'
            payload_result += 'Auto Building Test Payload :' + '\n'

            check_result = True
            
            model_data = solver.model()

            for key_index in model_data :
                if str(key_index) == 'calldata' :
                    calldata_array = []
                    
                    for i in range(opcode_express.opcode_call_data_config.LENGTH) :
                        calldata_array.append(int(str(model_data.eval(input_data['calldata'][i]))))
                    
                    value = '0x' + ''.join('{:02x}'.format(x) for x in calldata_array)
                else :
                    value = hex(int(str(model_data[key_index])))
                
                payload_result += '033[1;34m>>' + str(key_index) + str(value) + '\033[0m' + '\n'
                print payload_result
        return check_result,payload_result

    @staticmethod
    def add_balance_check(state_object,topic_object,data_object,input_data) :
        check_result = False

        # import z3

        # z3_init_list = opcode_express.make_z3_init()

        # for init_index in z3_init_list :
        #     exec(init_index)

        solver = z3.Solver()

        for express_data in state_object.express_list :
            # express_data = express_index.make_express()
            solver.add(format_to_bool(express_data))
            # exec('solver.add(%s)' % (express_data))
        
        topic_express = topic_object
        data_express = data_object

        solver.add(input_data['caller'] == opcode_express.DEFAULT_INPUT_ADDRESS)
        solver.add(data_express > 0)
        # Transfer Event
        solver.add(topic_express == opcode_express.TRANSFER_LOG_TOPIC_ADDRESS)
        # exec('solver.add((%s) == %s)' % (address_express,opcode_express.DEFAULT_INPUT_ADDRESS))
        # exec('solver.add(%s > 0)' % (data_express))
        payload_result = ''
        if z3.sat == solver.check() :
            payload_result += '\033[1;31m---- add balance Vuln Check ! ----\033[0m' + '\n'
            payload_result += 'Auto Building Test Payload :' + '\n'

            check_result = True
            
            model_data = solver.model()

            for key_index in model_data :
                if str(key_index) == 'calldata' :
                    calldata_array = []
                    
                    for i in range(opcode_express.opcode_call_data_config.LENGTH) :
                        calldata_array.append(int(str(model_data.eval(input_data['calldata'][i]))))
                    
                    value = '0x' + ''.join('{:02x}'.format(x) for x in calldata_array)
                else :
                    value = hex(int(str(model_data[key_index])))
                
                payload_result += '033[1;34m>>' + str(key_index) + str(value) + '\033[0m' + '\n'
                print payload_result
        return check_result,payload_result
    
#     @staticmethod
#     def transfer_overflow_check(state_object,address_object,check_object) :
#         check_result = False

#         if  not opcode_express.is_take_input(address_object) and \
#             not opcode_express.is_input(address_object) :
#             return False

#         import z3

#         z3_init_list = opcode_express.make_z3_init()

#         for init_index in z3_init_list :
#             exec(init_index)

#         solver = z3.Solver()

#         for express_index in state_object.express_list :
#             express_data = express_index.make_express()

#             exec('solver.add(%s)' % (express_data))

#         if not opcode_express.is_take_input(check_object) and not opcode_express.is_input(check_object):
#             condition_value = execute_real_express(check_object)
#         else :
#             address_express = address_object.make_express()
#             check_express = check_object.make_express()

#             exec('solver.add((%s) == %s)' % (address_express,opcode_express.DEFAULT_INPUT_ADDRESS))
#             exec('solver.add(%s < 0)' % (check_express))

#             if z3.sat == solver.check() :
#                 print '\033[1;31m---- Transfer Overflow Vuln Check ! ----\033[0m'
#                 print 'Auto Building Test Payload :'

#                 check_result = True
#                 model_data = solver.model()

#                 for key_index in model_data :
#                     if str(key_index) == 'calldata' :
#                         calldata_array = []
                        
#                         for i in range(opcode_express.opcode_call_data.LENGTH) :
#                             calldata_array.append(int(str(model_data.eval(calldata[i]))))
                        
#                         value = '0x' + ''.join('{:02x}'.format(x) for x in calldata_array)
#                     else :
#                         value = hex(int(str(model_data[key_index])))
                    
#                     print '\033[1;34m>>',key_index,value,'\033[0m'

#         return check_result

    @staticmethod
    def arbitrarily_selfdestruct(state_object,address_object,input_data) :
        check_result = False

        if  not opcode_express.is_z3_express(address_object) :
            return False,''

        solver = z3.Solver()

        for express_data in state_object.express_list :
            solver.add(format_to_bool(express_data))

        check_express = address_object
        payload_result = ''
        solver.add(check_express == opcode_express.DEFAULT_INPUT_ADDRESS)

        if z3.sat == solver.check() :
            payload_result += '\033[1;31m---- Arbitrarily Self-Destruct Vuln Check ! ----\033[0m' + '\n'
            payload_result += 'Auto Building Test Payload :' + '\n'

            check_result = True
            model_data = solver.model()

            for key_index in model_data :
                if str(key_index) == 'calldata' :
                    calldata_array = []
                    
                    for i in range(opcode_express.opcode_call_data_config.LENGTH) :
                        calldata_array.append(int(str(model_data.eval(input_data['calldata'][i]))))
                    
                    value = '0x' + ''.join('{:02x}'.format(x) for x in calldata_array)
                else :
                    value = hex(int(str(model_data[key_index])))
                
                payload_result += '\033[1;34m>>' + str(key_index) + str(value) + '\033[0m' + '\n'

        return check_result,payload_result

    @staticmethod
    def arbitrarily_call(state_object,address_object,input_data) :
        check_result = False

        if not opcode_express.is_z3_express(address_object) :
            return False,''

        solver = z3.Solver()

        for express_data in state_object.express_list :
            solver.add(format_to_bool(express_data))

        check_express = address_object
        payload_result = ''
        solver.add(check_express == opcode_express.DEFAULT_INPUT_CONTRACT_ADDRESS)

        if z3.sat == solver.check() :
            payload_result += '\033[1;31m---- Arbitrarily CALL Vuln Check ! ----\033[0m' + '\n'
            payload_result += 'Auto Building Test Payload :' + '\n'

            check_result = True
            model_data = solver.model()

            for key_index in model_data :
                if str(key_index) == 'calldata' :
                    calldata_array = []
                    
                    for i in range(opcode_express.opcode_call_data_config.LENGTH) :
                        calldata_array.append(int(str(model_data.eval(input_data['calldata'][i]))))
                    
                    value = '0x' + ''.join('{:02x}'.format(x) for x in calldata_array)
                else :
                    value = hex(int(str(model_data[key_index])))
                
                payload_result += '\033[1;34m>>' + str(key_index) + str(value) + '\033[0m' + '\n'

        return check_result,payload_result

    @staticmethod
    def transfer_check_fake_withdraw(executor_object,transfer_function_entry) :
        check_executor_object = executor_object.copy_executor()
        
        check_executor_object.state_object.store.set_default_return_value(0x1000) # set default user balance
        check_executor_object.run(transfer_function_entry,is_valid_vuln = False)

        def explore_transfer_log(executor_object,pc,current_opcode) :
            if not current_opcode.get_opcode().startswith('LOG') :
                return False

            log_count = int(current_opcode.get_opcode()[ 3 : ])
            topic_address = executor_object.state_object.stack.get_top_index_data(2)
            topic_address = topic_address.as_long()

            if topic_address == opcode_express.TRANSFER_LOG_TOPIC_ADDRESS :
                return True

            return False

        explore_executor_object = executor_object.copy_executor()

        explore_executor_object.state_object.store.set_default_return_value(0x1000)
        transefer_path = explore_executor_object.run(transfer_function_entry,is_valid_vuln = False,explore = explore_transfer_log)

        for sub_path_index in check_executor_object.all_path_record :
            is_transfer_path = False

            for success_transfer_path_index in explore_executor_object.all_path_record :
                if sub_path_index == success_transfer_path_index :
                    is_transfer_path = True

                    break

            if is_transfer_path :
                if not ('REVERT' == sub_path_index[-1].get_opcode() or \
                    'INVALID' == sub_path_index[-1].get_opcode()) :
                    return False

        for success_transfer_path_index in explore_executor_object.all_path_record :
            if not ('RETURN' == success_transfer_path_index[-1].get_opcode() or \
                'STOP' == success_transfer_path_index[-1].get_opcode()) :
                return False

        return True

    @staticmethod
    def print_input(state_object,input_data) :
        solver = z3.Solver()

        for express_data in state_object.express_list :
            solver.add(format_to_bool(express_data))

        if z3.sat == solver.check() :
            print '\033[1;31m---- print input ----\033[0m' + '\n'
            print 'Auto Building Test Payload :' + '\n'

            check_result = True
            model_data = solver.model()

            for key_index in model_data :
                if str(key_index) == 'calldata' :
                    calldata_array = []
                    
                    for i in range(opcode_express.opcode_call_data_config.LENGTH) :
                        calldata_array.append(int(str(model_data.eval(input_data['calldata'][i]))))
                    
                    value = '0x' + ''.join('{:02x}'.format(x) for x in calldata_array)
                else :
                    value = hex(int(str(model_data[key_index])))
                
                print '\033[1;34m>>',key_index,value,'\033[0m','\n'

        return True
    
#     @staticmethod
#     def div_zero_check(state_object,number_object) :
#         check_result = False

#         if  not opcode_express.is_take_input(number_object) and \
#             not opcode_express.is_input(number_object) :
#             if opcode_express.is_opcode_object(number_object) :
#                 if 0 == execute_value_express(number_object) :
#                     check_result = True
#             else :
#                 try :
#                     number_object = int(number_object)
#                 except :
#                     number_object = int(number_object,16)

#                 if 0 == number_object :
#                     check_result = True

#             return check_result

#         import z3

#         z3_init_list = opcode_express.make_z3_init()

#         for init_index in z3_init_list :
#             exec(init_index)

#         solver = z3.Solver()

#         for express_index in state_object.express_list :
#             express_data = express_index.make_express()

#             exec('solver.add(%s)' % (express_data))

#         check_express = number_object.make_express()

#         exec('solver.add((%s) == 0)' % (check_express))

#         if z3.sat == solver.check() :
#             print '\033[1;31m---- Div Zero Bug Check ! ----\033[0m'
#             print 'Auto Building Test Payload :'

#             check_result = True
#             model_data = solver.model()

#             for key_index in model_data :
#                 if str(key_index) == 'calldata' :
#                     calldata_array = []
                    
#                     for i in range(opcode_express.opcode_call_data.LENGTH) :
#                         calldata_array.append(int(str(model_data.eval(calldata[i]))))
                    
#                     value = '0x' + ''.join('{:02x}'.format(x) for x in calldata_array)
#                 else :
#                     value = hex(int(str(model_data[key_index])))
                
#                 print '\033[1;34m>>',key_index,value,'\033[0m'

#         return check_result


