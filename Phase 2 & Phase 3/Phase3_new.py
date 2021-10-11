class Regfile:
    def __init__(self):
        self.dcreg = {
            "00000": "0x00000000", "00001": "0x00000000", "00010": "0x7ffffff0", "00011": "0x10000000","00100": "0x00000000",
            "00101": "0x00000000", "00110": "0x00000000", "00111": "0x00000000", "01000": "0x00000000","01001": "0x00000000",
            "01010": "0x00000000", "01011": "0x00000000", "01100": "0x00000000", "01101": "0x00000000","01110": "0x00000000",
            "01111": "0x00000000", "10000": "0x00000000", "10001": "0x00000000", "10010": "0x00000000","10011": "0x00000000",
            "10100": "0x00000000", "10101": "0x00000000", "10110": "0x00000000", "10111": "0x00000000","11000": "0x00000000",
            "11001": "0x00000000", "11010": "0x00000000", "11011": "0x00000000", "11100": "0x00000000","11101": "0x00000000",
            "11110": "0x00000000", "11111": "0x00000000"}
        self.rs1 = "000000"
        self.rs2 = "000000"
        self.rd = "00000"
        self.wrline = "0x00000000"
        self.rdline1 = "0x00000000"
        self.rdline2 = "0x00000000"

    def reg_extract(self,rd,muxA,muxB, rs1, rs2):  # updates MUX A and B with the values req. from reg_file and makes regfile aware about rd
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.rdline1 = self.dcreg[rs1]
        self.rdline2 = self.dcreg[rs2]
        muxA.update(self.rdline1, 0)
        muxB.update(self.rdline2, 0)

    def reg_for_output(self, rd):
        self.rd = rd

    def obtain_RA(self):            # to quickly obtain value in x1
        return self.dcreg['00001']

    def load(self, inp):            # updates values in the regfile at required register
        self.wrline = inp
        if self.rd != '00000':
            self.dcreg[self.rd] = inp
        else:
            self.dcreg[self.rd] = "0x00000000"

class Mux:
    def __init__(self, in0, in1):
        self.in1 = in1
        self.in0 = in0
        self.out = '0x00000000'

    def update(self, inp, ln_no):       # updating inputs of the Mux
        if ln_no:
            self.in1 = inp
        else:
            self.in0 = inp

    def control(self, con_sig):         # evaluating output based on control line
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

    def update(self, inp, ln_no):# updating inputs of the Mux
        if ln_no==1:
            self.in1 = inp
        elif ln_no == 2:
            self.in2 = inp
        else:
            self.in0 = inp

    def byte_update(self, byte):  # self.byte stores no. of bytes to be stored or loaded from memory
        self.byte = byte

    def control(self, con_sig):     # evaluating output based on control line
        if con_sig == '00':
            self.out = self.in0
        elif con_sig == '01':
            self.out = self.in1
        elif con_sig == '10':
            self.out = self.in2

class Adder:                                # used for PC related hardware
    def __init__(self, in0, in1):
        self.in0 = in0
        self.in1 = in1
        self.out = '0x00000000'

    def in_update(self, inp0, inp1):        # updating inputs of the Adder
        self.in0 = inp0
        self.in1 = inp1

    def control_initial(self):          # called in fetch to add PC and 4. No need to check for -ve numbers.Output used for PC_next
        var1 = int(self.in1[2:], 16)
        var2 = int(self.in0[2:], 16)
        self.out = var1 + var2
        self.out = hex(self.out)        # no need to extend PC to 32 bits
    def control(self, opcode):      # inputs are 32 bit long but in hexadecimal...output(PC_next) need not be 32 bit long
        if self.in0[2] == 'f' or self.in0[2] == 'e' or self.in0[2] == 'd' or self.in0[2] == 'c' or self.in0[2] == 'b' or \
                self.in0[2] == 'a':     # checking if the input is negative(useful when backward branch needs to be taken)
            var1 = int(self.in0[2:], 16) - 2 ** 32
        else:
            var1 = int(self.in0[2:], 16)
        if self.in1[2] == 'f' or self.in1[2] == 'e' or self.in1[2] == 'd' or self.in1[2] == 'c' or self.in1[2] == 'b' or \
                self.in1[2] == 'a':      # checking if the input is negative(useful when backward branch needs to be taken)
            var2 = int(self.in1[2:], 16) - 2 ** 32
        else:
            var2 = int(self.in1[2:], 16)
        self.out = var1 + var2
        self.out = hex(self.out)

class ALU:
    def __init__(self, in0, in1):
        self.in1 = in1
        self.in0 = in0
        self.out = '0x00000000'

    def con_update(self, con_sig):      # updated control signal
        self.con = con_sig

    def in_update(self, inp, in_no):    # updates input
        if in_no == '0':
            self.in0 = inp
        else:
            self.in1 = inp

    def control(self):  # inputs are 32 bit in hexadecimal form and same is the output
        if self.in0[2] == 'f' or self.in0[2] == 'e' or self.in0[2] == 'd' or self.in0[2] == 'c' or self.in0[2] == 'b' or self.in0[2] == 'a' \
                or self.in0[2] == '9' or self.in0[2] == '8':    #check for -ve
            var1 = int(self.in0[2:], 16) - 2 ** 32
        else:
            var1 = int(self.in0[2:], 16)
        if self.in1[2] == 'f' or self.in1[2] == 'e' or self.in1[2] == 'd' or self.in1[2] == 'c' or self.in1[2] == 'b' or self.in1[2] == 'a'\
                or self.in1[2] == '9' or self.in1[2] == '8':    #check for -ve:
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
        elif self.con == '0101':    # no function in python to shift right logically so manually done
            str = bin(int(self.in0,16))
            str = str[0:2] + '0' * (34-len(str)) + str[2:]  # to make str 32 bits long with '0b' in start
            self.out = str[0:2] + '0' * var2 + str[2: 34 - var2]    # introducing req. 0 in front as well as ensuring output to be 32 bits
            self.out = int(self.out, 2)
        elif self.con == '0110':
            self.out = var1 - var2
        elif self.con == '0111':
            self.out = var1 ^ var2
        elif self.con == '1000':
            self.out = int(var1 / var2)     #division in python results in floating number
        elif self.con == '1001':
            self.out = var1 * var2
        elif self.con == '1010':
            self.out = var1 % var2
        elif self.con == '1011':    #slt instruction
            val = var1 - var2
            if val >= 0:
                self.out = '0x00000000'
            else:
                self.out = '0x00000001'
            return
        elif self.con == '1100':
            self.out = '0x00000000'
            if var1 == var2:
                return '1'
            else:
                return '0'
        elif self.con == '1101':
            self.out = '0x00000000'
            if var1 != var2:
                return '1'
            else:
                return '0'
        elif self.con == '1110':
            self.out = '0x00000000'
            if var1 >= var2:
                return '1'
            else:
                return '0'
        elif self.con == '1111':
            self.out = '0x00000000'
            if var1 < var2:
                return '1'
            else:
                return '0'
        if self.out<0: self.out+= 2 ** 32   # converting -ve num to +ve for conversion to hexadecimal
        self.out = hex(self.out)
        length = 10 - len(self.out)
        self.out = self.out[0:2] + '0' * length + self.out[2:]      # need to extend it to 32 bits

class Pip_F_ID():
    def __init__(self):
        self.pc_in ='0x0'
        self.ir_in ='0x00000000'
        self.pc_next_in ='0x4'
        self.pc_out = '0x0'
        self.ir_out = '0x00000000'
        self.pc_next_out = '0x4'
    def update(self,pc_next,pc_curr,ir):
        self.pc_in= pc_curr
        self.ir_in = ir
        self.pc_next_in= pc_next
    def update_in_to_out(self):
        self.pc_out = self.pc_in
        self.ir_out = self.ir_in
        self.pc_next_out = self.pc_next_in
    def print(self):
        print(self.pc_in,self.ir_in,self.pc_next_in,self.pc_out,self.ir_out,self.pc_next_out)

class Pip_ID_EX():
    def __init__(self):
        self.muxa_in = '0'
        self.muxb_in = '0'
        self.muxa1_in = '00'
        self.muxb1_in = '00'
        self.muxrz_in = '0'
        self.muxy_in = '00'
        self.alu_in ='0000'
        self.rd_in ='00000'
        self.opcode_in ='0000000'
        self.pc_in ='0x0'   # stores target pc for jal/jalr
        self.byte_in =0     # for load/store
        self.pc_temp_in ='0x0'  #stores PC+4 and used in jal/jalr
        self.muxrm_in ='0'
        self.muxm_in ='0'
        self.ra_in ='0x00000000'
        self.rb_in = '0x00000000'

        self.muxa_out = '0'
        self.muxb_out = '0'
        self.muxa1_out = '00'
        self.muxb1_out = '00'
        self.muxrz_out = '0'
        self.muxy_out = '00'
        self.alu_out = '0000'
        self.rd_out = '00000'
        self.opcode_out = '0000000'
        self.pc_out = '0x0'  # stores target pc for jal/jalr
        self.byte_out = 0  # for load/store
        self.pc_temp_out = '0x0'  # stores PC+4 and used in jal/jalr
        self.muxrm_out = '0'
        self.muxm_out = '0'
        self.ra_out = '0x00000000'
        self.rb_out = '0x00000000'
    def update_RIUSB(self,a,b,a1,b1,rz,y,alu,rd,opcode,pc):
        self.muxa_in = a
        self.muxb_in = b
        self.muxa1_in = a1
        self.muxb1_in = b1
        self.muxrz_in = rz
        self.muxy_in = y
        self.alu_in = alu
        self.rd_in = rd
        self.opcode_in = opcode
        self.pc_in = pc
        self.byte_in = 0
        self.pc_temp_in = '0x0'
        self.muxrm_in = '0'
        self.muxm_in = '0'

    def update_LS(self,a,b,a1,b1,rz,y,alu,rd,opcode,pc,byte,rm,m):
        self.update_RIUSB(a, b, a1, b1, rz, y, alu, rd, opcode, pc)
        self.byte_in=byte
        if self.opcode_in =='0100011':
            self.muxrm_in=rm
            self.muxm_in=m

    def update_JALJALR(self,pc,pc_temp,rd,rz,y,opcode):
        self.muxa_in = '0'
        self.muxb_in = '0'
        self.muxa1_in = '00'
        self.muxb1_in = '00'
        self.muxrz_in = rz
        self.muxy_in = y
        self.alu_in = '0000'
        self.rd_in = rd
        self.opcode_in = opcode
        self.pc_in = pc
        self.byte_in = 0  # for load/store
        self.pc_temp_in = pc_temp
        self.muxrm_in = '0'
        self.muxm_in = '0'

    def update_in_to_out(self):
        self.muxa_out = self.muxa_in
        self.muxb_out = self.muxb_in
        self.muxa1_out = self.muxa1_in
        self.muxb1_out = self.muxb1_in
        self.muxrz_out =self.muxrz_in
        self.muxy_out = self.muxy_in
        self.alu_out = self.alu_in
        self.rd_out = self.rd_in
        self.opcode_out = self.opcode_in
        self.pc_out = self.pc_in
        self.byte_out =  self.byte_in
        self.pc_temp_out = self.pc_temp_in
        self.muxrm_out =  self.muxrm_in
        self.muxm_out = self.muxm_in
        self.ra_out = self.ra_in
        self.rb_out = self.rb_in

    def print(self):
        print(self.muxa_in,self.muxb_in,self.muxa1_in,self.muxb1_in,self.muxrz_in,self.muxy_in,self.alu_in,self.rd_in,self.opcode_in,\
              self.pc_in ,self.byte_in,self.pc_temp_in,self.muxrm_in,self.muxm_in,self.ra_in,self.rb_in)
        print(self.muxa_out,self.muxb_out,self.muxa1_out,self.muxb1_out,self.muxrz_out,self.muxy_out,self.alu_out,self.rd_out,\
              self.opcode_out,self.pc_out ,self.byte_out,self.pc_temp_out,self.muxrm_out,self.muxm_out,self.ra_out,self.rb_out)

class Pip_EX_MA():
    def __init__(self):
        self.rz_in = '0x00000000'
        self.muxy_in = '00'
        self.rd_in = '00000'
        self.opcode_in = '0000000'
        self.pc_in = '0x0'
        self.byte_in = 0
        self.muxrm_in = '0'
        self.muxm_in = '0'
        self.rm_in='0x00000000'

        self.rz_out = '0x00000000'
        self.muxy_out = '00'
        self.rd_out = '00000'
        self.opcode_out = '0000000'
        self.pc_out = '0x0'
        self.byte_out = 0
        self.muxrm_out = '0'
        self.muxm_out = '0'
        self.rm_out = '0x00000000'
    def update(self,muxy,rd,opcode,pc,byte,muxrm,muxm,rm):
        self.muxy_in = muxy
        self.rd_in = rd
        self.opcode_in = opcode
        self.pc_in = pc
        self.byte_in = byte
        self.muxrm_in = muxrm
        self.muxm_in = muxm
        self.rm_in = rm

    def update_in_to_out(self):
        self.rz_out = self.rz_in
        self.muxy_out = self.muxy_in
        self.rd_out = self.rd_in
        self.opcode_out = self.opcode_in
        self.pc_out = self.pc_in
        self.byte_out = self.byte_in
        self.muxrm_out = self.muxrm_in
        self.muxm_out = self.muxm_in
        self.rm_out = self.rm_in

    def print(self):
        print(self.rz_in,self.muxy_in,self.rd_in,self.opcode_in,self.pc_in,self.byte_in,self.muxrm_in,self.muxm_in,self.rm_in)
        print(self.rz_out, self.muxy_out, self.rd_out, self.opcode_out, self.pc_out, self.byte_out, self.muxrm_out,
              self.muxm_out, self.rm_out)

class Pip_MA_WB():
    def __init__(self):
        self.ry_in  = '0x00000000'
        self.rd_in  = '00000'
        self.pc_in  = '0x0'
        self.ry_out = '0x00000000'
        self.rd_out = '00000'
        self.pc_out = '0x0'
    def update(self,rd,pc):
        self.rd_in  = rd
        self.pc_in  = pc
    def update_in_to_out(self):
        self.ry_out = self.ry_in
        self.rd_out = self.rd_in
        self.pc_out = self.pc_in

    def print(self):
        print(self.ry_in,self.rd_in,self.pc_in,self.ry_out,self.rd_out,self.pc_out)

def convert_binary_to_integer(imm, bits):
    if imm[2] == '1':
        imm = int(imm, 2) - 2 ** bits
    else:
        imm = int(imm, 2)
    return imm

def convert_to_hex_extend(imm): # immediate in binary
    if imm[0] == '1':
        imm = hex(int(imm, 2))  # need to extend it to 32 bits
        length = 10 - len(imm)
        imm = '0x' + 'f' * length + imm[2:]
    else:
        imm = hex(int(imm, 2))  # need to extend it to 32 bits
        length = 10 - len(imm)
        imm = imm[0:2] + '0' * length + imm[2:]
    #print(imm)
    return imm

def load_from_memory(MAR, byte, mem):  # MAR :address;byte:bytes to be loaded;mem:initial dictionary(memory) created
    check1 = 0
    check2 = 0

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

    if check1 == 0 and check2 == 0:
        ke1 = "00000000"  # if not present,then update in mem dict with initial values 0
        ke2 = "00000000"
        mem.update({adr1: ke1, adr2: ke2})
    elif check1 == 0 and check2 == 1:
        ke1 = "00000000"  # if one present and other not,update the one not present
        mem.update({adr1: ke1})
        ke2 = mem.get(adr2)
        ke2 = ke2 + '0' * (8 - len(ke2))  # making key value upto 32 bits(i.e. 8bytes),if not initially
        mem.update({adr2: ke2})
    elif check1 == 1 and check2 == 0:
        ke2 = "00000000"
        ke1 = mem.get(adr1)
        ke1 = ke1 + '0' * (8 - len(ke1))
        mem.update({adr1: ke1, adr2: ke2})
    elif check1 == 1 and check2 == 1:
        ke1 = mem.get(adr1)
        ke2 = mem.get(adr2)
        ke1 = ke1 + '0' * (8 - len(ke1))
        ke2 = ke2 + '0' * (8 - len(ke2))
        mem.update({adr1: ke1, adr2: ke2})

    tot = rem1 + byte  # tot=6
    MDR = ''
    if tot == 4:  # loadng of bytes
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

def store_to_memory(MAR, MDR, mem):  # MAR :address;MDR: data to be stored;mem:initial dictionary(memory) created
    check1 = 0  # store_value(0x10000011,2,20,data memory )
    check2 = 0
    s = ''
    tot = 0

    MDR = MDR.replace("0x", '')  # "14"
    byte = int(len(MDR) / 2)
    st_rev = ''
    for i in range(0, len(MDR), 2):
        s = MDR[i:i + 2]
        st_rev = s + st_rev

    b = int(MAR.replace("0x", ''),16)
    rem1 = b % 4  # 3
    rem2 = 4 - rem1  # 1
    adr1 = b - rem1  # 10000008
    adr2 = b + rem2  # 10000012
    adr1 = hex(adr1)  # "0x10000008"
    adr2 = hex(adr2)  # "0x10000012"
    if adr1 in mem.keys():
        check1 = 1  # checking both the address in mem deictionary
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
        ke2 = ke2 + '0' * (8 - len(ke2))  # making key value upto 32 bits(i.e. 8bytes),if not initially
        mem.update({adr2: ke2})
    elif check1 == 1 and check2 == 0:
        ke2 = "00000000"
        ke1 = mem.get(adr1)
        ke1 = ke1 + '0' * (8 - len(ke1))
        mem.update({adr1: ke1, adr2: ke2})
    elif check1 == 1 and check2 == 1:
        ke1 = mem.get(adr1)
        ke2 = mem.get(adr2)
        ke1 = ke1 + '0' * (8 - len(ke1))
        ke2 = ke2 + '0' * (8 - len(ke2))
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

class PhaseThree:

    def prep_hardware(self):
        # hardware initiation
        self.PC = '0x0'
        self.IR='0x00000000'
        self.RA = '0x00000000'
        self.adder = Adder(self.PC, '0x0004')
        self.adder.control_initial()

        self.PC_temp = self.PC

        # data path related hardware
        self.reg1 = Regfile()
        self.control_ALU = {'+': '0000', '&': '0001', '|': '0010', '<<': '0011', '>>>': '0100', '>>': '0101',
                            '-': '0110', '^': '0111', '/': '1000', '*': '1001',
                            '%': '1010', '--': '1011'}
        # dictionary containing control signals for all muxes
        self.con_mux = {'A': '0', 'B': '0', 'A1': '00', 'B1': '00', 'Y': "00", 'AH': '0', 'RZ': '0', 'PC': '0',
                        'RM': '0', 'M': '0'}

        # pipeline registers
        self.pr1 = Pip_F_ID()
        self.pr2 = Pip_ID_EX()
        self.pr3 = Pip_EX_MA()
        self.pr4 = Pip_MA_WB()

        self.muxB = Mux(self.pr2.rb_in , '0x00000000')  # first one selected when control line is '0'
        self.muxA = Mux(self.pr2.ra_in , self.PC)
        self.alu = ALU(self.muxA.out, self.muxB.out)
        self.pr3.rz_in  = self.alu.out

        self.rm = self.muxB.in0
        self.MDR = self.rm
        self.muxY = MuxY(self.pr3.rz_in , self.MDR, self.PC_temp)
        self.pr4.ry_in  = self.muxY.out
        self.reg1.load(self.pr4.ry_in )

        self.muxA1 = MuxY(self.muxA.out, self.pr3.rz_in , self.pr4.ry_in )
        self.muxB1 = MuxY(self.muxB.out, self.pr3.rz_in , self.pr4.ry_in )
        self.alu.in_update(self.muxA1.out, '0')
        self.alu.in_update(self.muxB1.out, '1')
        self.muxRZ = Mux(self.alu.out, '0x00000000')
        self.pr3.rz_in  = self.alu.out
        self.MAR = self.pr3.rz_in
        self.muxRM = Mux(self.pr2.rb_in , self.pr4.ry_in )
        self.rm = self.muxRM.out
        self.muxM = Mux(self.rm, self.pr4.ry_in )
        self.MDR = self.muxM.out

        self.list_PC = []
        self.ins_stage = {}
        self.ins_reg = {}
        self.BTB = {}
        self.total_ins=0
        self.data_transfer=0
        self.alu_ins=0
        self.control_ins=0
        self.stall=0


    def __init__(self, file,knob3,knob4,knob5):        # takes mc file as input
        self.prep_hardware()
        from memory import memory  # memory is a file in which memory is the dictionary finalised after Phase 1 .data has been read
        self.mem = memory  # self.mem is our data memory now
        f = open(file, 'r+')  # read and write (memory) both
        line_array = f.readlines()  # read the file until the last statement (ending one) arrives
        self.Ins_memory = {}  # this is the instruction memory
        self.clock = 0
        last_PC = '0x0'
        for line in line_array:  # loop to store instructions in the ins. memory and BTB to store predictions
            words = line.split()
            self.Ins_memory[words[0]] = words[1]
            if words[1] == '0xef000011' or words[1] == '0xEF000011': #save the last instruction PC to know when to exit
                last_PC = words[0]
            #BTB initialisation if control signal
            pc = words[0]
            IR = bin(int(words[1], 16))  # Calculating opcode
            length = 34 - len(IR)
            IR = IR[0:2] + '0' * length + IR[2:]
            IR = IR[2:]  # Binary starts with 0bxxxx....
            opcode = IR[25:]
            '''
                1. words[0] is the pc line address - key of dictionary
                2. First value of the dictionary is Target Address ( where it is pointing to )
                3. Second value of the dictionary is BHT ( branch history table )
                    # 0 - NT - branch not taken 
                    # 1 - T - branch taken
            '''
            if opcode == '1100011':  # SB format instruction
                self.BTB[pc]=[0,0]
                imm = IR[0] + IR[24] + IR[1:7] + IR[20:24] + '0'  # For calculating target address
                imm = imm[1:]
                imm = convert_to_hex_extend(imm)
                var1 = int(pc[2:], 16)
                if (imm[2] == 'f' or imm[2] == 'e' or imm[2] == 'd' or imm[2] == 'c' or
                        imm[2] == 'b' or imm[2] == 'a' or imm[2] == '9' or imm[2] == '8'):
                    var2 = int(imm[2:], 16) - 2 ** 32
                    self.BTB[pc][1] = 0
                else:
                    var2 = int(imm[2:], 16)
                    self.BTB[pc][1] = 1
                target_pc = var1 + var2
                target_pc = hex(target_pc)
                self.BTB[pc][0] = target_pc
            elif opcode == '1100111' and IR[17:20] == '000':  # jalr
                self.BTB[pc]= [0, 0, 0]
                imm = IR[0:12]
                imm = convert_to_hex_extend(imm)
                self.BTB[pc][2] = imm
                imm = hex(int(imm[2:], 16))
                self.BTB[pc][0] = imm  # x1(->0) + offset
                self.BTB[pc][1] = 1
            elif opcode == '1101111':  # jal
                self.BTB[pc]= [0, 0]
                imm = IR[0] + IR[12:20] + IR[11] + IR[1:11] + '0'  # msb is imm[0]
                imm = imm[1:]
                imm = convert_to_hex_extend(imm)
                var1 = int(pc[2:], 16)
                if (imm[2] == 'f' or imm[2] == 'e' or imm[2] == 'd' or imm[2] == 'c' or
                        imm[2] == 'b' or imm[2] == 'a' or imm[2] == '9' or imm[2] == '8'):
                    var2 = int(imm[2:], 16) - 2 ** 32
                else:
                    var2 = int(imm[2:], 16)
                target_pc = var1 + var2
                target_pc = hex(target_pc)
                self.BTB[pc][0] = target_pc
                self.BTB[pc][1] = 1

        # Pipeline_execution here------------------------------------------------------>
        if knob5!=0:
            search=hex(knob5*4)
        self.fetch()
        self.pr1.update_in_to_out()
        if knob3==1:
            print(self.reg1.dcreg)
        if knob4==1:
            self.pr1.print()
        self.clock=self.clock+1
        while bool(self.ins_stage):     #dictionary is not empty
            #print(self.ins_stage,self.PC)
            if 'WB' in self.ins_stage.values():
                self.register_update()
            if "MA" in self.ins_stage.values():
                self.mem_access()
            if 'E' in self.ins_stage.values():
                self.execute()
            if 'D' in self.ins_stage.values():
                self.decode()
            if 'F' in self.ins_stage.values():
                self.PC = self.pr1.pc_in
                self.stall=self.stall+1
            if self.PC != last_PC:
                self.fetch()
            self.clock = self.clock + 1
            # update pipeline registers from input to output
            if 'F' not in self.ins_stage.values():
                self.pr1.update_in_to_out()
            self.pr2.update_in_to_out()
            self.pr3.update_in_to_out()
            self.pr4.update_in_to_out()
            #print(self.ins_reg, self.clock)
            if knob3 == 1:
                print(self.reg1.dcreg)
            if knob4 == 1:
                self.pr1.print()
                self.pr2.print()
                self.pr3.print()
                self.pr4.print()
            if knob5!=0:
                if self.pr1.pc_out==search: self.pr1.print()
                if self.pr2.pc_out == search: self.pr2.print()
                if self.pr3.pc_out == search: self.pr3.print()
                if self.pr4.pc_out == search: self.pr4.print()
         #--------------------------------------------------------------------------------------->
        print("Stat 1:"+ self.clock)
        print("Stat 2:"+ self.total_ins)
        CPI=int(self.clock/self.total_ins)
        print("Stat 3:{}".format(CPI))
        print("Stat 4:" + self.data_transfer)
        print("Stat 5:"+ self.alu_ins)
        print("Stat 6:" + self.control_ins)
        print("Stat 7:"+ self.stall)
        #write data memory in the .mc file
        # l='\n\nData Memory :\n'
        # for key in list(self.mem):
        #     l = l + (key + ' : ' + self.mem[key] + '\n')
        # f.write(l)
        # f.close()

    def detect_data_hazard(self,ins_reg, PC_curr, PC_prev, PC_preprev):
        info_curr = ins_reg[PC_curr]
        info_prev = ins_reg[PC_prev]
        if PC_preprev in ins_reg: info_preprev = ins_reg[PC_preprev]
        else: info_preprev = ['0000000', '00000', '00000', '00000']

        if info_curr[0] == '1101111' or info_curr[0] == '0010111' or info_curr[0] == '0110111':  # UJ or U format-> without any control signal update
            return
        elif info_prev[0] == '1100011' or info_prev[0] == '0100011':  # prev_ins is S or SB format
            if info_preprev[0] == '1100011' or info_preprev[0] == '0100011' or info_preprev[0] == '0000000':  # preprev_ins is S or SB format or not in pipeline
                self.con_mux['A1'] = '0'
                self.con_mux['B1'] = '0'
                self.con_mux['RM'] = '0'
                self.con_mux['M'] = '0'
                self.ins_stage[PC_curr] = 'E'
                return
            else:
                if info_curr[0] == '0110011' or info_curr[0] == '1100011':  # curr_ins is R,SB format
                    self.cmp_pre_R_SB(info_curr[0], info_curr[2], info_preprev, 0)
                    self.cmp_pre_R_SB(info_curr[0], info_curr[3], info_preprev, 1)
                elif info_curr[0] == '0100011':  # S format
                    self.cmp_pre_S(info_curr[0], info_curr[3], info_preprev, 0)
                    self.cmp_pre_S(info_curr[0], info_curr[2], info_preprev, 1)
                elif info_curr[0] == '1100111':  # jalr
                    self.cmp_pre_R_SB(info_curr[0], info_curr[2], info_preprev, 0)
                else:  # addi,load
                    self.cmp_pre_R_SB(info_curr[0], info_curr[2], info_preprev, 0)
                return
        elif info_preprev[0] == '1100011' or info_preprev[0] == '0100011' or info_preprev[0] == '0000000':
              # preprev_ins is S or SB format or not in pipeline
            if info_curr[0] == '0110011' or info_curr[0] == '1100011':  # curr_ins is R,SB format
                self.cmp_R_SB(info_curr[0], info_curr[2], info_prev, 0)
                self.cmp_R_SB(info_curr[0], info_curr[3], info_prev, 1)
            elif info_curr[0] == '0100011':  # S format
                self.cmp_S(info_curr[0], info_curr[2], info_prev, 1)
                self.cmp_S(info_curr[0], info_curr[3], info_prev, 0)
            elif info_curr[0] == '1100111':  # jalr
                self.cmp_R_SB(info_curr[0], info_curr[2], info_prev, 0)
            else:  # addi,load
                self.cmp_R_SB(info_curr[0], info_curr[2], info_prev, 0)
            return
        else:
            if info_curr[0] == '0110011' or info_curr[0] == '1100011':  # curr_ins is R format
                self.cmp_both_R_SB(info_curr[0], info_curr[2], info_prev, info_preprev, 0)
                if self.ins_stage[PC_curr]=='E':
                    self.cmp_both_R_SB(info_curr[0], info_curr[3], info_prev, info_preprev, 1)
            elif info_curr[0] == '1100011':  # curr_ins is SB format
                if info_curr[2] == info_prev[1]:
                    self.cmp_both_R_SB(info_curr[0], info_curr[2], info_prev, info_preprev, 0)
                elif info_curr[3] == info_prev[1]:
                    self.cmp_both_R_SB(info_curr[0], info_curr[3], info_prev, info_preprev, 1)
                else:
                    self.cmp_both_R_SB(info_curr[0], info_curr[2], info_prev, info_preprev, 0)
                    self.cmp_both_R_SB(info_curr[0], info_curr[3], info_prev, info_preprev, 1)
            elif info_curr[0] == '0100011':
                self.cmp_both_S(info_curr[0], info_curr[2], info_prev, info_preprev, 1)
                self.cmp_both_S(info_curr[0], info_curr[3], info_prev, info_preprev, 0)
            elif info_curr[0] == '1100111':  # jalr
                self.cmp_both_R_SB(info_curr[0], info_curr[2], info_prev, info_preprev, 0)
            else:
                self.cmp_both_R_SB(info_curr[0], info_curr[2], info_prev, info_preprev, 0)
            return

    def cmp_pre_R_SB(self,opcode, reg, info, a):
        if reg != info[1] or reg == '00000':
            self.con_mux['A1'] = '00'
            self.con_mux['B1'] = '00'
            self.con_mux['RM'] = '0'
            self.con_mux['M'] = '0'
            self.ins_stage[self.pr1.pc_out] = 'E'
        elif opcode == '1100011' or opcode == '1100111':  # SB,jalr ins.
            if info[0] == '0000011':
                if self.pr4.pc_out == info[0]:
                    if a == 1:
                        self.con_mux['B1'] = '10'
                    elif a == 0:
                        self.con_mux['A1'] = '10'
                    self.ins_stage[self.pr1.pc_out]='E'
                else:
                    self.ins_stage[self.pr1.pc_out] = 'D'
                    # data hazard stall
            else:
                if self.pr3.pc_out == info[0]:
                    if a == 1:
                        self.con_mux['B1'] = '01'
                    elif a == 0:
                        self.con_mux['A1'] = '01'
                    self.ins_stage[self.pr1.pc_out] = 'E'
        else:  # R and other ins.
            # use M-E forwarding path
            if self.pr4.pc_out == info[0]:
                if a == 1:
                    self.con_mux['B1'] = '10'
                elif a == 0:
                    self.con_mux['A1'] = '10'
                self.ins_stage[self.pr1.pc_out] = 'E'
        return

    def cmp_pre_S(self,opcode, reg, info, a):
        if reg != info[1] or reg == '00000':
            self.con_mux['A1'] = '00'
            self.con_mux['B1'] = '00'
            self.con_mux['RM'] = '0'
            self.con_mux['M'] = '0'
            self.ins_stage[self.pr1.pc_out] = 'E'
            return
        else:
            if a == 1 and self.pr4.pc_in== info[0]:
                self.con_mux['RM'] = '1'
                self.con_mux['M'] = '0'
            elif a == 0 and self.pr4.pc_in == info[0]:
                self.con_mux['A1'] = '10'
            self.ins_stage[self.pr1.pc_out] = 'E'

    def cmp_R_SB(self,opcode, reg, info, a):
        if reg != info[1] or reg == '00000':
            self.con_mux['A1'] = '00'
            self.con_mux['B1'] = '00'
            self.con_mux['RM'] = '0'
            self.con_mux['M'] = '0'
            self.ins_stage[self.pr1.pc_out] = 'E'
            return
        elif opcode == '1100011' or opcode == '1100111':
            if info[0] == '0000011':
                if self.pr4.pc_out == info[0]:
                    if a == 1:
                        self.con_mux['B1'] = '10'
                    elif a == 0:
                        self.con_mux['A1'] = '10'
                    self.ins_stage[self.pr1.pc_out] = 'E'
                else:
                    self.ins_stage[self.pr1.pc_out] = 'D'
                    # data hazard stall------> 2 stalls taken then read from reg. file
            else:
                if self.pr3.pc_out == info[0]:
                    if a == 1:
                        self.con_mux['B1'] = '01'
                    elif a == 0:
                        self.con_mux['A1'] = '01'
                    self.ins_stage[self.pr1.pc_out] = 'E'
                else:
                    self.ins_stage[self.pr1.pc_out] = 'D'
                #  need to stall----> 1 time
        else:  # R and other ins.
            if info[0] != '0000011':  # use E-E forwarding path
                if self.pr3.pc_in == info[0]:
                    if a == 1:
                        self.con_mux['B1'] = '01'
                    elif a == 0:
                        self.con_mux['A1'] = '01'
                    self.ins_stage[self.pr1.pc_out] = 'E'
            else:  # use M-E after stall
                if self.pr4.pc_in == info[0]:
                    if a == 1:
                        self.con_mux['B1'] = '10'
                    elif a == 0:
                        self.con_mux['A1'] = '10'
                    self.ins_stage[self.pr1.pc_out] = 'E'
                else:
                    self.ins_stage[self.pr1.pc_out] = 'D'
                #  need to stall----> 1 time
        return

    def cmp_S(self,opcode, reg, info, a):
        if reg != info[1] or reg == '00000':
            self.con_mux['A1'] = '00'
            self.con_mux['B1'] = '00'
            self.con_mux['RM'] = '0'
            self.con_mux['M'] = '0'
            self.ins_stage[self.pr1.pc_out] = 'E'
            return
        else:
            if a == 1 and (self.pr3.pc_in == info[0] or (self.ins_stage[self.pr3.pc_out]==opcode and self.pr4.pc_in == info[0])):
                self.con_mux['RM'] = '0'
                self.con_mux['M'] = '1'
                self.ins_stage[self.pr1.pc_out] = 'E'
            elif a == 0:
                if info[0] != '0000011':  # use E-E forwarding path
                    if self.pr3.pc_in == info[0]: self.con_mux['A1'] = '01'
                    self.ins_stage[self.pr1.pc_out] = 'E'
                else:  # use M-E after stall
                    if self.pr4.pc_in == info[0]:
                        self.con_mux['A1'] = '10'
                        self.ins_stage[self.pr1.pc_out] = 'E'
                    else:
                        self.ins_stage[self.pr1.pc_out] = 'D'

    def cmp_both_S(self,opcode, rs, info_prev, info_preprev, a):
        if (rs != info_prev[1] and rs != info_preprev[1]) or rs == '00000':
            self.con_mux['A1'] = '0'
            self.con_mux['B1'] = '0'
            self.con_mux['RM'] = '0'
            self.con_mux['M'] = '0'
            self.ins_stage[self.pr1.pc_out] = 'E'
            return
        elif rs == info_prev[1]:
            if a == 1 and (self.pr3.pc_in == info_prev[0] or (self.ins_stage[self.pr3.pc_out]==opcode and self.pr4.pc_in == info_prev[0])):
                self.con_mux['RM'] = '0'
                self.con_mux['M'] = '1'
                self.ins_stage[self.pr1.pc_out] = 'E'
            elif a == 0:
                if info_prev[0] != '0000011':  # use E-E forwarding path
                    if self.pr3.pc_in == info_prev[0]: self.con_mux['A1'] = '01'
                    self.ins_stage[self.pr1.pc_out] = 'E'
                else:  # use M-E after stall
                    if self.pr4.pc_in == info_prev[0]:
                        self.con_mux['A1'] = '10'
                        self.ins_stage[self.pr1.pc_out] = 'E'
                    else:
                        self.ins_stage[self.pr1.pc_out] = 'D'
        elif rs == info_preprev[0]:
            if a == 1 and self.pr4.pc_in == info_preprev[0]:
                self.con_mux['RM'] = '1'
                self.con_mux['M'] = '0'
            elif a == 0 and self.pr4.pc_in == info_preprev[0]:
                self.con_mux['A1'] = '10'
            self.ins_stage[self.pr1.pc_out] = 'E'

    def cmp_both_R_SB(self,opcode, rs, info_prev, info_preprev, a):
        if (rs != info_prev[1] and rs != info_preprev[1]) or rs == '00000':
            self.con_mux['A1'] = '0'
            self.con_mux['B1'] = '0'
            self.con_mux['RM'] = '0'
            self.con_mux['M'] = '0'
            self.ins_stage[self.pr1.pc_out] = 'E'
            return
        elif opcode == '1100011' or opcode == '1100111':  # SB,jalr ins.
            if rs == info_prev[1]:
                if info_prev[0] == '0000011':
                    if self.pr4.pc_out == info_prev[0]:
                        if a == 1:
                            self.con_mux['B1'] = '10'
                        elif a == 0:
                            self.con_mux['A1'] = '10'
                        self.ins_stage[self.pr1.pc_out] = 'E'
                    else:
                        self.ins_stage[self.pr1.pc_out] = 'D'
                        return 1
                # need to stall------> 2 stalls taken then read from reg. file
                else:
                    if self.pr3.pc_out == info_prev[0]:
                        if a == 1:
                            self.con_mux['B1'] = '01'
                        elif a == 0:
                            self.con_mux['A1'] = '01'
                        self.ins_stage[self.pr1.pc_out] = 'E'
                    else:
                        self.ins_stage[self.pr1.pc_out] = 'D'
                #  need to stall----> 1 time
            elif rs == info_preprev[1]:
                if info_preprev[0] == '0000011':
                    if self.pr4.pc_out == info_preprev[0]:
                        if a == 1:
                            self.con_mux['B1'] = '10'
                        elif a == 0:
                            self.con_mux['A1'] = '10'
                        self.ins_stage[self.pr1.pc_out] = 'E'
                    else: # need to stall
                        self.ins_stage[self.pr1.pc_out] = 'D'
                else:
                    if self.pr3.pc_out == info_preprev[0]:
                        if a == 1:
                            self.con_mux['B1'] = '01'
                        elif a == 0:
                            self.con_mux['A1'] = '01'
                        self.ins_stage[self.pr1.pc_out] = 'E'
        else:  # R and other ins.
            if rs == info_prev[1]:
                if info_prev[0] != '0000011':  # use E-E forwarding path
                    if self.pr3.pc_in == info_prev[0]:
                        if a == 1:
                            self.con_mux['B1'] = '01'
                        elif a == 0:
                            self.con_mux['A1'] = '01'
                        self.ins_stage[self.pr1.pc_out] = 'E'
                else:  # use M-E after stall
                    if self.pr4.pc_in == info_prev[0]:
                        if a == 1:
                            self.con_mux['B1'] = '10'
                        elif a == 0:
                            self.con_mux['A1'] = '10'
                        self.ins_stage[self.pr1.pc_out] = 'E'
                    else:
                        self.ins_stage[self.pr1.pc_out] = 'D'
                    #  need to stall----> 1 time
            elif rs == info_preprev[1]:
                # use M-E forwarding path
                if self.pr4.pc_in == info_preprev[0]:
                    if a == 1:
                        self.con_mux['B1'] = '10'
                    elif a == 0:
                        self.con_mux['A1'] = '10'
                    self.ins_stage[self.pr1.pc_out] = 'E'
            return

    def fetch(self):
        self.list_PC.append(self.PC)
        if (self.pr2.pc_in in self.ins_stage) and self.ins_stage[self.pr2.pc_in] == 'D': self.ins_stage[self.PC] = 'F'
        else: self.ins_stage[self.PC] = 'D'
        self.PC_temp = self.PC
        self.IR = self.Ins_memory[self.PC]

        self.IR = bin(int(self.IR, 16))  # converts IR into binary and extend to 32 bits
        length = 34 - len(self.IR)
        self.IR = self.IR[0:2] + '0' * length + self.IR[2:]

        # following steps update PC->PC + 4
        self.adder.in_update(self.PC, '0x0004')
        self.adder.control_initial()
        self.PC = self.adder.out

        self.pr1.update(self.PC, self.PC_temp, self.IR)
        # branch prediction
        if (self.IR[27:] == '1100011' and self.BTB[self.pr1.pc_in][1] == 1) or self.IR[27:] == '1101111' or self.IR[27:] == '1100111':
            self.PC = self.BTB[self.pr1.pc_in][0]

    def decode(self):
        bin_int = self.pr1.ir_out[2:]
        opcode = bin_int[25:]

        if opcode == '0110011':  # R format
            funct3 = bin_int[17:20]
            rd = bin_int[20:25]
            rs1 = bin_int[12:17]
            rs2 = bin_int[7:12]
            funct7 = bin_int[0:7]
            self.alu_ins=self.alu_ins+1

            # generate related control signals for all hardware
            self.con_mux['A'] = '0'
            self.con_mux['B'] = '0'
            self.con_mux['Y'] = '0'
            self.con_mux['RZ'] = '0'

            self.reg1.reg_extract(rd, self.muxA, self.muxB, rs1, rs2)
            self.pr2.ra_in = self.reg1.rdline1
            self.pr2.rb_in = self.reg1.rdline2

            if funct3 == '000' and funct7 == '0000000':con = self.control_ALU['+']
            elif funct3 == '111' and funct7 == '0000000': con = self.control_ALU['&']
            elif funct3 == '110' and funct7 == '0000000': con = self.control_ALU['|']
            elif funct3 == '001' and funct7 == '0000000': con = self.control_ALU['<<']
            elif funct3 == '010' and funct7 == '0000000': con = self.control_ALU['--']
            elif funct3 == '101' and funct7 == '0100000': con = self.control_ALU['>>>']
            elif funct3 == '101' and funct7 == '0000000': con = self.control_ALU['>>']
            elif funct3 == '000' and funct7 == '0100000': con = self.control_ALU['-']
            elif funct3 == '100' and funct7 == "0000000": con = self.control_ALU['^']
            elif funct3 == '000' and funct7 == '0000001': con = self.control_ALU['*']
            elif funct3 == '100' and funct7 == '0000001': con = self.control_ALU['/']
            elif funct3 == '110' and funct7 == '0000001': con = self.control_ALU['%']

            # send info to hazard detection unit and fill details in the pipeline register ID_EX
            self.ins_reg[self.pr1.pc_out] = [opcode, rd, rs1, rs2]
            if len(self.list_PC) > 2:
                self.detect_data_hazard(self.ins_reg, self.pr1.pc_out, self.list_PC[-2], self.list_PC[-3])
            elif len(self.list_PC) == 2:
                self.detect_data_hazard(self.ins_reg, self.pr1.pc_out, self.list_PC[-2], '0xffffffff')
            else:
                self.ins_stage[self.pr1.pc_out] = 'E'
            # con_mux a1 and b1 depend on it---------------------------> not possible if P(i-2) not in pipeline
            self.pr2.update_RIUSB(self.con_mux['A'], self.con_mux['B'], self.con_mux['A1'], self.con_mux['B1'],
                                  self.con_mux['RZ'],self.con_mux['Y'], con, rd, opcode, self.pr1.pc_out)
        elif opcode == '0010011':  # I format-andi,addi,ori
            funct3 = bin_int[17:20]
            rd = bin_int[20:25]
            rs1 = bin_int[12:17]
            imm = bin_int[0:12]
            imm1 = convert_to_hex_extend(imm)
            self.alu_ins = self.alu_ins + 1

            self.con_mux['A'] = '0'
            self.con_mux['B'] = '1'
            self.con_mux['Y'] = '0'
            self.con_mux['RZ'] = '0'

            self.muxB.update(imm1, 1)
            self.reg1.reg_extract(rd, self.muxA, self.muxB, rs1, '00000')
            self.pr2.ra_in = self.reg1.rdline1
            self.pr2.rb_in = self.reg1.rdline2  # 0 gets stored

            if funct3 == '000':
                con = self.control_ALU['+']
            elif funct3 == '111':
                con = self.control_ALU['&']
            elif funct3 == '110':
                con = self.control_ALU['|']

            # fill details in the pipeline register ID_EX and send info to hazard detection unit
            self.ins_reg[self.pr1.pc_out] = [opcode, rd, rs1, '00000']
            if len(self.list_PC) > 2:
                self.detect_data_hazard(self.ins_reg, self.pr1.pc_out, self.list_PC[-2], self.list_PC[-3])
            elif len(self.list_PC) == 2:
                self.detect_data_hazard(self.ins_reg, self.pr1.pc_out, self.list_PC[-2], '0xffffffff')
            else: self.ins_stage[self.pr1.pc_out] = 'E'
                # con_mux a1 depend on it------------------------>
            self.pr2.update_RIUSB(self.con_mux['A'], self.con_mux['B'], self.con_mux['A1'], '0', self.con_mux['RZ'],
                                  self.con_mux['Y'], con, rd, opcode, self.pr1.pc_out)
        elif opcode == '0000011':  # load instructions
            funct3 = bin_int[17:20]
            self.data_transfer = self.data_transfer + 1
            if funct3 == '011':
                print("Not supported instruction!")
                return 1
            rd = bin_int[20:25]
            rs1 = bin_int[12:17]
            imm = bin_int[0:12]
            imm1 = convert_to_hex_extend(imm)
            self.con_mux['A'] = '0'
            self.con_mux['B'] = '1'
            self.con_mux['Y'] = '1'
            self.con_mux['RZ'] = '0'
            con = self.control_ALU['+']

            self.muxB.update(imm1, 1)
            self.reg1.reg_extract(rd, self.muxA, self.muxB, rs1, '00000')
            self.pr2.ra_in = self.reg1.rdline1
            self.pr2.rb_in = self.reg1.rdline2
            if funct3 == '000': byte = 1
            elif funct3 == '001': byte = 2
            elif funct3 == '010': byte = 4
            # fill details in the pipeline register ID_EX and send info to hazard detection unit
            self.ins_reg[self.pr1.pc_out] = [opcode, rd, rs1, '00000']
            if len(self.list_PC) > 2:
                self.detect_data_hazard(self.ins_reg, self.pr1.pc_out, self.list_PC[-2], self.list_PC[-3])
            elif len(self.list_PC) == 2:
                self.detect_data_hazard(self.ins_reg, self.pr1.pc_out, self.list_PC[-2], '0xffffffff')
            else:
                self.ins_stage[self.pr1.pc_out] = 'E'
            self.pr2.update_LS(self.con_mux['A'], self.con_mux['B'], self.con_mux['A1'], '0', self.con_mux['RZ'],
                               self.con_mux['Y'], con, rd, opcode, self.pr1.pc_out, byte, '0', '0')
        elif opcode == '1100111' and bin_int[17:20] == '000':  # jalr
            rd = bin_int[20:25]
            rs1 = bin_int[12:17]
            self.control_ins = self.control_ins + 1

            self.reg1.reg_extract(rd, self.muxA, self.muxB, '00000', '00000')
            self.pr2.ra_in  = self.reg1.rdline1
            self.pr2.rb_in  = self.reg1.rdline2

            self.con_mux['Y'] = '0'
            self.con_mux['AH'] = '100'
            self.con_mux['RZ'] = '1'

            # fill details in the pipeline register ID_EX and send info to hazard detection unit
            self.ins_reg[self.pr1.pc_out] = [opcode, rd, rs1, '00000']
            if len(self.list_PC) > 2:
                self.detect_data_hazard(self.ins_reg, self.pr1.pc_out, self.list_PC[-2], self.list_PC[-3])
            elif len(self.list_PC) == 2:
                self.detect_data_hazard(self.ins_reg, self.pr1.pc_out, self.list_PC[-2], '0xffffffff')
            else:
                self.ins_stage[self.pr1.pc_out] = 'E'
            # muxa1 dependence as ALU input line 0 taken input to addn hardware
            # ---------->flush out curr ins. in fetch if path not taken through regfile
            # resolve branch to get target pc ----> call addn hardware giving inputs as ALU input line 0 and offset(self.BTB[self.pr1.pc][2])
            # ---->set self.PC if required
            if self.con_mux['A1']=='01':
                # flush out current ins. in fetch stage
                input1 = int(self.muxA1.in1,16)
                input2 = int(self.BTB[self.pr1.pc_out][2],16)
                self.PC = hex(input1+input2)
            elif self.con_mux['A1'] == '10':
                # flush out current ins. in fetch stage
                input1 = int(self.muxA1.in2,16)
                input2 = int(self.BTB[self.pr1.pc_out][2], 16)
                self.PC = hex(input1 + input2)
            else: # branch prediction is correct
                pass
            self.pr2.update_JALJALR(self.pr1.pc_out, self.pr1.pc_next_out, rd, self.con_mux['RZ'], self.con_mux['Y'], opcode)
        elif opcode == '1101111':  # jal
            rd = bin_int[20:25]
            self.control_ins = self.control_ins + 1
            self.reg1.reg_extract(rd, self.muxA, self.muxB, '00000', '00000')
            self.pr2.ra_in = self.reg1.rdline1
            self.pr2.rb_in = self.reg1.rdline2
            self.con_mux['Y'] = '0'
            self.con_mux['RZ'] = '1'
            # fill details in the pipeline register ID_EX and send info to hazard detection unit
            self.ins_reg[self.pr1.pc_out] = [opcode, rd, '00000', '00000']
            self.ins_stage[self.pr1.pc_out] = 'E'
            self.pr2.update_JALJALR(self.pr1.pc_out, self.pr1.pc_next_out, rd, self.con_mux['RZ'], self.con_mux['Y'], opcode)
        elif opcode == '0010111' or opcode == '0110111':  # U(auipc or lui)
            rd = bin_int[20:25]
            self.alu_ins = self.alu_ins + 1
            imm = bin_int[0:20] + '0' * 12
            imm1 = convert_to_hex_extend(imm)
            self.muxB.update(imm1, 1)
            self.muxA.update(self.pr1.pc_out, 1)
            self.reg1.reg_extract(rd, self.muxA, self.muxB, '00000', '00000')
            self.pr2.ra_in  = self.reg1.rdline1
            self.pr2.rb_in  = self.reg1.rdline2

            self.con_mux['B'] = '1'
            self.con_mux['Y'] = '0'
            self.con_mux['RZ'] = '0'
            con = self.control_ALU['+']

            if opcode == '0010111':
                self.con_mux['A'] = '1'
            else:
                self.con_mux['A'] = '0'
            # fill details in the pipeline register ID_EX and send info to hazard detection unit
            self.ins_reg[self.pr1.pc_out] = [opcode, rd, '00000', '00000']
            self.ins_stage[self.pr2.pc_out] = 'E'
            self.pr2.update_RIUSB(self.con_mux['A'], self.con_mux['B'], '0', '0', self.con_mux['RZ'], self.con_mux['Y'],
                                  con, rd, opcode, self.pr1.pc_out)
        elif opcode == '1100011':  # SB format
            funct3 = bin_int[17:20]
            rs1 = bin_int[12:17]
            rs2 = bin_int[7:12]
            self.control_ins = self.control_ins + 1

            self.reg1.reg_extract('00000', self.muxA, self.muxB, rs1, rs2)
            self.pr2.ra_in = self.reg1.rdline1
            self.pr2.rb_in = self.reg1.rdline2

            self.con_mux['A'] = '0'
            self.con_mux['B'] = '0'
            self.con_mux['Y'] = '0'
            self.con_mux['RZ'] = '1'

            # fill details in the pipeline register ID_EX and send info to hazard detection unit
            self.ins_reg[self.pr1.pc_out] = [opcode, '00000', rs1, rs2]
            if len(self.list_PC) > 2:
                self.detect_data_hazard(self.ins_reg, self.pr1.pc_out, self.list_PC[-2], self.list_PC[-3])
            elif len(self.list_PC) == 2:
                self.detect_data_hazard(self.ins_reg, self.pr1.pc_out, self.list_PC[-2], '0xffffffff')
            else:
                self.ins_stage[self.pr2.pc_out] = 'E'
            # resolve branch ----------> give inputs as ALU inputs and after it calculates the result
            # if pred. wrong self.PC and self.BTB[self.pr1.pc][1]corrected------------> stores '0x00000000' in self.pr2.pc_temp
            self.muxA.control(self.con_mux['A'])
            self.muxA1.update(self.muxA.out, 0)
            self.muxA1.control(self.con_mux['A1'])
            input1 = self.muxA1.out

            self.muxB.control(self.con_mux['B'])
            self.muxB1.update(self.muxB.out, 0)
            self.muxB1.control(self.con_mux['B1'])
            input2 = self.muxB1.out

            if self.ins_stage[self.pr1.pc_out] == 'E':
                if funct3 == '000':
                    if input1==input2 and self.BTB[self.pr1.pc_out][1]==0:
                        # control hazard and branch misprediction----> increment here
                        self.PC = self.BTB[self.pr1.pc_out][0]
                        self.BTB[self.pr1.pc_out][1]=1
                    elif input1!=input2 and self.BTB[self.pr1.pc_out][1]==1:
                        # control hazard and branch misprediction----> increment here
                        self.PC = self.pr1.pc_next_out
                        self.BTB[self.pr1.pc_out][1] = 0
                elif funct3 == '001':
                    if input1!=input2 and self.BTB[self.pr1.pc_out][1]==0:
                        # control hazard and branch misprediction----> increment here
                        self.PC = self.BTB[self.pr1.pc_out][0]
                        self.BTB[self.pr1.pc_out][1]=1
                    elif input1==input2 and self.BTB[self.pr1.pc_out][1]==1:
                        # control hazard and branch misprediction----> increment here
                        self.PC = self.pr1.pc_next_out
                        self.BTB[self.pr1.pc_out][1] = 0
                elif funct3 == '101':
                    if input1>=input2 and self.BTB[self.pr1.pc_out][1]==0:
                        # control hazard and branch misprediction----> increment here
                        self.PC = self.BTB[self.pr1.pc_out][0]
                        self.BTB[self.pr1.pc_out][1]=1
                    elif input1<input2 and self.BTB[self.pr1.pc_out][1]==1:
                        # control hazard and branch misprediction----> increment here
                        self.PC = self.pr1.pc_next_out
                        self.BTB[self.pr1.pc_out][1] = 0
                elif funct3 == '100':
                    if input1<input2 and self.BTB[self.pr1.pc_out][1]==0:
                        # control hazard and branch misprediction----> increment here
                        self.PC = self.BTB[self.pr1.pc_out][0]
                        self.BTB[self.pr1.pc_out][1]=1
                    elif input1>=input2 and self.BTB[self.pr1.pc_out][1]==1:
                        # control hazard and branch misprediction----> increment here
                        self.PC = self.pr1.pc_next_out
                        self.BTB[self.pr1.pc_out][1] = 0
            self.pr2.update_RIUSB('0', '0', '0', '0', self.con_mux['RZ'], self.con_mux['Y'], '0000', '00000', opcode,
                                  self.pr1.pc_out)
        elif opcode == '0100011':  # S format
            funct3 = bin_int[17:20]
            self.data_transfer = self.data_transfer + 1
            if funct3 == '011':
                print("Not supported instruction!")
                return 1
            rs2 = bin_int[12:17]
            rs1 = bin_int[7:12]  # value to be stored
            imm = bin_int[0:7] + bin_int[20:25]
            imm1 = convert_to_hex_extend(imm)

            self.muxB.update(imm1, 1)
            self.reg1.reg_extract('00000', self.muxA, self.muxB, rs2, rs1)
            self.pr2.ra_in = self.reg1.rdline1
            self.pr2.rb_in = self.reg1.rdline2

            self.con_mux['A'] = '0'
            self.con_mux['B'] = '1'
            self.con_mux['Y'] = '1'
            self.con_mux['RZ'] = '0'
            con = self.control_ALU['+']

            if funct3 == '000': byte = 1
            elif funct3 == '001': byte = 2
            elif funct3 == '010': byte = 4

            # fill details in the pipeline register ID_EX and send info to hazard detection unit
            self.ins_reg[self.pr1.pc_out] = [opcode, '00000', rs2, rs1]
            if len(self.list_PC) > 2:
                self.detect_data_hazard(self.ins_reg, self.pr1.pc_out, self.list_PC[-2], self.list_PC[-3])
            elif len(self.list_PC) == 2:
                self.detect_data_hazard(self.ins_reg, self.pr1.pc_out, self.list_PC[-2], '0xffffffff')
            else:
                self.ins_stage[self.pr1.pc_out] = 'E'  # sets rm,m for rs1, a for rs2
            self.pr2.update_LS(self.con_mux['A'], self.con_mux['B'], self.con_mux['A1'], '0', self.con_mux['RZ'],
                               self.con_mux['Y'], con, '00000', opcode, self.pr1.pc_out, byte, self.con_mux['RM'],
                               self.con_mux['M'])

    def execute(self):
        self.muxA.control(self.pr2.muxa_out)
        self.muxA1.update(self.muxA.out, 0)
        self.muxA1.control(self.pr2.muxa1_out)
        self.alu.in_update(self.muxA1.out, '0')

        self.muxB.control(self.pr2.muxb_out)
        self.muxB1.update(self.muxB.out, 0)
        self.muxB1.control(self.pr2.muxb1_out)
        self.alu.in_update(self.muxB1.out, '1')

        self.alu.con_update(self.pr2.alu_out)
        self.alu.control()
        self.muxRZ.update(self.alu.out, 0)

        if self.pr2.opcode_out == '1100011' or self.pr2.opcode_out == '1101111' or self.pr2.opcode_out == '1100111':
            self.muxRZ.update(self.pr2.pc_temp_out, 1)

        self.muxRZ.control(self.pr2.muxrz_out)
        self.pr3.rz_in = self.muxRZ.out
        if self.pr2.pc_out == '0000011':
            self.muxRM.control(self.pr2.muxrm_out)
            self.pr3.rm_in = self.muxRM.out
            if self.pr2.byte_out == 1: self.rm = '0x' + self.rm[10:]
            elif self.pr2.byte_out == 2: self.rm = '0x' + self.rm[8:]
            self.pr3.update(self.pr2.muxy_out, self.pr2.rd_out, self.pr2.opcode_out, self.pr2.pc_out, self.pr2.byte_out, self.pr2.muxrm_out,
                            self.pr2.muxm_out, self.pr3.rm_in)
        else:
            self.pr3.update(self.pr2.muxy_out, self.pr2.rd_out, self.pr2.opcode_out, self.pr2.pc_out, self.pr2.byte_out, self.pr2.muxrm_out,
                            self.pr2.muxm_out, '0x00000000')
        self.muxA1.update(self.pr3.rz_in, 1)
        self.muxB1.update(self.pr3.rz_in, 1)
        self.ins_stage[self.pr3.pc_in] = 'MA'

    def mem_access(self):
        if self.con_mux['Y'] == '0':  # for R format, I format(ALU),auipc,jal,jalr,SB and lui instructions
            self.muxY.update(self.pr3.rz_out, 0)
        elif self.con_mux['Y'] == '1':  # for load and store instructions
            self.MAR = self.pr3.rz_out
            if self.pr3.pc_out == '0000011':
                self.MDR = load_from_memory(self.MAR, self.pr3.byte_out,
                                            self.mem)  # obtains data at required memory address and stores it in MDR
            elif self.pr3.pc_out == '0100011':
                self.muxM.update(self.pr3.rm_out, 0)
                self.muxM.control(self.pr3.muxm_out)
                self.MDR = self.muxM.out
                store_to_memory(self.MAR, self.MDR, self.mem)  # MDR is restored to '0x00000000'
            self.muxY.update(self.MDR, 1)

        self.muxY.control(self.con_mux['Y'])
        self.pr3.ry_in = self.muxY.out
        self.muxA1.update(self.pr3.ry_in, 2)
        self.muxB1.update(self.pr3.ry_in, 2)
        self.muxM.update(self.pr3.ry_in, 1)
        self.muxRM.update(self.pr3.ry_in, 1)
        self.pr4.update(self.pr3.rd_out, self.pr3.pc_out)
        self.ins_stage[self.pr4.pc_in] = 'WB'

    def register_update(self):
        self.reg1.reg_for_output(self.pr4.rd_out)
        self.reg1.load(self.pr4.ry_out)
        del self.ins_stage[self.pr4.pc_out]
        del self.ins_reg[self.pr4.pc_out]
        self.total_ins=self.total_ins+1

start_phase3=PhaseThree("Fibonacci.mc")