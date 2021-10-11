class if_id:

    def __init__(self):
        self.ir = ''
        self.prevpc = ''
        self.pc = '0x0'   # next pc

    def update(self,pc,ir,PC_temp):
        self.prevpc = PC_temp
        self.pc = pc
        self.ir = ir

class id_ex:
    def __init__(self):
        self.IR = ''
        self.con_mux = ''
        self.funct3 = ''
        self.muxY_byte_update = ''
        self.rm = ''
        self.rd = ''
        self.imm = ''
        self.rd = ''
        self.opcode = ''
        self.muxINC_update = ''
        self.PC_temp = ''
        self.PC = ''
        self.RA = ''
        self.rd = ''

    def update_R (self,con_mux,rd,opcode):
        self.rd = rd
        self.con_mux = con_mux
        self.opcode = opcode

    def update_I(self,con_mux,rd,opcode):
        self.rd = rd
        self.con_mux = con_mux
        self.opcode = opcode

    def update_jal(self,con_mux,imm,muxINC_update,opcode,PC_temp,PC,rd):
        self.imm = imm
        self.con_mux = con_mux
        self.muxINC_update = muxINC_update
        self.opcode = opcode
        self.PC_temp = PC_temp
        self.PC = PC
        self.rd = rd

    def update_jalr(self,con_mux,imm,muxINC_update,opcode,PC_temp,PC,RA,rd):
        self.imm = imm
        self.con_mux = con_mux
        self.muxINC_update = muxINC_update
        self.opcode = opcode
        self.PC_temp = PC_temp
        self.PC = PC
        self.RA = RA
        self.rd = rd

    def update_load(self,rd,con_mux,muxY_byte_update,opcode):
        self.con_mux = con_mux
        self.rd = rd
        self.muxY_byte_update = muxY_byte_update
        self.opcode = opcode

    def update_auipc_lui(self,rd,con_mux,opcode):
        self.rd = rd
        self.con_mux = con_mux
        self.opcode = opcode

    def update_sb(self,con_mux,imm,muxINC_update,opcode,PC_temp,PC):
        self.imm = imm
        self.con_mux = con_mux
        self.muxINC_update = muxINC_update
        self.opcode = opcode
        self.PC_temp = PC_temp
        self.PC = PC

    def update_S(self,con_mux,rm,muxY_byte_update,opcode):
        self.con_mux = con_mux
        self.rm = rm
        self.muxY_byte_update = muxY_byte_update
        self.opcode = opcode

class ex_mem:
    def __init__(self):
        self.con_mux = {}
        self.opcode = ''
        self.muxY_byte_update = ''
        self.rm = ''
        self.rd = ''
        self.imm = ''
        self.PC_temp = ''
        self.PC = ''

    def nonbranch_SB(self,con_mux,opcode,muxY_byte_update,rm,rd,imm,PC_temp):
        self.con_mux = con_mux
        self.opcode = opcode
        self.muxY_byte_update = muxY_byte_update
        self.rm  = rm
        self.rd = rd
        self.imm = imm
        self.PC_temp = PC_temp

    def branch(self,PC_temp,rd):
        self.PC_temp = PC_temp
        self.rd = rd

class mem_wr:
    def __init__(self):
        self.rd = ''
        self.opcode = ''

    def update(self,rd,opcode):
        self.rd = rd
        self.opcode = opcode

def convert_binary_to_integer(imm, bits):
    if imm[2] == '1':
        imm = int(imm, 2) - 2 ** bits
    else:
        imm = int(imm, 2)
    return imm

# immediate in binary
def convert_to_hex_extend(imm):
    if imm[0] == '1':           # negative number
        imm = hex(int(imm, 2))  # need to extend it to 32 bits
        length = 10 - len(imm)
        imm = '0x' + 'f' * length + imm[2:]
    else:
        imm = hex(int(imm, 2))  # need to extend it to 32 bits
        length = 10 - len(imm)
        imm = imm[0:2] + '0' * length + imm[2:]
    return imm

class Regfile:

    def __init__(self):
        self.dcreg = {
            "00000": "0x00000000", "00001": "0x00000000", "00010": "0x7ffffff0", "00011": "0x10000000",
            "00100": "0x00000000",
            "00101": "0x00000000", "00110": "0x00000000", "00111": "0x00000000", "01000": "0x00000000",
            "01001": "0x00000000",
            "01010": "0x00000000", "01011": "0x00000000", "01100": "0x00000000", "01101": "0x00000000",
            "01110": "0x00000000",
            "01111": "0x00000000", "10000": "0x00000000", "10001": "0x00000000", "10010": "0x00000000",
            "10011": "0x00000000",
            "10100": "0x00000000", "10101": "0x00000000", "10110": "0x00000000", "10111": "0x00000000",
            "11000": "0x00000000",
            "11001": "0x00000000", "11010": "0x00000000", "11011": "0x00000000", "11100": "0x00000000",
            "11101": "0x00000000",
            "11110": "0x00000000", "11111": "0x00000000"}
        self.rs1 = "000000"
        self.rs2 = "000000"
        self.rd = "00000"
        self.wrline = "0x00000000"
        self.rdline1 = "0x00000000"
        self.rdline2 = "0x00000000"

    # updates MUX A and B with the values req. from reg_file and makes regfile aware about rd
    def reg_extract(self, rd, muxA, muxB, rs1, rs2):
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.rdline1 = self.dcreg[rs1]
        self.rdline2 = self.dcreg[rs2]
        muxA.update(self.rdline1, 0)
        muxB.update(self.rdline2, 0)

    # to quickly obtain value in x1
    def obtain_RA(self):
        return self.dcreg['00001']

    # updates values in the regfile at required register
    def load(self, inp):
        self.wrline = inp
        if self.rd != '00000':
            self.dcreg[self.rd] = self.wrline
        else:
            self.dcreg[self.rd] = "0x00000000"

class ALU:
    def __init__(self, in0, in1):
        self.in1 = in1
        self.in0 = in0
        self.out = '0x00000000'

    # updated control signal
    def con_update(self, con_sig):
        self.con = con_sig

    # updates input
    def in_update(self, inp, in_no):
        if in_no == '0':
            self.in0 = inp
        else:
            self.in1 = inp

    # inputs are 32 bit in hexadecimal form and same is the output
    @property
    def control(self):
        # check for -ve
        if (self.in0[2] == 'f' or self.in0[2] == 'e' or self.in0[2] == 'd' or self.in0[2] == 'c' or self.in0[2] == 'b'
                or self.in0[2] == 'a' or self.in0[2] == '9' or self.in0[2] == '8'):
            var1 = int(self.in0[2:], 16) - 2 ** 32
        else:
            var1 = int(self.in0[2:], 16)

        if (self.in1[2] == 'f' or self.in1[2] == 'e' or self.in1[2] == 'd' or self.in1[2] == 'c' or self.in1[2] == 'b'
                or self.in1[2] == 'a' or self.in1[2] == '9' or self.in1[2] == '8'):
            var2 = int(self.in1[2:], 16) - 2 ** 32
        else:
            var2 = int(self.in1[2:], 16)

        # perform required operation based upon control signal
        if self.con == '0000':
            self.out = var1 + var2

        elif self.con == '0001':
            self.out = var1 & var2

        elif self.con == '0010':
            self.out = var1 | var2

        elif self.con == '0011':
            self.out = var1 << var2

        elif self.con == '0100':
            self.out = var1 >> var2

        # no function in python to shift right logically so manually done
        elif self.con == '0101':
            str = bin(int(self.in0,16))
            str = str[0:2] + '0' * (34-len(str)) + str[2:]          # to make str 32 bits long with '0b' in start
            self.out = str[0:2] + '0' * var2 + str[2: 34 - var2]    # introducing req. 0 in front as well as ensuring output to be 32 bits
            self.out = int(self.out, 2)

        elif self.con == '0110':
            self.out = var1 - var2

        elif self.con == '0111':
            self.out = var1 ^ var2

        elif self.con == '1000':
            # division in python results in floating number
            self.out = int(var1 / var2)

        elif self.con == '1001':
            self.out = var1 * var2

        elif self.con == '1010':
            self.out = var1 % var2

        # slt instruction
        elif self.con == '1011':
            val = var1 - var2
            if val >= 0:
                self.out = '0x00000000'
            else:
                self.out = '0x00000001'
            return

        # beq instruction
        elif self.con == '1100':
            self.out = '0x00000000'
            if var1 == var2:
                return '1'
            else:
                return '0'

        # bne instruction
        elif self.con == '1101':
            self.out = '0x00000000'
            if var1 != var2:
                return '1'
            else:
                return '0'

        # bge instruction
        elif self.con == '1110':
            self.out = '0x00000000'
            if var1 >= var2:
                return '1'
            else:
                return '0'

        # blt instruction
        elif self.con == '1111':
            self.out = '0x00000000'
            if var1 < var2:
                return '1'
            else:
                return '0'

        # converting -ve num to +ve for conversion to hexadecimal
        if self.out<0:
            self.out+= 2 ** 32

        self.out = hex(self.out)
        length = 10 - len(self.out)
        # need to extend it to 32 bits
        self.out = self.out[0:2] + '0' * length + self.out[2:]
        return

class IAG:
    def __init__(self):
        self.PC = '0x0'
        self.RA = '0x00000000'
        self.muxINC = Mux('0x0004', '0x0000')
        self.adder = Adder(self.PC, self.muxINC.out)
        self.muxPC = Mux(self.RA, self.adder.out)
        self.PC_temp = self.PC

    def update_fetch(self, PC):
        self.RA = '0x00000000'
        self.muxINC = Mux('0x0004', '0x0000')
        self.PC_temp = PC           # this step helps later for branch instruction
        self.PC = PC
        self.muxINC.control('0')
        self.adder.in_update(self.PC, self.muxINC.out)
        self.adder.control_initial()
        self.muxPC.update(self.adder.out, 1)
        self.muxPC.control('1')
        self.PC = self.muxPC.out

class Mux:
    def __init__(self, in0, in1):
        self.in1 = in1
        self.in0 = in0
        self.out = '0x00000000'

    # updating inputs of the Mux
    # if ln_no is 1 then update in1 else in0
    def update(self, inp, ln_no):
        if ln_no == 1:
            self.in1 = inp
        else:
            self.in0 = inp

    # evaluating output based on control line
    def control(self, con_sig):
        if con_sig == '0':
            self.out = self.in0
        else:
            self.out = self.in1

class MuxY:
    def __init__(self, in0, in1, in2):
        self.in2 = in2
        self.in1 = in1
        self.in0 = in0
        self.out = '0x00000000'

    # updating inputs of the MuxY
    def update(self, inp, ln_no):
        if ln_no == 1:
            self.in1 = inp
        elif ln_no == 2:
            self.in2 = inp
        else:
            self.in0 = inp

    # self.byte stores no. of bytes to be stored or loaded from memory      ###########################
    def byte_update(self, byte):
        self.byte = byte

    # evaluating output based on control line
    def control(self, con_sig):
        if con_sig == '00':
            self.out = self.in0
        elif con_sig == '01':
            self.out = self.in1
        elif con_sig == '10':
            self.out = self.in2

# MAR :address;byte:bytes to be loaded;mem:initial dictionary(memory) created
def load_from_memory( MAR, byte, mem):
    check1 = 0
    check2 = 0
    ke1 = ''
    ke2 = ''
    b = int(MAR.replace("0x", ''), 16)
    rem1 = b % 4
    rem2 = 4 - rem1
    adr1 = b - rem1
    adr2 = b + rem2
    adr1 = hex(adr1)
    adr2 = hex(adr2)
    if adr1 in mem.keys():
        check1 = 1  # checking both the address in memory
    if adr2 in mem.keys():
        check2 = 1

    # if not present,then update in mem dict with initial values 0
    if check1 == 0 and check2 == 0:
        ke1 = "00000000"
        ke2 = "00000000"
        mem.update({adr1: ke1, adr2: ke2})

    # if one present and other not,update the one not present
    elif check1 == 0 and check2 == 1:
        ke1 = "00000000"
        mem.update({adr1: ke1})
        ke2 = mem.get(adr2)
        # making key value upto 32 bits(i.e. 8bytes),if not initially
        ke2 += '0' * (8 - len(ke2))
        mem.update({adr2: ke2})

    elif check1 == 1 and check2 == 0:
        ke2 = "00000000"
        ke1 = mem.get(adr1)
        ke1 += '0' * (8 - len(ke1))
        mem.update({adr1: ke1, adr2: ke2})

    elif check1 == 1 and check2 == 1:
        ke1 = mem.get(adr1)
        ke2 = mem.get(adr2)
        ke1 += '0' * (8 - len(ke1))
        ke2 += '0' * (8 - len(ke2))
        mem.update({adr1: ke1, adr2: ke2})

    # tot=6
    tot = rem1 + byte
    MDR = ''
    if tot == 4:  # loading of bytes
        # MDR = ke1[7:rem1 * 2]  # loading of 4 bytes from 0x10000010
        for i in range(6, rem1 * 2 - 2, -2):
            s = ke1[i:i + 2]
            MDR = MDR + s

    elif tot > 4:
        temp1 = ''
        temp2 = ''
        for i in range(6, rem1 * 2 - 2, -2):
            s = ke1[i:i + 2]
            temp1 = temp1 + s
        sub = tot - 4
        # temp2 = ke2[0:sub * 2]
        for i in range(0, sub * 2, 2):
            s = ke2[i:i + 2]
            temp2 = s + temp2
        MDR = temp2 + temp1
    else:
        # MDR = ke1[rem1 * 2:tot * 2]
        for i in range(tot * 2 - 2, rem1 * 2 - 2, -2):
            s = ke1[i:i + 2]
            MDR = MDR + s

    length = 8 - len(MDR)
    MDR = '0x' + '0' * length + MDR
    return MDR


# MAR :address;MDR: data to be stored; mem:initial dictionary(memory) created
def store_to_memory(MAR, MDR, mem):
    # store_value(0x10000011,2,20,data memory)
    check1 = 0
    check2 = 0
    s = ''
    tot = 0
    ke1 = ''
    ke2 = ''
    MDR = MDR.replace("0x", '')  # "14"
    byte = int(len(MDR) / 2)
    st_rev = ''
    for i in range(0, len(MDR), 2):
        s = MDR[i:i + 2]
        st_rev = s + st_rev

    b = int(MAR.replace("0x", ''), 16)
    rem1 = b % 4  # 3
    rem2 = 4 - rem1  # 1
    adr1 = b - rem1  # 10000008
    adr2 = b + rem2  # 10000012
    adr1 = hex(adr1)  # "0x10000008"
    adr2 = hex(adr2)  # "0x10000012"

    if adr1 in mem.keys():
        check1 = 1  # checking both the address in mem dictionary

    if adr2 in mem.keys():  # if present, make check=1
        check2 = 1

    if check1 == 0 and check2 == 0:
        ke1 = "00000000"  # if not present,then update in mem dict with initial values 0
        ke2 = "00000000"
        mem.update({adr1: ke1, adr2: ke2})

    elif check1 == 0 and check2 == 1:
        ke1 = "00000000"  # if one present and other not,update the one not present
        mem.update({adr1: ke1})
        ke2 = mem.get(adr2)
        ke2 += '0' * (8 - len(ke2))  # making key value upto 32 bits(i.e. 8bytes),if not initially
        mem.update({adr2: ke2})

    elif check1 == 1 and check2 == 0:
        ke2 = "00000000"
        ke1 = mem.get(adr1)
        ke1 += '0' * (8 - len(ke1))
        mem.update({adr1: ke1, adr2: ke2})

    elif check1 == 1 and check2 == 1:
        ke1 = mem.get(adr1)
        ke2 = mem.get(adr2)
        ke1 += '0' * (8 - len(ke1))
        ke2 += '0' * (8 - len(ke2))
        mem.update({adr1: ke1, adr2: ke2})

    tot = rem1 + byte  # tot=5
    if tot == 4:
        ke1 = ke1[0:rem1 * 2] + st_rev
        mem.update({adr1: ke1})

    elif tot > 4:
        key_temp = ''
        sub = tot - 4
        key_temp = ke1[0:rem1 * 2] + st_rev + ke2[sub * 2:]
        ke1 = key_temp[0:8]
        ke2 = key_temp[8:]
        mem.update({adr1: ke1, adr2: ke2})

    else:
        ke1 = ke1[0:rem1 * 2] + st_rev + ke1[tot * 2:]
        mem.update({adr1: ke1})

    MDR = '0x00000000'

# used for PC related hardware
class Adder:
    def __init__(self, in0, in1):
        self.in0 = in0
        self.in1 = in1
        self.out = '0x00000000'

    # updating inputs of the Adder
    def in_update(self, inp0, inp1):
        self.in0 = inp0
        self.in1 = inp1

    # called in fetch to add PC and 4. No need to check for -ve numbers. Output used for PC_next
    def control_initial(self):
        var1 = int(self.in1[2:], 16)
        var2 = int(self.in0[2:], 16)
        self.out = var1 + var2
        # no need to extend PC to 32 bits
        self.out = hex(self.out)

    def control(self, opcode):
        # inputs are 32 bit long but in hexadecimal...output(PC_next) need not be 32 bit long
        if (self.in0[2] == 'f' or self.in0[2] == 'e' or self.in0[2] == 'd' or self.in0[2] == 'c' or self.in0[2] == 'b'
                or self.in0[2] == 'a'):
            # checking if the input is negative(useful when backward branch needs to be taken)
            var1 = int(self.in0[2:], 16) - 2 ** 32
        else:
            var1 = int(self.in0[2:], 16)

        if (self.in1[2] == 'f' or self.in1[2] == 'e' or self.in1[2] == 'd' or self.in1[2] == 'c' or self.in1[2] == 'b'
                or self.in1[2] == 'a'):
            # checking if the input is negative(useful when backward branch needs to be taken)
            var2 = int(self.in1[2:], 16) - 2 ** 32
        else:
            var2 = int(self.in1[2:], 16)

        self.out = var1 + var2
        self.out = hex(self.out)

        # for branching instructions, adder.control called in 4th stage only if branch needs to be taken
        if opcode == "1100011":
            return
        return

class phase3:
    def __init__(self, file):
        # Knobs
        self.knob1 = 0
        self.knob2 = 0
        self.knob3 = 0
        self.knob4 = 0
        self.knob5 = 0

        # control for Knobs
        print(' >>> MODES <<<')
        print('Enter value of Knob1:')
        print('1 - To Enable Pipeline Execution')
        print('0 - To Disable Pipeline Execution')
        print('Enter your choice : ', end=' ')
        self.knob1 = int(input())
        if self.knob1 == 1:
            print('Enter value of Knob2:')
            print('1 - To Enable Data Forwarding')
            print('0 - To Disable Data Forwarding')
            print('Enter your choice : ', end=' ')
            self.knob2 = int(input())
        else:
            print('Knob2 is disabled as no pipeline execution')
            self.knob2 = 0
        print('Enter value of Knob3:')
        print('1 - To Enable printing values in the register file at the end of each cycle')
        print('0 - To Disable printing values in the register file at the end of each cycle')
        print('Enter your choice : ', end=' ')
        self.knob3 = int(input())
        print('Knob4 is disabled as no pipeline execution')
        print('Knob5 is disabled as no pipeline execution')

        # Components to end the execution of Program
        self.last_pc = ''

        # Hardware Components
        self.Ins_memory = {}  # Instruction Memory
        self.PC = '0x0'
        self.PC_temp = '0x0'
        self.RA = '0x00000000'
        self.muxINC = Mux('0x0004', '0x0000')
        self.adder = Adder(self.PC, self.muxINC.out)
        self.muxPC = Mux(self.RA, self.adder.out)
        self.IAG = IAG()
        self.clock = 0  # Clock

        self.reg1 = Regfile()
        self.control_ALU = {'+': '0000', '&': '0001', '|': '0010', '<<': '0011', '>>>': '0100', '>>': '0101',
                            '-': '0110', '^': '0111', '/': '1000', '*': '1001',
                            '%': '1010', '--': '1011', '=': '1100', '!=': '1101', '>=': '1110', '<': '1111'}
        # dictionary containing control signals for all muxes
        # E determines which execute path to take (the one in data path) or (the one in PC hardware) 'E'=1 if data path
        self.con_mux = {'A': '0', 'B': '0', 'Y': "00", 'INC': '0', 'PC': '0', 'E': '0'}
        self.muxB = Mux(self.reg1.rdline2, '0x00000000')  # first one selected when control line is '0'
        self.muxA = Mux(self.reg1.rdline1, self.PC)
        self.alu = ALU(self.muxA.out, self.muxB.out)
        self.rz = self.alu.out
        self.MAR = self.rz
        self.rm = self.muxB.in0
        self.MDR = self.rm
        self.muxY = MuxY(self.rz, self.MDR, self.PC_temp)
        self.ry = self.muxY.out
        self.reg1.load(self.ry)

        # Pipeline Registers
        self.if_id = if_id()
        self.id_ex = id_ex()
        self.ex_mem = ex_mem()
        self.mem_wr = mem_wr()

        # Printing Variables
        self.cycles = 0  # Cycles
        self.ex_inst = 0  # Total number of instruction executed
        self.cpi = 0  # CPI
        self.data_trasf = 0  # number of data - trasfer (load and store)
        self.alu_inst = 0  # number of ALU instruction executed
        self.control_inst = 0  # number of control instruction executed
        self.num_stalls = 0  # number of stalls/bubbles in the pipeline
        self.num_datahz = 0  # number of data hazards
        self.num_controlhz = 0  # number of control hazards
        self.num_misprediction = 0  # number of branch mispredictions
        self.num_stall_datahz = 0  # number of stalls due to data hazards
        self.num_stall_controlhz = 0  # number of stalls due to control hazards

        f = open('Instruction_Memory.mc', 'r+')
        line_array = f.readlines()
        for line in line_array:
            words = line.split()
            self.Ins_memory[words[0]] = words[1]
            if words[1] == '0xef000011' or words[1] == '0xEF000011':
                self.last_pc = words[0]

        self.mem = {}
        h = open('memory.txt', 'r+')
        line_array1 = h.readlines()
        for line in line_array1:
            line = line.replace(':', ' ')
            words = line.split()
            self.mem[words[0]] = words[1]

        if self.knob1 == 0:
            # Not Pipelined with Pipeline Registers
            while self.PC != self.last_pc:
                if self.PC in self.Ins_memory:
                    self.cycles += 1
                    print('Cycle Number : ' + str(self.cycles))
                    self.ex_inst += 5
                    self.data_trasf += 2

                    self.fetch()   # Next instruction address
                    a = self.decode()
                    if a:
                        continue  # for ld and sd instructions no work
                    self.execute()
                    self.mem_access()
                    self.register_update()
                    if self.knob3 == 1:
                        print(self.reg1.dcreg)
                else:
                    break
        # write data memory in the .mc file
        l = '\n\nData Memory :\n'
        for key in list(self.mem):
            l = l + (key + ' : ' + self.mem[key] + '\n')
        f.write(l)
        f.close()

        p = open("Output.txt", "w")
        p.write('Total number of cycles : ' + str(self.cycles) + '\n')
        p.write('Total instructions executed : ' + str(self.ex_inst) + '\n')
        self.cpi = self.ex_inst / self.cycles
        p.write('CPI : ' + str(self.cpi) + '\n')
        p.write('Number of Data-transfer (load and store) instructions executed : ' + str(self.data_trasf) + '\n')
        p.write('Number of ALU instructions executed : ' + str(self.alu_inst) + '\n')
        p.write('Number of Control instructions executed : ' + str(self.control_inst) + '\n')
        self.num_stalls = 0
        p.write('Number of Stalls/Bubbles in the pipeline : ' + str(self.num_stalls) + '\n')

        self.num_stall_datahz = 0
        p.write('Number of data hazards : ' + str(self.num_datahz) + '\n')
        self.num_controlhz = 0
        p.write('Number of control hazards : ' + str(self.num_controlhz) + '\n')
        self.num_misprediction = 0
        p.write('Number of branch mispredictions : ' + str(self.num_misprediction) + '\n')
        self.num_stall_datahz = 0
        self.num_stall_controlhz = 0
        p.write('Number of stalls due to data hazards : ' + str(self.num_stall_datahz) + '\n')
        p.write('Number of stalls due to control hazards : ' + str(self.num_stall_controlhz) + '\n')
        print("...... Execution Ended ......")


    def fetch(self):
        IR = self.Ins_memory[self.PC]
        IR = bin(int(IR, 16))
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        IR = IR[2:]
        # following steps update PC->PC + 4 using IAG
        self.IAG.update_fetch(self.PC)
        # updating the if_id buffer with current IR and Current PC
        self.if_id.update(self.IAG.PC,IR,self.IAG.PC_temp)
        self.PC = self.IAG.PC

    def decode(self):
        bin_int = self.if_id.ir
        opcode = bin_int[25:]
        if opcode == '0110011':  # R format
            self.alu_inst += 1
            funct3 = bin_int[17:20]
            rd = bin_int[20:25]
            rs1 = bin_int[12:17]
            rs2 = bin_int[7:12]
            funct7 = bin_int[0:7]
            # generate related control signals for all hardware
            self.con_mux['A'] = '0'
            self.con_mux['B'] = '0'
            self.con_mux['Y'] = '00'
            self.con_mux['E'] = '1'
            self.reg1.reg_extract(rd, self.muxA, self.muxB, rs1, rs2)
            if funct3 == '000' and funct7 == '0000000':
                self.alu.con_update(self.control_ALU['+'])
            elif funct3 == '111' and funct7 == '0000000':
                self.alu.con_update(self.control_ALU['&'])
            elif funct3 == '110' and funct7 == '0000000':
                self.alu.con_update(self.control_ALU['|'])
            elif funct3 == '001' and funct7 == '0000000':
                self.alu.con_update(self.control_ALU['<<'])
            elif funct3 == '010' and funct7 == '0000000':  # slt
                self.alu.con_update(self.control_ALU['--'])
            elif funct3 == '101' and funct7 == '0100000':
                self.alu.con_update(self.control_ALU['>>>'])
            elif funct3 == '101' and funct7 == '0000000':
                self.alu.con_update(self.control_ALU['>>'])
            elif funct3 == '000' and funct7 == '0100000':
                self.alu.con_update(self.control_ALU['-'])
            elif funct3 == '100' and funct7 == "0000000":
                self.alu.con_update(self.control_ALU['^'])
            elif funct3 == '000' and funct7 == '0000001':
                self.alu.con_update(self.control_ALU['*'])
            elif funct3 == '100' and funct7 == '0000001':
                self.alu.con_update(self.control_ALU['/'])
            elif funct3 == '110' and funct7 == '0000001':
                self.alu.con_update(self.control_ALU['%'])
            self.id_ex.update_R(self.con_mux, rd, opcode)

        elif opcode == '0010011':  # I format-andi,addi,ori
            self.alu_inst += 1
            funct3 = bin_int[17:20]
            rd = bin_int[20:25]
            rs1 = bin_int[12:17]
            imm = bin_int[0:12]
            imm1 = convert_to_hex_extend(imm)  # length 10 32 bit long hex number

            self.con_mux['E'] = '1'
            self.con_mux['A'] = '0'
            self.con_mux['B'] = '1'
            self.con_mux['Y'] = '00'
            self.muxB.update(imm1, 1)
            self.reg1.reg_extract(rd, self.muxA, self.muxB, rs1, '00000')

            if funct3 == '000':
                self.alu.con_update(self.control_ALU['+'])
            elif funct3 == '111':
                self.alu.con_update(self.control_ALU['&'])
            elif funct3 == '110':
                self.alu.con_update(self.control_ALU['|'])
            self.id_ex.update_I(self.con_mux, rd, opcode)

        elif opcode == '0000011':  # load instructions
            self.alu_inst += 1
            funct3 = bin_int[17:20]
            if funct3 == '011':
                print("Not supported instruction!")
                return 1
            rd = bin_int[20:25]
            rs1 = bin_int[12:17]
            imm = bin_int[0:12]
            imm1 = convert_to_hex_extend(imm)

            self.con_mux['E'] = '1'
            self.con_mux['A'] = '0'
            self.con_mux['B'] = '1'
            self.con_mux['Y'] = '01'
            self.alu.con_update(self.control_ALU['+'])
            self.muxB.update(imm1, 1)
            self.reg1.reg_extract(rd, self.muxA, self.muxB, rs1, '00000')
            muxY_byte_update = 0
            if funct3 == '000':
                # self.muxY.byte_update(1)
                muxY_byte_update = 1
            elif funct3 == '001':
                # self.muxY.byte_update(2)
                muxY_byte_update = 2
            elif funct3 == '010':
                # self.muxY.byte_update(4)
                muxY_byte_update = 4
            self.id_ex.update_load(rd, self.con_mux,muxY_byte_update, opcode)

        elif opcode == '1100111' and bin_int[17:20] == '000':  # jalr
            self.control_inst += 1
            rd = bin_int[20:25]
            rs1 = bin_int[12:17]
            imm = bin_int[0:12]
            imm1 = convert_to_hex_extend(imm)
            # self.muxINC.update(imm1, 1)
            muxINC_update = 1
            RA = self.reg1.obtain_RA()
            self.reg1.reg_extract(rd, self.muxA, self.muxB, '00000', '00000')
            self.con_mux['E'] = '0'
            self.con_mux['PC'] = '0'
            self.con_mux['INC'] = '1'
            self.con_mux['Y'] = '10'
            self.id_ex.update_jalr(self.con_mux, imm1, muxINC_update,opcode,self.if_id.prevpc,self.if_id.pc,RA,rd)

        elif opcode == '1101111':  # jal
            self.control_inst += 1
            rd = bin_int[20:25]
            imm = bin_int[0] + bin_int[12:20] + bin_int[11] + bin_int[1:11] + '0'  # msb is imm[0]
            imm = imm[1:]
            imm1 = convert_to_hex_extend(imm)
            # self.muxINC.update(imm1, 1)
            muxINC_update = 1
            self.reg1.reg_extract(rd, self.muxA, self.muxB, '00000', '00000')

            self.con_mux['E'] = '0'
            self.con_mux['INC'] = '1'
            self.con_mux['PC'] = '1'
            self.con_mux['Y'] = '10'
            self.id_ex.update_jal(self.con_mux, imm1,muxINC_update,opcode,self.if_id.prevpc,self.if_id.pc,rd)

        elif opcode == '0010111' or opcode == '0110111':  # U(auipc or lui)
            self.alu_inst += 1
            rd = bin_int[20:25]
            imm = bin_int[0:20] + '0' * 12
            imm1 = convert_to_hex_extend(imm)
            self.muxB.update(imm1, 1)
            # self.muxA.update(self.PC_temp, 1)
            self.muxA.update(self.if_id.prevpc,1)
            self.reg1.reg_extract(rd, self.muxA, self.muxB, '00000', '00000')
            self.con_mux['B'] = '1'
            self.con_mux['E'] = '1'
            self.con_mux['Y'] = '00'
            self.alu.con_update(self.control_ALU['+'])
            if opcode == '0010111':
                self.con_mux['A'] = '1'
            else:
                self.con_mux['A'] = '0'
            self.id_ex.update_auipc_lui(rd,self.con_mux,opcode)

        elif opcode == '1100011':  # SB format
            self.control_inst += 1
            funct3 = bin_int[17:20]
            rs1 = bin_int[12:17]
            rs2 = bin_int[7:12]
            imm = bin_int[0] + bin_int[24] + bin_int[1:7] + bin_int[20:24] + '0'
            imm = imm[1:]
            imm1 = convert_to_hex_extend(imm)
            # self.muxINC.update(imm1, 1)
            muxINC_update = 1
            self.reg1.reg_extract('00000', self.muxA, self.muxB, rs1, rs2)

            self.con_mux['A'] = '0'
            self.con_mux['E'] = '1'
            self.con_mux['B'] = '0'
            self.con_mux['Y'] = '11'

            if funct3 == '000':
                self.alu.con_update(self.control_ALU['='])
            elif funct3 == '001':
                self.alu.con_update(self.control_ALU['!='])
            elif funct3 == '101':
                self.alu.con_update(self.control_ALU['>='])
            elif funct3 == '100':
                self.alu.con_update(self.control_ALU['<'])
            self.id_ex.update_sb(self.con_mux, imm1, muxINC_update,opcode,self.if_id.prevpc,self.if_id.pc)

        elif opcode == '0100011':  # S format
            self.alu_inst += 1
            funct3 = bin_int[17:20]
            if funct3 == '011':
                print("Not supported instruction!")
                return 1
            rs1 = bin_int[12:17]  # For effective address
            rs2 = bin_int[7:12]   # value to be stored
            imm = bin_int[0:7] + bin_int[20:25]
            imm1 = convert_to_hex_extend(imm)
            self.muxB.update(imm1, 1)
            self.reg1.reg_extract('00000', self.muxA, self.muxB, rs1, rs2)
            # self.rm = self.muxB.in0
            rm = self.muxB.in0
            self.con_mux['A'] = '0'
            self.con_mux['B'] = '1'
            self.con_mux['E'] = '1'
            self.con_mux['Y'] = '01'
            self.alu.con_update(self.control_ALU['+'])
            muxY_byte_update = 0
            if funct3 == '000':
                # self.muxY.byte_update(1)
                # self.rm = '0x' + self.rm[10:]  WHY ??
                muxY_byte_update = 1
                rm = '0x' + rm[10:]
            elif funct3 == '001':
                # self.muxY.byte_update(2)
                # self.rm = '0x' + self.rm[8:]   WHY ??
                muxY_byte_update = 2
                rm = '0x' + rm[8:]
            elif funct3 == '010':
                # self.muxY.byte_update(4)       WHY NOT HERE ??
                muxY_byte_update = 4
            self.id_ex.update_S(self.con_mux,rm,muxY_byte_update,opcode)

    def execute(self):
        if self.id_ex.con_mux['E'] == '0':      # used in jal and jalr
            temp = self.id_ex.PC_temp
            PC_temp = self.id_ex.PC  # we need to store PC+4 in PC_temp for transfer as input to MuxY
            PC = ''
            if self.id_ex.opcode == '1101111':      # jal
                PC = temp  # PC set to original PC (i.e. before fetch stage incremented it by 4)
                length = 10 - len(PC)
                PC = PC[0:2] + '0' * length + PC[2:]
            if self.id_ex.opcode == '1100111':  # for jalr - PC set as RA
                RA = self.id_ex.RA
                self.muxPC.update(RA, 0)
                self.muxPC.control(self.id_ex.con_mux['PC'])
                PC = self.muxPC.out

            self.muxINC.update(self.id_ex.imm,1)
            self.muxINC.control(self.id_ex.con_mux['INC'])
            self.adder.in_update(PC, self.muxINC.out)
            self.adder.control(self.id_ex.opcode)
            self.muxPC.update(self.adder.out, 1)
            self.muxPC.control('1')
            self.PC = self.muxPC.out           # updated New PC
            self.ex_mem.branch(PC_temp,self.id_ex.rd)

        else:
            self.muxA.control(self.con_mux['A'])
            self.alu.in_update(self.muxA.out, '0')
            self.muxB.control(self.con_mux['B'])
            self.alu.in_update(self.muxB.out, '1')
            self.con_mux['INC'] = self.alu.control  # muxINC signal used in SB instructions
            self.rz = self.alu.out
            self.ex_mem.nonbranch_SB(self.con_mux,self.id_ex.opcode,self.id_ex.muxY_byte_update,
                                     self.id_ex.rm,self.id_ex.rd,self.id_ex.imm,self.id_ex.PC_temp)

    def mem_access(self):
        if self.ex_mem.con_mux['Y'] == '00':     # for R format, I format(ALU),auipc and lui instructions
            self.muxY.update(self.rz, 0)

        elif self.ex_mem.con_mux['Y'] == '01':  # for load and store instructions
            self.MAR = self.rz
            if self.ex_mem.opcode == '0000011':
                self.MDR = load_from_memory(self.MAR, self.ex_mem.muxY_byte_update,
                                            self.mem)  # obtains data at required memory address and stores it in MDR
            elif self.ex_mem.opcode == '0100011':
                self.MDR = self.ex_mem.rm
                store_to_memory(self.MAR, self.MDR, self.mem)  # MDR is restored to '0x00000000'
            self.muxY.update(self.MDR, 1)

        elif self.ex_mem.con_mux['Y'] == '10':  # for jal and jalr instructions
            self.muxY.update(self.ex_mem.PC_temp, 2)

        elif self.ex_mem.con_mux['Y'] == '11':  # for SB format instructions
            if self.ex_mem.con_mux['INC'] == '1':
                # self.execute('0')  # for branch instructions we require the working of both the alu units
                if self.ex_mem.opcode == '1100011':  # for SB instructions-we need to renew the old PC
                    PC = self.ex_mem.PC_temp
                    self.muxINC.update(self.ex_mem.imm, 1)
                    self.muxINC.control(self.ex_mem.con_mux['INC'])
                    self.adder.in_update(PC, self.muxINC.out)
                    self.adder.control(self.id_ex.opcode)
                    self.muxPC.update(self.adder.out, 1)
                    self.muxPC.control('1')
                    self.PC = self.muxPC.out  # updated New PC

            else:
                pass
            self.muxY.update(self.rz, 0)
        self.muxY.control(self.id_ex.con_mux['Y'])
        self.ry = self.muxY.out
        self.mem_wr.update(self.ex_mem.rd,self.ex_mem.opcode)

    def register_update(self):
        self.reg1.load(self.ry)
        # 0100011 - store, 1100011 - SB format
        if self.mem_wr.opcode == "0100011" or self.mem_wr.opcode == "1100011" or self.mem_wr.rd == '00000':
            pass
        else:
            pass

if __name__ == '__main__':
    # print(':::::::::::: Pipeline Execution ::::::::::::')
    start = phase3("Instruction_Memory.mc")
