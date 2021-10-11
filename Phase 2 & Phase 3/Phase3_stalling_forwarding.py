class predictor:
    def __init__(self,file):
        # For SB instruction beq, blt, bne, bge defining 1-bit branch prediction hardware
        self.branch_prediction = {}
        self.branch_target = {}

        f = open(file,'r+')
        lines = f.readlines()
        for line in lines:
            words = line.split()
            pc = words[0]
            IR = bin(int(words[1], 16))  # Calculating opcode
            length = 34 - len(IR)
            IR = IR[0:2] + '0' * length + IR[2:]
            IR = IR[2:]        # Binary starts with 0bxxxx....
            opcode = IR[25:]
            '''
            1. words[0] is the pc line address - key of dictionary
            2. First value of the dictionary is BHT ( branch history table )
                # 0 - NT - branch not taken 
                # 1 - T - branch taken
            3. Second value of the dictionary is Target Address ( where it is pointing to )
            '''
            if opcode == '1100011':     # SB format instruction
                imm = IR[0] + IR[24] + IR[1:7] + IR[20:24] + '0'  # For calculating target address
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
                self.branch_prediction[pc] = 0
                self.branch_target[pc] = target_pc

            if opcode == '1100111':       # jalr
                funct3 = IR[17:20]
                if funct3 == '000':
                    target_pc = 0
                    target_pc = hex(target_pc)
                    self.branch_prediction[pc] = 1
                    self.branch_target[pc] = target_pc

            if opcode == '1101111':        #jal
                imm = IR[0] + IR[12:20] + IR[11] + IR[1:11] + '0'   # msb is imm[0]
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
                self.branch_prediction[pc] = 1
                self.branch_target[pc] = target_pc

    # After execution, result of branch prediction is known, then update the prediction
    def update_predict(self,value,pc):      # SB Format
        if value == False:  # update
            if self.branch_prediction[pc]==1:
                self.branch_prediction[pc]=0
            else:
                self.branch_prediction[pc]=1
        else:
            pass

    '''
    # In the fetch stage if opcode is in SB format we need to predict the value return the predicted PC for next 
    instruction
    '''

    def prediction_jalSB(self,pc):       # jal, SB
        if pc in self.branch_prediction:
            a = self.branch_prediction[pc]
            b = self.branch_target[pc]
            return a,b

    def prediction_jalr(self, pc, reg1, ir):
        if pc in self.branch_prediction:
            IR = ir
            opcode = IR[25:]
            if opcode == '1100111':
                funct3 = IR[17:20]
                if funct3 == '000':
                    imm = IR[0:12]
                    imm = convert_to_hex_extend(imm)
                    rs1 = IR[12:17]
                    var1 = int(reg1.dcreg[rs1], 16)
                    if (imm[2] == 'f' or imm[2] == 'e' or imm[2] == 'd' or imm[2] == 'c' or
                            imm[2] == 'b' or imm[2] == 'a' or imm[2] == '9' or imm[2] == '8'):
                        var2 = int(imm[2:], 16) - 2 ** 32
                    else:
                        var2 = int(imm[2:], 16)
                    target_pc = var1 + var2
                    target_pc = hex(target_pc)
                    a = 1
                    b = target_pc
                    return a, b

class if_id:

    def __init__(self):
        self.ir = ''
        self.prevpc = ''
        self.pc = '0x0'   # next pc
        self.bp = 0
        self.ta = '0x0'
        self.flush = 0
        self.knob5 = 0

    def update(self,pc,ir,PC_temp,bp,ta):
        self.prevpc = PC_temp
        self.pc = pc
        self.ir = ir
        self.bp = bp
        self.ta = ta

    def print_if_id(self):
        print('IR:' + self.ir)
        print('Previous PC:' + self.prevpc)
        print('PC:' + self.pc)
        print('Branch Prediction:' + str(self.bp))
        print('Target Address:' + self.ta)

class id_ex:
    def __init__(self):
        self.IR = ''
        self.con_a = ''
        self.con_b = ''
        self.con_y = ''
        self.con_e = ''
        self.con_pc = ''
        self.con_inc = ''
        self.funct3 = ''
        self.muxY_byte_update = ''
        self.rm = ''
        self.rd = ''
        self.rs1 = ''
        self.rs2 = ''
        self.imm = ''
        self.rd = ''
        self.opcode = ''
        self.muxINC_update = ''
        self.PC_temp = ''
        self.PC = ''
        self.RA = ''
        self.rd = ''
        self.stall = 0
        self.bp = 0
        self.ta = '0x0'
        self.flush = 0
        self.knob5 = 0

        # Forwarding implementation
        self.con_ee = 0
        self.rd_ee = 0
        self.con_me = 0
        self.rd_me = 0
        self.con_mm = 0
        self.rd_mm = 0
        self.con_pwm = 0
        self.rd_pwm = 0

    def update_R (self,con_a,con_b,con_y,con_e,rd,rs1,rs2,opcode,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,con_pwm,rd_pwm):
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.con_a = con_a
        self.con_b = con_b
        self.con_y = con_y
        self.con_e = con_e
        self.opcode = opcode
        self.con_ee = con_ee
        self.con_me = con_me
        self.con_mm = con_mm
        self.con_pwm = con_pwm
        self.rd_ee = rd_ee
        self.rd_me = rd_me
        self.rd_mm = rd_mm
        self.rd_pwm = rd_pwm

    def update_I(self,con_a,con_b,con_y,con_e,rd,opcode,rs1,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,con_pwm,rd_pwm):
        self.rd = rd
        self.con_a = con_a
        self.con_b = con_b
        self.con_y = con_y
        self.con_e = con_e
        self.opcode = opcode
        self.rs1 = rs1
        self.con_ee = con_ee
        self.con_me = con_me
        self.con_mm = con_mm
        self.con_pwm = con_pwm
        self.rd_ee = rd_ee
        self.rd_me = rd_me
        self.rd_mm = rd_mm
        self.rd_pwm = rd_pwm

    def update_jal(self,con_e,con_pc,con_inc,con_y,imm,muxINC_update,opcode,PC_temp,PC,rd,bp,ta,con_ee,rd_ee,con_me,
                   rd_me,con_mm,rd_mm,con_pwm,rd_pwm):
        self.imm = imm
        self.con_pc = con_pc
        self.con_inc = con_inc
        self.con_y = con_y
        self.con_e = con_e
        self.muxINC_update = muxINC_update
        self.opcode = opcode
        self.PC_temp = PC_temp
        self.PC = PC
        self.rd = rd
        self.bp = bp
        self.ta = ta
        self.con_ee = con_ee
        self.con_me = con_me
        self.con_mm = con_mm
        self.con_pwm = con_pwm
        self.rd_ee = rd_ee
        self.rd_me = rd_me
        self.rd_mm = rd_mm
        self.rd_pwm = rd_pwm

    def update_jalr(self,con_e,con_pc,con_inc,con_y,imm,muxINC_update,opcode,PC_temp,PC,RA,rd,bp,ta,con_ee,rd_ee,
                    con_me,rd_me,con_mm,rd_mm,con_pwm,rd_pwm):
        self.imm = imm
        self.con_pc = con_pc
        self.con_inc = con_inc
        self.con_y = con_y
        self.con_e = con_e
        self.muxINC_update = muxINC_update
        self.opcode = opcode
        self.PC_temp = PC_temp
        self.PC = PC
        self.RA = RA
        self.rd = rd
        self.bp = bp
        self.ta = ta
        self.con_ee = con_ee
        self.con_me = con_me
        self.con_mm = con_mm
        self.con_pwm = con_pwm
        self.rd_ee = rd_ee
        self.rd_me = rd_me
        self.rd_mm = rd_mm
        self.rd_pwm = rd_pwm

    def update_load(self,rd,con_a,con_b,con_y,con_e,muxY_byte_update,opcode,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,
                    con_pwm,rd_pwm):
        self.con_a = con_a
        self.con_b = con_b
        self.con_y = con_y
        self.con_e = con_e
        self.rd = rd
        self.muxY_byte_update = muxY_byte_update
        self.opcode = opcode
        self.con_ee = con_ee
        self.con_me = con_me
        self.con_mm = con_mm
        self.con_pwm = con_pwm
        self.rd_ee = rd_ee
        self.rd_me = rd_me
        self.rd_mm = rd_mm
        self.rd_pwm = rd_pwm

    def update_auipc_lui(self,rd,con_a,con_b,con_y,con_e,opcode,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,con_pwm,rd_pwm):
        self.rd = rd
        self.con_a = con_a
        self.con_b = con_b
        self.con_y = con_y
        self.con_e = con_e
        self.opcode = opcode
        self.con_ee = con_ee
        self.con_me = con_me
        self.con_mm = con_mm
        self.con_pwm = con_pwm
        self.rd_ee = rd_ee
        self.rd_me = rd_me
        self.rd_mm = rd_mm
        self.rd_pwm = rd_pwm

    def update_sb(self,con_a,con_b,con_y,con_e,imm,muxINC_update,opcode,PC_temp,PC,bp,ta,con_ee,rd_ee,con_me,rd_me,
                  con_mm,rd_mm,con_pwm,rd_pwm):
        self.imm = imm
        self.con_a = con_a
        self.con_b = con_b
        self.con_y = con_y
        self.con_e = con_e
        self.muxINC_update = muxINC_update
        self.opcode = opcode
        self.PC_temp = PC_temp
        self.PC = PC
        self.bp = bp
        self.ta = ta
        self.con_ee = con_ee
        self.con_me = con_me
        self.con_mm = con_mm
        self.con_pwm = con_pwm
        self.rd_ee = rd_ee
        self.rd_me = rd_me
        self.rd_mm = rd_mm
        self.rd_pwm = rd_pwm

    def update_S(self,con_a,con_b,con_y,con_e,rm,muxY_byte_update,opcode,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,con_pwm,
                 rd_pwm):
        self.con_a = con_a
        self.con_b = con_b
        self.con_y = con_y
        self.con_e = con_e
        self.rm = rm
        self.muxY_byte_update = muxY_byte_update
        self.opcode = opcode
        self.con_ee = con_ee
        self.con_me = con_me
        self.con_mm = con_mm
        self.con_pwm = con_pwm
        self.rd_ee = rd_ee
        self.rd_me = rd_me
        self.rd_mm = rd_mm
        self.rd_pwm = rd_pwm

    def print_id_ex(self):
        print('IR:' + self.IR)
        print('Control A:' + self.con_a)
        print('Control B:' + self.con_b)
        print('Control Y:' + self.con_y)
        print('Control E:' + self.con_e)
        print('Control PC:' + self.con_pc)
        print('Control INC:' + str(self.con_inc))
        print('Funct3:' + self.funct3)
        print('MuxY byte update:' + str(self.muxY_byte_update))
        print('RM:' + self.rm)
        print('Rd:' + self.rd)
        print('Immediate:' + self.imm)
        print('Opcode:' + self.opcode)
        print('MuxInc update:' + str(self.muxINC_update))
        print('PC_temp:' + self.PC_temp)
        print('PC:' + self.PC)
        print('RA:' + self.RA)
        print('Branch Prediction:' + str(self.bp))
        print('Target Address:' + self.ta)

class ex_mem:
    def __init__(self):
        self.opcode = ''
        self.muxY_byte_update = ''
        self.rm = ''
        self.rd = ''
        self.imm = ''
        self.PC_temp = ''
        self.PC = ''
        self.stall = 0
        self.flush = 0
        self.con_y = ''
        self.rz = ''
        self.con_mm = ''
        self.con_pwm = ''
        self.rd_mm = ''
        self.rd_pwm = ''
        self.knob5 = 0

    def print_ex_mem(self):
        print('Opcode:' + self.opcode)
        print('MuxY_byte_update:' + str(self.muxY_byte_update))
        print('RM:'+self.rm)
        print('Rd:' + self.rd)
        print('Immediate:' + self.imm)
        print('PC_temp' + self.PC_temp)
        print('PC:' + self.PC)
        print('Control Y:' + self.con_y)

    def nonbranch_SB(self,con_y,opcode,muxY_byte_update,rm,rd,imm,PC_temp,rz,con_mm,rd_mm,con_pwm,rd_pwm):
        self.opcode = opcode
        self.muxY_byte_update = muxY_byte_update
        self.rm  = rm
        self.rd = rd
        self.imm = imm
        self.PC_temp = PC_temp
        self.con_y = con_y
        self.rz = rz
        self.con_mm = con_mm
        self.con_pwm = con_pwm
        self.rd_mm = rd_mm
        self.rd_pwm = rd_pwm

    def branch(self,rz,rd,con_y,con_mm,rd_mm,con_pwm,rd_pwm):
        self.rz = rz
        self.rd = rd
        self.con_y = con_y
        self.con_mm = con_mm
        self.con_pwm = con_pwm
        self.rd_mm = rd_mm
        self.rd_pwm = rd_pwm

class mem_wr:
    def __init__(self):
        self.rd_in = ''
        self.opcode_in = ''
        self.ry_in = ''

        self.rd_out = ''
        self.opcode_out = ''
        self.ry_out = ''

        self.stall = 0
        self.flush = 0
        self.knob5 = 0

    def update_in(self,rd,opcode,ry):
        self.rd_in = rd
        self.opcode_in = opcode
        self.ry_in = ry

    def update_out(self):
        self.rd_out = self.rd_in
        self.opcode_out = self.opcode_in
        self.ry_out = self.ry_in

    def print_mem_wr(self):
        print('Rd:' + self.rd_in)
        print('Opcode:' + self.opcode_in)
        print('Ry:' + self.rd_in)

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
    def load(self, inp, rd):
        self.wrline = inp
        if rd != '00000':
            self.dcreg[rd] = self.wrline
        else:
            self.dcreg[rd] = "0x00000000"

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
            # introducing req. 0 in front as well as ensuring output to be 32 bits
            self.out = str[0:2] + '0' * var2 + str[2: 34 - var2]
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
        self.muxINC = Mux('0x0004', '0x0000')      # update Ish suggestion
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
            # print("EXECUTE: Branch taken and PC set as sum of " + self.in0 + " and " + self.in1)
            return
        # print("EXECUTE: Add {0} and {1} and set PC as output".format(var1,var2))
        return

class data_hazard:

    def __init__(self,Ins_memory):
        # Basic Hardware initialisation
        self.pc_prevprev = ''
        self.pc_prev = ''
        self.pc_cur = ''
        self.ir_prevprev = '0x00000000'
        self.ir_prev = '0x00000000'
        self.ir_cur = '0x00000000'
        self.Ins_memory = Ins_memory

        # Hardware for Forwarding
        self.e_e = 0  # 0 - No forwarding between E ot E latch else 1
        self.m_e = 0  # 0 - No forwarding between M ot E latch else 1
        self.m_m = 0  # 0 - No forwarding between M ot M latch else 1
        self.pw_m = 0  # 0 - No forwarding between post write back ot E latch else 1
        self.rd_forward_ee = 0    # Forwarding the match data
        self.rd_forward_me = 0
        self.rd_forward_mm = 0
        self.rd_forward_pwm = 0
        self.temp = 0
        # Stall in prev stage
        self.stall_previns = 0   # Stall present one instruction earlier

    def forward_reset(self):
        self.e_e = 0
        self.m_e = 0
        self.m_m = 0
        self.pw_m = 0

    def forward_rd_reset(self):
        self.rd_forward_ee = 0  # Forwarding the match data
        self.rd_forward_me = 0
        self.rd_forward_mm = 0
        self.rd_forward_pwm = 0

    def dh_R(self,pc):
        if self.pc_cur != pc:
            self.pc_prevprev = self.pc_prev
            self.pc_prev = self.pc_cur
            self.pc_cur = pc             # current pc for data hazard but actually it is PC_temp

        else:
            return self.stall_previns           # forwards will remain same lets see what's happen

        self.forward_reset()
        self.forward_rd_reset()

        if self.pc_prevprev == '':
            self.ir_prevprev = '0x00000000'
        else:
            self.ir_prevprev = self.Ins_memory[self.pc_prevprev]

        if self.pc_prev == '':
            self.ir_prev = '0x00000000'
        else:
            self.ir_prev = self.Ins_memory[self.pc_prev]

        if self.pc_cur == '':
            self.ir_cur = '0x00000000'
        else:
            self.ir_cur = self.Ins_memory[self.pc_cur]

        IR = bin(int(self.ir_cur, 16))  # For current IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_cur = IR[2:]

        IR = bin(int(self.ir_prev, 16))  # For prev. IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_prev = IR[2:]

        IR = bin(int(self.ir_prevprev, 16))  # For prev. to prev. IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_prevprev = IR[2:]

        if self.stall_previns == 0:     # Previous instruction not having stall
            stall_prev = 0
            rs1 = int(self.ir_cur[12:17], 2)  # current pc
            rs2 = int(self.ir_cur[7:12], 2)
            opcode = self.ir_prev[25:]
            self.temp = 0
            if (opcode == '0110011' or opcode == '0010011' or (opcode == '1100111' and self.ir_prev[17:20] == '000')
                    or opcode == '1101111' or opcode == '0010111' or opcode == '0110111'):
                # R format,I-ori,jalr,jal,auipc,lui, E-E Forwarding
                rd = int(self.ir_prev[20:25], 2)  # pc earlier
                ############################
                opcode1 = self.ir_prevprev[25:]
                if (opcode1 == '0110011' or opcode1 == '0010011' or opcode1 == '0000011'
                        or (opcode1 == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode1 == '1101111' or opcode1 == '0010111' or opcode1 == '0110111'):
                    rd1 = int(self.ir_prevprev[20:25], 2)
                    if rd1 == rd:
                        self.temp = 1
                ############################
                if rd == 0:
                    stall_prev = 0
                else:
                    if (rd == rs1 and rd == rs2) or (rd == rs1 and rd != rs2) or (rd != rs1 and rd == rs2):
                        stall_prev = 0
                        self.rd_forward_ee = rd
                        self.e_e = 1
                    else:
                        stall_prev = 0

            elif opcode == '0000011':  # Load instruction
                rd = int(self.ir_prev[20:25], 2)  # pc earlier
                ############################
                opcode1 = self.ir_prevprev[25:]
                if (opcode1 == '0110011' or opcode1 == '0010011' or opcode1 == '0000011'
                        or (opcode1 == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode1 == '1101111' or opcode1 == '0010111' or opcode1 == '0110111'):
                    rd1 = int(self.ir_prevprev[20:25], 2)
                    if rd1 == rd:
                        self.temp = 1
                ############################
                if rd == 0:
                    stall_prev = 0
                else:
                    if (rd == rs1 and rd == rs2) or (rd == rs1 and rd != rs2) or (rd != rs1 and rd == rs2):
                        stall_prev = 1
                        self.rd_forward_me = rd
                        self.m_e = 1
                    else:
                        stall_prev = 0

            else:
                stall_prev = 0

            if stall_prev != 0 or self.temp == 1:
                self.stall_previns = stall_prev
                stall_number = self.stall_previns
                return stall_number

            else:
                stall_prevprev = 0
                # rs1,rs2 will remain same but opcode and rd will change for the prev_prev instruction
                opcode = self.ir_prevprev[25:]
                if (opcode == '0110011' or opcode == '0010011' or opcode == '0000011'
                        or (opcode == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode == '1101111' or opcode == '0010111' or opcode == '0110111'):
                    # R format,I-ori,load,jalr,jal,auipc,lui, E-E Forwarding
                    rd = int(self.ir_prevprev[20:25], 2)  # pc earlier
                    if rd == 0:
                        stall_prevprev = 0
                    else:
                        if (rd == rs1 and rd == rs2) or (rd == rs1 and rd != rs2) or (rd != rs1 and rd == rs2):
                            stall_prevprev = 0
                            self.rd_forward_me = rd
                            self.m_e = 1
                        else:
                            stall_prevprev = 0

                else:
                    stall_prevprev = 0
                self.stall_previns = stall_prevprev
                stall_number = self.stall_previns
                return stall_number

        elif self.stall_previns != 0:   # Previous instruction is having stall, Means only check for prev. ins. only.
            rs1 = int(self.ir_cur[12:17], 2)  # current pc
            rs2 = int(self.ir_cur[7:12], 2)
            opcode = self.ir_prev[25:]
            if (opcode == '0110011' or opcode == '0010011' or (opcode == '1100111' and self.ir_prev[17:20] == '000')
                    or opcode == '1101111' or opcode == '0010111' or opcode == '0110111'):
                # R format,I-ori,jalr,jal,auipc,lui, E-E Forwarding
                rd = int(self.ir_prev[20:25], 2)  # pc earlier
                if rd == 0:
                    stall_prev = 0
                else:
                    if (rd == rs1 and rd == rs2) or (rd == rs1 and rd != rs2) or (rd != rs1 and rd == rs2):
                        stall_prev = 0
                        self.rd_forward_ee = rd
                        self.e_e = 1
                    else:
                        stall_prev = 0

            elif opcode == '0000011':  # Load instruction
                rd = int(self.ir_prev[20:25], 2)  # pc earlier
                if rd == 0:
                    stall_prev = 0
                else:
                    if (rd == rs1 and rd == rs2) or (rd == rs1 and rd != rs2) or (rd != rs1 and rd == rs2):
                        stall_prev = 1
                        self.rd_forward_me = rd
                        self.m_e = 1
                    else:
                        stall_prev = 0

            else:
                stall_prev = 0

            self.stall_previns = stall_prev
            stall_number = self.stall_previns
            return stall_number

    def dh_Immediate(self,pc):
        if self.pc_cur != pc:
            self.pc_prevprev = self.pc_prev
            self.pc_prev = self.pc_cur
            self.pc_cur = pc  # current pc for data hazard but actually it is PC_temp
        else:
            return self.stall_previns

        self.forward_reset()
        self.forward_rd_reset()

        if self.pc_prevprev == '':
            self.ir_prevprev = '0x00000000'
        else:
            self.ir_prevprev = self.Ins_memory[self.pc_prevprev]

        if self.pc_prev == '':
            self.ir_prev = '0x00000000'
        else:
            self.ir_prev = self.Ins_memory[self.pc_prev]

        if self.pc_cur == '':
            self.ir_cur = '0x00000000'
        else:
            self.ir_cur = self.Ins_memory[self.pc_cur]

        IR = bin(int(self.ir_cur, 16))  # For current IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_cur = IR[2:]

        IR = bin(int(self.ir_prev, 16))  # For prev. IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_prev = IR[2:]

        IR = bin(int(self.ir_prevprev, 16))  # For prev. to prev. IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_prevprev = IR[2:]

        if self.stall_previns == 0:  # Previous instruction not having stall
            stall_prev = 0
            rs1 = int(self.ir_cur[12:17], 2)  # current pc
            opcode = self.ir_prev[25:]
            self.temp = 0
            if (opcode == '0110011' or opcode == '0010011'
                    or (opcode == '1100111' and self.ir_prev[17:20] == '000') or opcode == '1101111' or
                    opcode == '0010111' or opcode == '0110111'):  # R format,I-ori,jalr,jal,auipc,lui
                rd = int(self.ir_prev[20:25], 2)
                ############################
                opcode1 = self.ir_prevprev[25:]
                if (opcode1 == '0110011' or opcode1 == '0010011' or opcode1 == '0000011'
                        or (opcode1 == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode1 == '1101111' or opcode1 == '0010111' or opcode1 == '0110111'):
                    rd1 = int(self.ir_prevprev[20:25], 2)
                    if rd1 == rd:
                        self.temp = 1
                ############################
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1:
                        stall_prev = 0
                        self.rd_forward_ee = rd
                        self.e_e = 1
                    else:
                        stall_prev = 0

            elif opcode == '0000011':  # Load instruction
                rd = int(self.ir_prev[20:25], 2)
                ############################
                opcode1 = self.ir_prevprev[25:]
                if (opcode1 == '0110011' or opcode1 == '0010011' or opcode1 == '0000011'
                        or (opcode1 == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode1 == '1101111' or opcode1 == '0010111' or opcode1 == '0110111'):
                    rd1 = int(self.ir_prevprev[20:25], 2)
                    if rd1 == rd:
                        self.temp = 1
                ############################
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1:
                        stall_prev = 1
                        self.rd_forward_me = rd
                        self.m_e = 1
                    else:
                        stall_prev = 0

            else:
                stall_prev = 0

            if stall_prev != 0 or self.temp == 1:
                self.stall_previns = stall_prev
                stall_number = self.stall_previns
                return stall_number

            else:
                stall_prevprev = 0
                # rs1 will remain same but opcode and rd will change for the prev_prev instruction
                opcode = self.ir_prevprev[25:]
                if (opcode == '0110011' or opcode == '0010011' or opcode == '0000011'
                        or (opcode == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode == '1101111' or opcode == '0010111' or opcode == '0110111'):
                    # R format,I-ori,jalr,jal,auipc,lui
                    rd = int(self.ir_prevprev[20:25], 2)
                    if rd == 0:
                        stall_prevprev = 0
                    else:
                        if rd == rs1:
                            stall_prevprev = 0
                            self.rd_forward_me = rd
                            self.m_e = 1
                        else:
                            stall_prevprev = 0

                else:
                    stall_prevprev = 0
                self.stall_previns = stall_prevprev
                stall_number = self.stall_previns
                return stall_number

        elif self.stall_previns != 0:  # Previous instruction is having stall, Means only check for prev. ins. only.
            rs1 = int(self.ir_cur[12:17], 2)  # current pc
            opcode = self.ir_prev[25:]
            if (opcode == '0110011' or opcode == '0010011'
                    or (opcode == '1100111' and self.ir_prev[17:20] == '000') or opcode == '1101111' or
                    opcode == '0010111' or opcode == '0110111'):  # R format,I-ori,jalr,jal,auipc,lui
                rd = int(self.ir_prev[20:25], 2)
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1:
                        stall_prev = 0
                        self.rd_forward_ee = rd
                        self.e_e = 1
                    else:
                        stall_prev = 0

            elif opcode == '0000011':  # Load instruction
                rd = int(self.ir_prev[20:25], 2)
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1:
                        stall_prev = 1
                        self.rd_forward_me = rd
                        self.m_e = 1
                    else:
                        stall_prev = 0

            else:
                stall_prev = 0

            self.stall_previns = stall_prev
            stall_number = self.stall_previns
            return stall_number

    def dh_Load(self, pc):
        if self.pc_cur != pc:
            self.pc_prevprev = self.pc_prev
            self.pc_prev = self.pc_cur
            self.pc_cur = pc  # current pc for data hazard but actually it is PC_temp
        else:
            return self.stall_previns

        self.forward_reset()
        self.forward_rd_reset()

        if self.pc_prevprev == '':
            self.ir_prevprev = '0x00000000'
        else:
            self.ir_prevprev = self.Ins_memory[self.pc_prevprev]

        if self.pc_prev == '':
            self.ir_prev = '0x00000000'
        else:
            self.ir_prev = self.Ins_memory[self.pc_prev]

        if self.pc_cur == '':
            self.ir_cur = '0x00000000'
        else:
            self.ir_cur = self.Ins_memory[self.pc_cur]

        IR = bin(int(self.ir_cur, 16))  # For current IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_cur = IR[2:]

        IR = bin(int(self.ir_prev, 16))  # For prev. IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_prev = IR[2:]

        IR = bin(int(self.ir_prevprev, 16))  # For prev. to prev. IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_prevprev = IR[2:]

        if self.stall_previns == 0:  # Previous instruction not having stall
            stall_prev = 0
            rs1 = int(self.ir_cur[12:17], 2)  # current pc
            opcode = self.ir_prev[25:]
            self.temp = 0
            if (opcode == '0110011' or opcode == '0010011'
                    or (opcode == '1100111' and self.ir_prev[17:20] == '000') or opcode == '1101111' or
                    opcode == '0010111' or opcode == '0110111'):  # R format,I-ori,jalr,jal,auipc,lui
                rd = int(self.ir_prev[20:25], 2)
                ############################
                opcode1 = self.ir_prevprev[25:]
                if (opcode1 == '0110011' or opcode1 == '0010011' or opcode1 == '0000011'
                        or (opcode1 == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode1 == '1101111' or opcode1 == '0010111' or opcode1 == '0110111'):
                    rd1 = int(self.ir_prevprev[20:25], 2)
                    if rd1 == rd:
                        self.temp = 1
                ############################
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1:
                        stall_prev = 0
                        self.rd_forward_ee = rd
                        self.e_e = 1
                    else:
                        stall_prev = 0

            elif opcode == '0000011':  # Load instruction
                rd = int(self.ir_prev[20:25], 2)
                ############################
                opcode1 = self.ir_prevprev[25:]
                if (opcode1 == '0110011' or opcode1 == '0010011' or opcode1 == '0000011'
                        or (opcode1 == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode1 == '1101111' or opcode1 == '0010111' or opcode1 == '0110111'):
                    rd1 = int(self.ir_prevprev[20:25], 2)
                    if rd1 == rd:
                        self.temp = 1
                ############################
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1:
                        stall_prev = 1
                        self.rd_forward_me = rd
                        self.m_e = 1
                    else:
                        stall_prev = 0

            else:
                stall_prev = 0

            if stall_prev != 0 or self.temp == 1:
                self.stall_previns = stall_prev
                stall_number = self.stall_previns
                return stall_number

            else:
                stall_prevprev = 0
                # rs1 will remain same but opcode and rd will change for the prev_prev instruction
                opcode = self.ir_prevprev[25:]
                if (opcode == '0110011' or opcode == '0010011' or opcode == '0000011'
                        or (opcode == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode == '1101111' or opcode == '0010111' or opcode == '0110111'):
                    # R format,I-ori,jalr,jal,auipc,lui
                    rd = int(self.ir_prevprev[20:25], 2)
                    if rd == 0:
                        stall_prevprev = 0
                    else:
                        if rd == rs1:
                            stall_prevprev = 0
                            self.rd_forward_me = rd
                            self.m_e = 1
                        else:
                            stall_prevprev = 0

                else:
                    stall_prevprev = 0
                self.stall_previns = stall_prevprev
                stall_number = self.stall_previns
                return stall_number

        elif self.stall_previns != 0:  # Previous instruction is having stall, Means only check for prev. ins. only.
            rs1 = int(self.ir_cur[12:17], 2)  # current pc
            opcode = self.ir_prev[25:]
            if (opcode == '0110011' or opcode == '0010011'
                    or (opcode == '1100111' and self.ir_prev[17:20] == '000') or opcode == '1101111' or
                    opcode == '0010111' or opcode == '0110111'):  # R format,I-ori,jalr,jal,auipc,lui
                rd = int(self.ir_prev[20:25], 2)
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1:
                        stall_prev = 0
                        self.rd_forward_ee = rd
                        self.e_e = 1
                    else:
                        stall_prev = 0

            elif opcode == '0000011':  # Load instruction
                rd = int(self.ir_prev[20:25], 2)
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1:
                        stall_prev = 1
                        self.rd_forward_me = rd
                        self.m_e = 1
                    else:
                        stall_prev = 0

            else:
                stall_prev = 0

            self.stall_previns = stall_prev
            stall_number = self.stall_previns
            return stall_number

    def dh_jalr(self, pc):
        if self.pc_cur != pc:
            self.pc_prevprev = self.pc_prev
            self.pc_prev = self.pc_cur
            self.pc_cur = pc  # current pc for data hazard but actually it is PC_temp
        else:
            return self.stall_previns

        self.forward_reset()
        self.forward_rd_reset()

        if self.pc_prevprev == '':
            self.ir_prevprev = '0x00000000'
        else:
            self.ir_prevprev = self.Ins_memory[self.pc_prevprev]

        if self.pc_prev == '':
            self.ir_prev = '0x00000000'
        else:
            self.ir_prev = self.Ins_memory[self.pc_prev]

        if self.pc_cur == '':
            self.ir_cur = '0x00000000'
        else:
            self.ir_cur = self.Ins_memory[self.pc_cur]

        IR = bin(int(self.ir_cur, 16))  # For current IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_cur = IR[2:]

        IR = bin(int(self.ir_prev, 16))  # For prev. IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_prev = IR[2:]

        IR = bin(int(self.ir_prevprev, 16))  # For prev. to prev. IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_prevprev = IR[2:]

        if self.stall_previns == 0:  # Previous instruction not having stall
            stall_prev = 0
            rs1 = int(self.ir_cur[12:17], 2)  # current pc
            opcode = self.ir_prev[25:]
            self.temp = 0
            if (opcode == '0110011' or opcode == '0010011'
                    or (opcode == '1100111' and self.ir_prev[17:20] == '000') or opcode == '1101111' or
                    opcode == '0010111' or opcode == '0110111'):  # R format,I-ori,jalr,jal,auipc,lui
                rd = int(self.ir_prev[20:25], 2)
                ############################
                opcode1 = self.ir_prevprev[25:]
                if (opcode1 == '0110011' or opcode1 == '0010011' or opcode1 == '0000011'
                        or (opcode1 == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode1 == '1101111' or opcode1 == '0010111' or opcode1 == '0110111'):
                    rd1 = int(self.ir_prevprev[20:25], 2)
                    if rd1 == rd:
                        self.temp = 1
                ############################
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1:
                        stall_prev = 0
                        self.rd_forward_ee = rd
                        self.e_e = 1
                    else:
                        stall_prev = 0

            elif opcode == '0000011':  # Load instruction
                rd = int(self.ir_prev[20:25], 2)
                ############################
                opcode1 = self.ir_prevprev[25:]
                if (opcode1 == '0110011' or opcode1 == '0010011' or opcode1 == '0000011'
                        or (opcode1 == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode1 == '1101111' or opcode1 == '0010111' or opcode1 == '0110111'):
                    rd1 = int(self.ir_prevprev[20:25], 2)
                    if rd1 == rd:
                        self.temp = 1
                ############################
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1:
                        stall_prev = 1
                        self.rd_forward_me = rd
                        self.m_e = 1
                    else:
                        stall_prev = 0

            else:
                stall_prev = 0

            if stall_prev != 0 or self.temp == 1:
                self.stall_previns = stall_prev
                stall_number = self.stall_previns
                return stall_number

            else:
                stall_prevprev = 0
                # rs1 will remain same but opcode and rd will change for the prev_prev instruction
                opcode = self.ir_prevprev[25:]
                if (opcode == '0110011' or opcode == '0010011' or opcode == '0000011'
                        or (opcode == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode == '1101111' or opcode == '0010111' or opcode == '0110111'):
                    # R format,I-ori,jalr,jal,auipc,lui
                    rd = int(self.ir_prevprev[20:25], 2)
                    if rd == 0:
                        stall_prevprev = 0
                    else:
                        if rd == rs1:
                            stall_prevprev = 0
                            self.rd_forward_me = rd
                            self.m_e = 1
                        else:
                            stall_prevprev = 0

                else:
                    stall_prevprev = 0
                self.stall_previns = stall_prevprev
                stall_number = self.stall_previns
                return stall_number

        elif self.stall_previns != 0:  # Previous instruction is having stall, Means only check for prev. ins. only.
            rs1 = int(self.ir_cur[12:17], 2)  # current pc
            opcode = self.ir_prev[25:]
            if (opcode == '0110011' or opcode == '0010011'
                    or (opcode == '1100111' and self.ir_prev[17:20] == '000') or opcode == '1101111' or
                    opcode == '0010111' or opcode == '0110111'):  # R format,I-ori,jalr,jal,auipc,lui
                rd = int(self.ir_prev[20:25], 2)
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1:
                        stall_prev = 0
                        self.rd_forward_ee = rd
                        self.e_e = 1
                    else:
                        stall_prev = 0

            elif opcode == '0000011':  # Load instruction
                rd = int(self.ir_prev[20:25], 2)
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1:
                        stall_prev = 1
                        self.rd_forward_me = rd
                        self.m_e = 1
                    else:
                        stall_prev = 0

            else:
                stall_prev = 0

            self.stall_previns = stall_prev
            stall_number = self.stall_previns
            return stall_number

    def dh_store(self,pc):
        if self.pc_cur != pc:
            self.pc_prevprev = self.pc_prev
            self.pc_prev = self.pc_cur
            self.pc_cur = pc  # current pc for data hazard but actually it is PC_temp
        else:
            return self.stall_previns

        self.forward_reset()
        self.forward_rd_reset()

        if self.pc_prevprev == '':
            self.ir_prevprev = '0x00000000'
        else:
            self.ir_prevprev = self.Ins_memory[self.pc_prevprev]

        if self.pc_prev == '':
            self.ir_prev = '0x00000000'
        else:
            self.ir_prev = self.Ins_memory[self.pc_prev]

        if self.pc_cur == '':
            self.ir_cur = '0x00000000'
        else:
            self.ir_cur = self.Ins_memory[self.pc_cur]

        IR = bin(int(self.ir_cur, 16))  # For current IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_cur = IR[2:]

        IR = bin(int(self.ir_prev, 16))  # For prev. IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_prev = IR[2:]

        IR = bin(int(self.ir_prevprev, 16))  # For prev. to prev. IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_prevprev = IR[2:]

        if self.stall_previns == 0:
            rs1 = int(self.ir_cur[12:17], 2)  # current pc
            rs2 = int(self.ir_cur[7:12], 2)
            opcode = self.ir_prev[25:]
            self.temp = 0                          # To go to prev_prev instruction
            if (opcode == '0110011' or opcode == '0010011' or (opcode == '1100111' and self.ir_prev[17:20] == '000')
                    or opcode == '1101111' or opcode == '0010111' or opcode == '0110111'):
                rd = int(self.ir_prev[20:25], 2)  # pc earlier
                ############################
                opcode1 = self.ir_prevprev[25:]
                if (opcode1 == '0110011' or opcode1 == '0010011' or opcode1 == '0000011'
                        or (opcode1 == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode1 == '1101111' or opcode1 == '0010111' or opcode1 == '0110111'):
                    rd1 = int(self.ir_prevprev[20:25], 2)
                    if rd1==rd:
                        self.temp=1
                ############################
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1 and rd == rs2:
                        stall_prev = 0
                        self.e_e = 1
                        self.m_m = 1
                        self.rd_forward_ee = rd
                        self.rd_forward_mm = rd
                        # update both E-E, M-M
                    elif rd == rs1 and rd != rs2:
                        stall_prev = 0
                        self.e_e = 1
                        self.rd_forward_ee = rd
                        # update E-E
                    elif rd != rs1 and rd == rs2:
                        stall_prev = 0
                        self.m_m = 1
                        self.rd_forward_mm = rd
                        # update M-M
                    else:
                        stall_prev = 0

            elif opcode == '0000011':  # Load instruction
                rd = int(self.ir_prev[20:25], 2)  # pc earlier
                ############################
                opcode1 = self.ir_prevprev[25:]
                if (opcode1 == '0110011' or opcode1 == '0010011' or opcode1 == '0000011'
                        or (opcode1 == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode1 == '1101111' or opcode1 == '0010111' or opcode1 == '0110111'):
                    rd1 = int(self.ir_prevprev[20:25], 2)
                    if rd1 == rd:
                        self.temp = 1
                ############################
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1 and rd == rs2:
                        stall_prev = 1
                        self.m_e = 1
                        self.pw_m = 1
                        self.rd_forward_me = rd
                        self.rd_forward_pwm = rd
                        # update both E-E, M-M
                    elif rd == rs1 and rd != rs2:
                        stall_prev = 1
                        self.m_e = 1
                        self.rd_forward_me = rd
                        # update E-E
                    elif rd != rs1 and rd == rs2:
                        stall_prev = 0
                        self.m_m = 1
                        self.rd_forward_mm = rd
                        # update M-M
                    else:
                        stall_prev = 0

            else:
                stall_prev = 0

            if stall_prev != 0 or self.temp == 1:
                self.stall_previns = stall_prev
                stall_number = self.stall_previns
                return stall_number

            else:
                stall_prevprev = 0
                opcode = self.ir_prevprev[25:]
                if (opcode == '0110011' or opcode == '0010011' or opcode == '0000011' or
                        (opcode=='1100111' and self.ir_prevprev[17:20]=='000')
                        or opcode == '1101111' or opcode == '0010111' or opcode == '0110111'):
                    rd = int(self.ir_prevprev[20:25], 2)  # pc earlier
                    if rd == 0:
                        stall_prevprev = 0
                    else:
                        if rd == rs1 and rd == rs2:
                            stall_prevprev = 0
                            self.m_e = 1
                            self.pw_m = 1
                            self.rd_forward_me = rd
                            self.rd_forward_pwm = rd
                            # update both E-E, M-M
                        elif rd == rs1 and rd != rs2:
                            stall_prevprev = 0
                            self.m_e = 1
                            self.rd_forward_me = rd
                            # update E-E
                        elif rd != rs1 and rd == rs2:
                            stall_prevprev = 0
                            self.pw_m = 1
                            self.rd_forward_pwm = rd
                            # update M-M
                        else:
                            stall_prevprev = 0
                else:
                    stall_prevprev = 0

                self.stall_previns = stall_prevprev
                stall_number = self.stall_previns
                return stall_number

        elif self.stall_previns != 0:  # only check the previous instruction
            rs1 = int(self.ir_cur[12:17], 2)  # current pc
            rs2 = int(self.ir_cur[7:12], 2)
            opcode = self.ir_prev[25:]
            if (opcode == '0110011' or opcode == '0010011' or (opcode == '1100111' and self.ir_prev[17:20] == '000')
                    or opcode == '1101111' or opcode == '0010111' or opcode == '0110111'):
                rd = int(self.ir_prev[20:25], 2)  # pc earlier
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd==rs1 and rd==rs2:
                        stall_prev = 0
                        self.e_e = 1
                        self.m_m = 1
                        self.rd_forward_ee = rd
                        self.rd_forward_mm = rd
                        # update both E-E, M-M
                    elif rd==rs1 and rd!=rs2:
                        stall_prev = 0
                        self.e_e = 1
                        self.rd_forward_ee = rd
                        # update E-E
                    elif rd!=rs1 and rd==rs2:
                        stall_prev = 0
                        self.m_m = 1
                        self.rd_forward_mm = rd
                        #update M-M
                    else:
                        stall_prev = 0

            elif opcode == '0000011':  # Load instruction
                rd = int(self.ir_prev[20:25], 2)  # pc earlier
                if rd == 0:
                    stall_prev = 0
                else:
                    if (rd == rs1 and rd == rs2):
                        stall_prev = 1
                        self.m_e = 1
                        self.pw_m = 1
                        self.rd_forward_me = rd
                        self.rd_forward_pwm = rd
                        # update both E-E, M-M
                    elif (rd == rs1 and rd != rs2):
                        stall_prev = 1
                        self.m_e = 1
                        self.rd_forward_me = rd
                        # update E-E
                    elif (rd != rs1 and rd == rs2):
                        stall_prev = 0
                        self.m_m = 1
                        self.rd_forward_mm = rd
                        # update M-M
                    else:
                        stall_prev = 0

            else:
                stall_prev = 0
            self.stall_previns = stall_prev
            stall_number = self.stall_previns
            return stall_number

    def dh_SB(self,pc):
        if self.pc_cur != pc:
            self.pc_prevprev = self.pc_prev
            self.pc_prev = self.pc_cur
            self.pc_cur = pc             # current pc for data hazard but actually it is PC_temp

        else:
            return self.stall_previns           # forwards will remain same lets see what's happen

        self.forward_reset()
        self.forward_rd_reset()

        if self.pc_prevprev == '':
            self.ir_prevprev = '0x00000000'
        else:
            self.ir_prevprev = self.Ins_memory[self.pc_prevprev]

        if self.pc_prev == '':
            self.ir_prev = '0x00000000'
        else:
            self.ir_prev = self.Ins_memory[self.pc_prev]

        if self.pc_cur == '':
            self.ir_cur = '0x00000000'
        else:
            self.ir_cur = self.Ins_memory[self.pc_cur]

        IR = bin(int(self.ir_cur, 16))  # For current IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_cur = IR[2:]

        IR = bin(int(self.ir_prev, 16))  # For prev. IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_prev = IR[2:]

        IR = bin(int(self.ir_prevprev, 16))  # For prev. to prev. IR value
        length = 34 - len(IR)
        IR = IR[0:2] + '0' * length + IR[2:]
        self.ir_prevprev = IR[2:]

        if self.stall_previns == 0:     # Previous instruction not having stall
            stall_prev = 0
            rs1 = int(self.ir_cur[12:17], 2)  # current pc
            rs2 = int(self.ir_cur[7:12], 2)
            opcode = self.ir_prev[25:]
            self.temp = 0
            if (opcode == '0110011' or opcode == '0010011' or (opcode == '1100111' and self.ir_prev[17:20] == '000')
                    or opcode == '1101111' or opcode == '0010111' or opcode == '0110111'):
                # R format,I-ori,jalr,jal,auipc,lui, E-E Forwarding
                rd = int(self.ir_prev[20:25], 2)  # pc earlier
                ############################
                opcode1 = self.ir_prevprev[25:]
                if (opcode1 == '0110011' or opcode1 == '0010011' or opcode1 == '0000011'
                        or (opcode1 == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode1 == '1101111' or opcode1 == '0010111' or opcode1 == '0110111'):
                    rd1 = int(self.ir_prevprev[20:25], 2)
                    if rd1 == rd:
                        self.temp = 1
                ############################
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1 and rd == rs2:
                        stall_prev = 0
                    elif (rd == rs1 and rd != rs2) or (rd != rs1 and rd == rs2):
                        stall_prev = 0
                        self.rd_forward_ee = rd
                        self.e_e = 1
                    else:
                        stall_prev = 0

            elif opcode == '0000011':  # Load instruction
                rd = int(self.ir_prev[20:25], 2)  # pc earlier
                ############################
                opcode1 = self.ir_prevprev[25:]
                if (opcode1 == '0110011' or opcode1 == '0010011' or opcode1 == '0000011'
                        or (opcode1 == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode1 == '1101111' or opcode1 == '0010111' or opcode1 == '0110111'):
                    rd1 = int(self.ir_prevprev[20:25], 2)
                    if rd1 == rd:
                        self.temp = 1
                ############################
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1 and rd == rs2:  # rs1==rs2
                        stall_prev = 0
                    elif (rd == rs1 and rd != rs2) or (rd != rs1 and rd == rs2):
                        stall_prev = 1
                        self.rd_forward_me = rd
                        self.m_e = 1
                    else:
                        stall_prev = 0

            else:
                stall_prev = 0

            if stall_prev != 0 or self.temp == 1:
                self.stall_previns = stall_prev
                stall_number = self.stall_previns
                return stall_number

            else:
                stall_prevprev = 0
                # rs1,rs2 will remain same but opcode and rd will change for the prev_prev instruction
                opcode = self.ir_prevprev[25:]
                if (opcode == '0110011' or opcode == '0010011' or opcode == '0000011'
                        or (opcode == '1100111' and self.ir_prevprev[17:20] == '000')
                        or opcode == '1101111' or opcode == '0010111' or opcode == '0110111'):
                    # R format,I-ori,load,jalr,jal,auipc,lui, E-E Forwarding
                    rd = int(self.ir_prevprev[20:25], 2)  # pc earlier
                    if rd == 0:
                        stall_prevprev = 0
                    else:
                        if rd == rs1 and rd == rs2:
                            stall_prevprev = 0
                        elif (rd == rs1 and rd != rs2) or (rd != rs1 and rd == rs2):
                            stall_prevprev = 0
                            self.rd_forward_me = rd
                            self.m_e = 1
                        else:
                            stall_prevprev = 0

                else:
                    stall_prevprev = 0
                self.stall_previns = stall_prevprev
                stall_number = self.stall_previns
                return stall_number

        elif self.stall_previns != 0:   # Previous instruction is having stall, Means only check for prev. ins. only.
            rs1 = int(self.ir_cur[12:17], 2)  # current pc
            rs2 = int(self.ir_cur[7:12], 2)
            opcode = self.ir_prev[25:]
            if (opcode == '0110011' or opcode == '0010011' or (opcode == '1100111' and self.ir_prev[17:20] == '000')
                    or opcode == '1101111' or opcode == '0010111' or opcode == '0110111'):
                # R format,I-ori,jalr,jal,auipc,lui, E-E Forwarding
                rd = int(self.ir_prev[20:25], 2)  # pc earlier
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1 and rd == rs2:
                        stall_prev = 0
                    elif (rd == rs1 and rd != rs2) or (rd != rs1 and rd == rs2):
                        stall_prev = 0
                        self.rd_forward_ee = rd
                        self.e_e = 1
                    else:
                        stall_prev = 0

            elif opcode == '0000011':  # Load instruction
                rd = int(self.ir_prev[20:25], 2)  # pc earlier
                if rd == 0:
                    stall_prev = 0
                else:
                    if rd == rs1 and rd == rs2:  # rs1==rs2
                        stall_prev = 0
                    elif (rd == rs1 and rd != rs2) or (rd != rs1 and rd == rs2):
                        stall_prev = 1
                        self.rd_forward_me = rd
                        self.m_e = 1
                    else:
                        stall_prev = 0

            else:
                stall_prev = 0

            self.stall_previns = stall_prev
            stall_number = self.stall_previns
            return stall_number

    def dh_AUIPC_LUI(self,pc):
        if self.pc_cur != pc:
            self.pc_prevprev = self.pc_prev
            self.pc_prev = self.pc_cur
            self.pc_cur = pc             # current pc for data hazard but actually it is PC_temp

        else:
            return self.stall_previns

        self.forward_reset()
        self.forward_rd_reset()
        self.stall_previns = 0
        stall_number = self.stall_previns
        return stall_number

    def dh_jal(self,pc):
        if self.pc_cur != pc:
            self.pc_prevprev = self.pc_prev
            self.pc_prev = self.pc_cur
            self.pc_cur = pc             # current pc for data hazard but actually it is PC_temp

        else:
            return self.stall_previns

        self.forward_reset()
        self.forward_rd_reset()
        self.stall_previns = 0
        stall_number = self.stall_previns
        return stall_number

class Stage_Control:
    """
     Whether to run particular stage or not in the pipeline in that clock cycle or not
    """
    def __init__(self):
        '''
        For ending the execution of instruction i.e. if IR - 0xEF000011 the no further instruction present
        1 - For continue stage execution
        0 - Not to continue stage execution
        '''
        self.fetch_decode_sig = 1
        self.decode_execute_sig = 1
        self.execute_memory_sig = 1
        self.memory_write_sig = 1

    def fetchsig(self, string):  # IF all insrtuctions are fetched, then End fetching the instruction
        if string == '0xEF000011' or string == '0xef000011':
            self.fetch_decode_sig = 0

    def fetch(self):
        if self.fetch_decode_sig == 1:
            return True
        else:
            return False

    def decode(self):
        if self.fetch_decode_sig == 1:
            return True
        else:
            self.decode_execute_sig = 0
            return False

    def execute(self):
        if self.decode_execute_sig == 1:
            return True
        else:
            self.execute_memory_sig = 0
            return False

    def memory(self):
        if self.execute_memory_sig == 1:
            return True
        else:
            self.memory_write_sig = 0
            return False

    def write(self):
        if self.memory_write_sig == 1:
            return True
        else:
            return False

class PWB:
    def __init__(self):
        self.rd= ''       # Register
        self.rd_value = '' # Value present in the register

        self.rd_prev = ''  # Prev. Register
        self.rd_value_prev = ''  # Prev. Value present in the register

    def update_pwb(self,rd,rd_value):
        self.rd_prev = self.rd
        self.rd_value_prev = self.rd_value
        self.rd = rd
        self.rd_value = rd_value

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
        if self.knob1 == 1:
            print('Enter value of Knob4:')
            print('1 - To Enable printing information in the pipeline register at the end of each cycle, along with '
                  'cycle number')
            print('0 - To Disable printing information in the pipeline register at the end of each cycle, along with '
                  'cycle number')
            print('Enter your choice : ', end=' ')
            self.knob4 = int(input())
        else:
            print('Knob4 is disabled as no pipeline execution')
            self.knob4 = 0
        if self.knob1 == 1:
            print('Enter value of Knob5:')
            print('This knob will enable printing information in the pipeline register for particular instruction')
            print('Enter 0 - To Disable Knob5')
            print('Enter the instruction number : ', end=' ')
            self.knob5 = int(input())
        else:
            print('Knob5 is disabled as no pipeline execution')
            self.knob5 = 0

        # Components to end the execution of Program
        self.last_pc = ''

        # Hardware for pipeline
        self.stage_sig = Stage_Control()  # End

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
        self.reg1.load(self.ry,'00000')

        # Pipeline Registers
        self.if_id = if_id()
        self.id_ex = id_ex()
        self.ex_mem = ex_mem()
        self.mem_wr = mem_wr()
        self.pwb = PWB()

        # Hardware for Hazard Detection
        self.data_hazard = data_hazard(self.Ins_memory)
        self.stall = 0
        self.count_stall = 0
        self.cal_pc = ''
        self.flush = 0      # 2 - flush two cycles to flush, 0 - not flush

        # Variables for printing
        self.knob5_pc = ''
        pc_count = 0
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

        f = open("Instruction_Memory.mc",'r+')
        line_array = f.readlines()
        for line in line_array:
            pc_count += 1
            words = line.split()
            self.Ins_memory[words[0]] = words[1]
            if self.knob5 != 0 and self.knob5 == pc_count:
                self.knob5_pc = words[0]
            if words[1] == '0xef000011' or words[1] == '0xEF000011':
                self.last_pc = words[0]

        self.mem = {}
        h = open('memory.txt', 'r+')
        line_array1 = h.readlines()
        for line in line_array1:
            line = line.replace(':', ' ')
            words = line.split()
            self.mem[words[0]] = words[1]
        # print(self.mem)

        # Pipeline with forwarding

        # Pipeline without forwarding
        if self.knob1 == 1 and self.knob2 == 1:
            self.predict = predictor(file)  # 1-Bit Branch Prediction initialisation
            # Pipeline Execution
            i = 0  # Iterator
            while (1):
                i += 1
                self.cycles += 1
                print("Cycle Number - " + str(i))
                if i == 1:
                    if self.stage_sig.fetch():
                        self.fetch()
                    if self.knob3 == 1:
                        print(self.reg1.dcreg)
                    if self.knob4 == 1:
                        print('IF_ID Pipeline Register')
                        print(self.if_id.print_if_id())
                        print('ID_EX Pipeline Register')
                        print(self.id_ex.print_id_ex())
                        print('EX_MEM Pipeline Register')
                        print(self.ex_mem.print_ex_mem())
                        print('MEM_WRITE Pipeline Register')
                        print(self.mem_wr.print_mem_wr())

                elif i == 2:
                    if self.stage_sig.decode():
                        self.decode()
                    if self.stall > 0:
                        if self.knob3 == 1:
                            print(self.reg1.dcreg)
                        if self.knob4 == 1:
                            print('IF_ID Pipeline Register')
                            print(self.if_id.print_if_id())
                            print('ID_EX Pipeline Register')
                            print(self.id_ex.print_id_ex())
                            print('EX_MEM Pipeline Register')
                            print(self.ex_mem.print_ex_mem())
                            print('MEM_WRITE Pipeline Register')
                            print(self.mem_wr.print_mem_wr())
                        continue
                    if self.stage_sig.fetch():
                        self.fetch()
                    if self.knob3 == 1:
                        print(self.reg1.dcreg)
                    if self.knob4 == 1:
                        print('IF_ID Pipeline Register')
                        print(self.if_id.print_if_id())
                        print('ID_EX Pipeline Register')
                        print(self.id_ex.print_id_ex())
                        print('EX_MEM Pipeline Register')
                        print(self.ex_mem.print_ex_mem())
                        print('MEM_WRITE Pipeline Register')
                        print(self.mem_wr.print_mem_wr())

                elif i == 3:
                    if self.stage_sig.execute():
                        self.execute()
                    if self.stage_sig.decode():
                        self.decode()
                    if self.stall > 0:
                        if self.knob3 == 1:
                            print(self.reg1.dcreg)
                        if self.knob4 == 1:
                            print('IF_ID Pipeline Register')
                            print(self.if_id.print_if_id())
                            print('ID_EX Pipeline Register')
                            print(self.id_ex.print_id_ex())
                            print('EX_MEM Pipeline Register')
                            print(self.ex_mem.print_ex_mem())
                            print('MEM_WRITE Pipeline Register')
                            print(self.mem_wr.print_mem_wr())
                        continue
                    if self.stage_sig.fetch():
                        self.fetch()
                    if self.knob3 == 1:
                        print(self.reg1.dcreg)
                    if self.knob4 == 1:
                        print('IF_ID Pipeline Register')
                        print(self.if_id.print_if_id())
                        print('ID_EX Pipeline Register')
                        print(self.id_ex.print_id_ex())
                        print('EX_MEM Pipeline Register')
                        print(self.ex_mem.print_ex_mem())
                        print('MEM_WRITE Pipeline Register')
                        print(self.mem_wr.print_mem_wr())

                elif i == 4:
                    if self.stage_sig.memory():
                        self.mem_access()
                    if self.stage_sig.execute():
                        self.execute()
                    if self.stage_sig.decode():
                        self.decode()
                    if self.stall > 0:
                        if self.knob3 == 1:
                            print(self.reg1.dcreg)
                        if self.knob4 == 1:
                            print('IF_ID Pipeline Register')
                            print(self.if_id.print_if_id())
                            print('ID_EX Pipeline Register')
                            print(self.id_ex.print_id_ex())
                            print('EX_MEM Pipeline Register')
                            print(self.ex_mem.print_ex_mem())
                            print('MEM_WRITE Pipeline Register')
                            print(self.mem_wr.print_mem_wr())
                        continue
                    if self.stage_sig.fetch():
                        self.fetch()
                    if self.knob3 == 1:
                        print(self.reg1.dcreg)
                    if self.knob4 == 1:
                        print('IF_ID Pipeline Register')
                        print(self.if_id.print_if_id())
                        print('ID_EX Pipeline Register')
                        print(self.id_ex.print_id_ex())
                        print('EX_MEM Pipeline Register')
                        print(self.ex_mem.print_ex_mem())
                        print('MEM_WRITE Pipeline Register')
                        print(self.mem_wr.print_mem_wr())

                else:
                    if self.stage_sig.write():
                        self.register_update()
                    if self.stage_sig.memory():
                        self.mem_access()
                    if self.stage_sig.execute():
                        self.execute()
                    if self.stage_sig.decode():
                        self.decode()
                    if self.stall > 0:
                        if self.knob3 == 1:
                            print(self.reg1.dcreg)
                        if self.knob4 == 1:
                            print('IF_ID Pipeline Register')
                            print(self.if_id.print_if_id())
                            print('ID_EX Pipeline Register')
                            print(self.id_ex.print_id_ex())
                            print('EX_MEM Pipeline Register')
                            print(self.ex_mem.print_ex_mem())
                            print('MEM_WRITE Pipeline Register')
                            print(self.mem_wr.print_mem_wr())
                        continue
                    if self.stage_sig.fetch():
                        self.fetch()
                    if self.knob3 == 1:
                        print(self.reg1.dcreg)
                    if self.knob4 == 1:
                        print('IF_ID Pipeline Register')
                        print(self.if_id.print_if_id())
                        print('ID_EX Pipeline Register')
                        print(self.id_ex.print_id_ex())
                        print('EX_MEM Pipeline Register')
                        print(self.ex_mem.print_ex_mem())
                        print('MEM_WRITE Pipeline Register')
                        print(self.mem_wr.print_mem_wr())
                if not self.stage_sig.write():
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
            p.write('Number of Stalls/Bubbles in the pipeline : ' + str(self.num_stalls) + '\n')
            self.num_stall_datahz = self.num_stalls - self.num_stall_controlhz
            p.write('Number of data hazards : ' + str(self.num_datahz) + '\n')
            self.num_controlhz = self.num_stall_controlhz / 2
            p.write('Number of control hazards : ' + str(self.num_controlhz) + '\n')
            self.num_misprediction = self.num_controlhz
            p.write('Number of branch mispredictions : ' + str(self.num_misprediction) + '\n')
            p.write('Number of stalls due to data hazards : ' + str(self.num_stall_datahz) + '\n')
            p.write('Number of stalls due to control hazards : ' + str(self.num_stall_controlhz) + '\n')
            print("...... Execution Ended ......")

        # Not Pipelined with Pipeline Registers
        if self.knob1 == 0:
            pass

    def fetch(self):
        if self.flush == 0:
            self.if_id.flush = 0
            IR = self.Ins_memory[self.PC]
            self.stage_sig.fetchsig(IR)
            if self.stage_sig.fetch():
                # print('Fetch')
                self.ex_inst += 1
                IR = bin(int(IR, 16))
                length = 34 - len(IR)
                IR = IR[0:2] + '0' * length + IR[2:]
                IR = IR[2:]
                PC = self.PC  # copy of current PC
                if PC == self.knob5_pc and self.knob5_pc!='':
                    self.if_id.knob5 = 1
                    print('IF_ID Pipeline Register')
                    print(self.if_id.print_if_id())
                    print('ID_EX Pipeline Register')
                    print(self.id_ex.print_id_ex())
                    print('EX_MEM Pipeline Register')
                    print(self.ex_mem.print_ex_mem())
                    print('MEM_WRITE Pipeline Register')
                    print(self.mem_wr.print_mem_wr())
                else:
                    self.if_id.knob5 = 0

                # Branch Prediction
                # bp = branch p. bp = 1 --- Branch Taken, bp = 0 --- Not Taken
                # ta = target address if bp = 1
                bp = 0
                ta = '0x0'
                opcode = IR[25:]
                # print(opcode)
                if opcode == '1101111' or opcode == '1100011':  # Jal, SB
                    bp, ta = self.predict.prediction_jalSB(self.PC)
                if opcode == '1100111' and IR[17:20] == '000':  # Jalr
                    bp, ta = self.predict.prediction_jalr(self.PC, self.reg1, IR)

                if bp == 0:
                    # following steps update PC->PC + 4 using IAG
                    self.IAG.update_fetch(self.PC)
                    self.PC = self.IAG.PC
                    self.PC_temp = self.IAG.PC_temp
                    ta = self.PC
                else:
                    self.PC = ta
                    self.PC_temp = PC
                # updating the if_id buffer with current IR and Current PC
                self.if_id.update(self.PC, IR, self.PC_temp,bp,ta)          # passing bp,ta for flushing if required
                # self.PC - Next instruction address, IR - curr instruction, self.PC_temp = prev. instruction address

        else:
            self.PC = self.cal_pc           # Backward path for next PC calculation
            self.flush = 0
            self.if_id.flush = 1

    def decode(self):
        if self.if_id.flush == 0 and self.flush == 0:
            self.id_ex.flush = 0
            # print('Decode')
            bin_int = self.if_id.ir
            opcode = bin_int[25:]
            if self.if_id.knob5 == 1:
                self.id_ex.knob5 = 1
                print('IF_ID Pipeline Register')
                print(self.if_id.print_if_id())
                print('ID_EX Pipeline Register')
                print(self.id_ex.print_id_ex())
                print('EX_MEM Pipeline Register')
                print(self.ex_mem.print_ex_mem())
                print('MEM_WRITE Pipeline Register')
                print(self.mem_wr.print_mem_wr())
            else:
                self.id_ex.knob5 = 0

            if opcode == '0110011':  # R format
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

                self.stall = self.data_hazard.dh_R(self.if_id.prevpc)  # It returns how many stalls to do
                # print('Stalls :')
                # print(self.stall)
                if self.count_stall == self.stall:
                    self.ex_inst += 1
                    self.alu_inst += 1
                    con_ee = self.data_hazard.e_e
                    con_me = self.data_hazard.m_e
                    con_mm = self.data_hazard.m_m
                    con_pwm = self.data_hazard.pw_m
                    rd_ee = self.data_hazard.rd_forward_ee
                    rd_me = self.data_hazard.rd_forward_me
                    rd_mm = self.data_hazard.rd_forward_mm
                    rd_pwm = self.data_hazard.rd_forward_pwm
                    self.id_ex.update_R(self.con_mux['A'],self.con_mux['B'],self.con_mux['Y'],self.con_mux['E'],rd,
                                        rs1,rs2,opcode,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,con_pwm,rd_pwm)
                    self.id_ex.stall = 0
                    self.count_stall = 0
                    self.stall = 0
                else:
                    if self.count_stall == 0:
                        self.num_datahz += 1
                    self.num_stalls += 1
                    self.count_stall += 1
                    self.id_ex.stall = 1

            elif opcode == '0010011':  # I format-andi,addi,ori
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

                self.stall = self.data_hazard.dh_Immediate(self.if_id.prevpc)  # It returns how many stalls to do
                # print('Stalls:')
                # print(self.stall)
                if self.count_stall == self.stall:
                    self.ex_inst += 1
                    self.alu_inst += 1
                    con_ee = self.data_hazard.e_e
                    con_me = self.data_hazard.m_e
                    con_mm = self.data_hazard.m_m
                    con_pwm = self.data_hazard.pw_m
                    rd_ee = self.data_hazard.rd_forward_ee
                    rd_me = self.data_hazard.rd_forward_me
                    rd_mm = self.data_hazard.rd_forward_mm
                    rd_pwm = self.data_hazard.rd_forward_pwm
                    self.id_ex.update_I(self.con_mux['A'],self.con_mux['B'],self.con_mux['Y'],self.con_mux['E'], rd,
                                        opcode,rs1,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,con_pwm,rd_pwm)
                    self.id_ex.stall = 0
                    self.count_stall = 0
                    self.stall = 0
                else:
                    if self.count_stall == 0:
                        self.num_datahz += 1
                    self.num_stalls += 1
                    self.count_stall += 1
                    self.id_ex.stall = 1

            elif opcode == '0000011':  # load instructions
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

                self.stall = self.data_hazard.dh_Load(self.if_id.prevpc)  # It returns how many stalls to do
                # print('Stalls:')
                # print(self.stall)
                if self.count_stall == self.stall:
                    self.ex_inst += 1
                    self.data_trasf += 1
                    self.alu_inst += 1
                    con_ee = self.data_hazard.e_e
                    con_me = self.data_hazard.m_e
                    con_mm = self.data_hazard.m_m
                    con_pwm = self.data_hazard.pw_m
                    rd_ee = self.data_hazard.rd_forward_ee
                    rd_me = self.data_hazard.rd_forward_me
                    rd_mm = self.data_hazard.rd_forward_mm
                    rd_pwm = self.data_hazard.rd_forward_pwm
                    self.id_ex.update_load(rd,self.con_mux['A'],self.con_mux['B'],self.con_mux['Y'],self.con_mux['E'],
                                           muxY_byte_update, opcode,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,con_pwm,
                                           rd_pwm)
                    self.id_ex.stall = 0
                    self.count_stall = 0
                    self.stall = 0
                else:
                    if self.count_stall == 0:
                        self.num_datahz += 1
                    self.num_stalls += 1
                    self.count_stall += 1
                    self.id_ex.stall = 1

            elif opcode == '1100111' and bin_int[17:20] == '000':  # jalr
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

                self.stall = self.data_hazard.dh_jalr(self.if_id.prevpc)  # It returns how many stalls to do
                # print('Stalls:')
                # print(self.stall)
                if self.count_stall == self.stall:
                    self.ex_inst += 1
                    self.control_inst += 1
                    con_ee = self.data_hazard.e_e
                    con_me = self.data_hazard.m_e
                    con_mm = self.data_hazard.m_m
                    con_pwm = self.data_hazard.pw_m
                    rd_ee = self.data_hazard.rd_forward_ee
                    rd_me = self.data_hazard.rd_forward_me
                    rd_mm = self.data_hazard.rd_forward_mm
                    rd_pwm = self.data_hazard.rd_forward_pwm
                    self.id_ex.update_jalr(self.con_mux['E'],self.con_mux['PC'],self.con_mux['INC'],self.con_mux['Y'],
                                           imm1, muxINC_update,opcode,self.if_id.prevpc,self.if_id.pc,RA,
                                           rd,self.if_id.bp,self.if_id.ta,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,
                                           con_pwm,rd_pwm)
                    self.id_ex.stall = 0
                    self.count_stall = 0
                    self.stall = 0
                else:
                    if self.count_stall == 0:
                        self.num_datahz += 1
                    self.num_stalls += 1
                    self.count_stall += 1
                    self.id_ex.stall = 1

            elif opcode == '1101111':  # jal
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
                self.stall = self.data_hazard.dh_jal(self.if_id.prevpc)  # It returns how many stalls to do
                # print('Stalls:')
                # print(self.stall)
                if self.count_stall == self.stall:
                    self.ex_inst += 1
                    self.control_inst += 1
                    con_ee = self.data_hazard.e_e
                    con_me = self.data_hazard.m_e
                    con_mm = self.data_hazard.m_m
                    con_pwm = self.data_hazard.pw_m
                    rd_ee = self.data_hazard.rd_forward_ee
                    rd_me = self.data_hazard.rd_forward_me
                    rd_mm = self.data_hazard.rd_forward_mm
                    rd_pwm = self.data_hazard.rd_forward_pwm
                    self.id_ex.update_jal(self.con_mux['E'],self.con_mux['PC'],self.con_mux['INC'],self.con_mux['Y'],
                                          imm1, muxINC_update, opcode, self.if_id.prevpc, self.if_id.pc,
                                          rd,self.if_id.bp, self.if_id.ta,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,
                                          con_pwm,rd_pwm)
                    self.id_ex.stall = 0
                    self.count_stall = 0
                    self.stall = 0
                else:
                    if self.count_stall == 0:
                        self.num_datahz += 1
                    self.num_stalls += 1
                    self.count_stall += 1
                    self.id_ex.stall = 1

            elif opcode == '0010111' or opcode == '0110111':  # U(auipc or lui)
                rd = bin_int[20:25]
                imm = bin_int[0:20] + '0' * 12
                imm1 = convert_to_hex_extend(imm)
                self.muxB.update(imm1, 1)
                # self.muxA.update(self.PC_temp, 1)
                self.muxA.update(self.if_id.prevpc, 1)
                self.reg1.reg_extract(rd, self.muxA, self.muxB, '00000', '00000')
                self.con_mux['B'] = '1'
                self.con_mux['E'] = '1'
                self.con_mux['Y'] = '00'
                self.alu.con_update(self.control_ALU['+'])
                if opcode == '0010111':
                    self.con_mux['A'] = '1'
                else:
                    self.con_mux['A'] = '0'
                self.stall = self.data_hazard.dh_AUIPC_LUI(self.if_id.prevpc)  # It returns how many stalls to do
                # print('Stalls:')
                # print(self.stall)
                if self.count_stall == self.stall:
                    self.ex_inst += 1
                    self.alu_inst += 1
                    con_ee = self.data_hazard.e_e
                    con_me = self.data_hazard.m_e
                    con_mm = self.data_hazard.m_m
                    con_pwm = self.data_hazard.pw_m
                    rd_ee = self.data_hazard.rd_forward_ee
                    rd_me = self.data_hazard.rd_forward_me
                    rd_mm = self.data_hazard.rd_forward_mm
                    rd_pwm = self.data_hazard.rd_forward_pwm
                    self.id_ex.update_auipc_lui(rd,self.con_mux['A'],self.con_mux['B'],self.con_mux['Y'],
                                                self.con_mux['E'], opcode,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,
                                                con_pwm,rd_pwm)
                    self.id_ex.stall = 0
                    self.count_stall = 0
                    self.stall = 0
                else:
                    if self.count_stall == 0:
                        self.num_datahz += 1
                    self.num_stalls += 1
                    self.count_stall += 1
                    self.id_ex.stall = 1

            elif opcode == '1100011':  # SB format
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

                self.stall = self.data_hazard.dh_SB(self.if_id.prevpc)  # It returns how many stalls to do
                # print('Stalls:')
                # print(self.stall)
                if self.count_stall == self.stall:
                    self.ex_inst += 1
                    self.control_inst += 1
                    con_ee = self.data_hazard.e_e
                    con_me = self.data_hazard.m_e
                    con_mm = self.data_hazard.m_m
                    con_pwm = self.data_hazard.pw_m
                    rd_ee = self.data_hazard.rd_forward_ee
                    rd_me = self.data_hazard.rd_forward_me
                    rd_mm = self.data_hazard.rd_forward_mm
                    rd_pwm = self.data_hazard.rd_forward_pwm
                    self.id_ex.update_sb(self.con_mux['A'],self.con_mux['B'],self.con_mux['Y'],self.con_mux['E'], imm1,
                                         muxINC_update, opcode, self.if_id.prevpc, self.if_id.pc,
                                         self.if_id.bp,self.if_id.ta,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,con_pwm,
                                         rd_pwm)
                    self.id_ex.stall = 0
                    self.count_stall = 0
                    self.stall = 0
                else:
                    if self.count_stall == 0:
                        self.num_datahz += 1
                    self.num_stalls += 1
                    self.count_stall += 1
                    self.id_ex.stall = 1

            elif opcode == '0100011':  # S format
                funct3 = bin_int[17:20]
                if funct3 == '011':
                    print("Not supported instruction!")
                    return 1
                rs1 = bin_int[12:17]  # For effective address
                rs2 = bin_int[7:12]  # value to be stored
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

                self.stall = self.data_hazard.dh_store(self.if_id.prevpc)  # It returns how many stalls to do
                # print('Stalls:')
                # print(self.stall)
                if self.count_stall == self.stall:
                    self.ex_inst += 1
                    self.data_trasf += 1
                    self.alu_inst += 1
                    con_ee = self.data_hazard.e_e
                    con_me = self.data_hazard.m_e
                    con_mm = self.data_hazard.m_m
                    con_pwm = self.data_hazard.pw_m
                    rd_ee = self.data_hazard.rd_forward_ee
                    rd_me = self.data_hazard.rd_forward_me
                    rd_mm = self.data_hazard.rd_forward_mm
                    rd_pwm = self.data_hazard.rd_forward_pwm
                    self.id_ex.update_S(self.con_mux['A'],self.con_mux['B'],self.con_mux['Y'],self.con_mux['E']
                                        , rm, muxY_byte_update, opcode,con_ee,rd_ee,con_me,rd_me,con_mm,rd_mm,con_pwm,
                                        rd_pwm)
                    self.id_ex.stall = 0
                    self.count_stall = 0
                    self.stall = 0
                else:
                    if self.count_stall == 0:
                        self.num_datahz += 1
                    self.num_stalls += 1
                    self.count_stall += 1
                    self.id_ex.stall = 1

        else:
            if self.flush != 0:
                self.flush -=1
            else:
                self.flush =0
            self.id_ex.flush = 1

    def execute(self):
        if self.id_ex.flush == 0:
            self.ex_mem.flush = 0
            if self.id_ex.stall == 0:
                self.ex_inst += 1
                if self.id_ex.knob5 == 1:
                    self.ex_mem.knob5 = 1
                    print('IF_ID Pipeline Register')
                    print(self.if_id.print_if_id())
                    print('ID_EX Pipeline Register')
                    print(self.id_ex.print_id_ex())
                    print('EX_MEM Pipeline Register')
                    print(self.ex_mem.print_ex_mem())
                    print('MEM_WRITE Pipeline Register')
                    print(self.mem_wr.print_mem_wr())
                else:
                    self.ex_mem.knob5 = 0
                # print('EXECUTE')
                if self.id_ex.con_e == '0':  # used in jal and jalr
                    temp = self.id_ex.PC_temp
                    # calculating PC + 4 for the branch target arrangement
                    var1 = int(temp[2:],16)
                    var2 = 4
                    PC_temp = hex(var1+var2)
                    # PC_temp = self.id_ex.PC  # we need to store PC+4 in PC_temp for transfer as input to MuxY
                    PC = ''
                    if self.id_ex.opcode == '1101111':         # jal
                        PC = temp  # PC set to original PC (i.e. before fetch stage incremented it by 4)
                        length = 10 - len(PC)
                        PC = PC[0:2] + '0' * length + PC[2:]
                    if self.id_ex.opcode == '1100111':  # for jalr - PC set as RA
                        RA = ''
                        if self.id_ex.con_ee == 0 and self.id_ex.con_me == 0:    # Normal working
                            RA = self.id_ex.RA
                        elif self.id_ex.con_ee == 1 and self.id_ex.con_me == 0:
                            RA = self.ex_mem.rz
                        elif self.id_ex.con_ee == 0 and self.id_ex.con_me == 1:
                            RA = self.mem_wr.ry_out
                        self.muxPC.update(RA, 0)
                        self.muxPC.control(self.id_ex.con_pc)
                        PC = self.muxPC.out
                    self.muxINC.update(self.id_ex.imm, 1)
                    self.muxINC.control(self.id_ex.con_inc)
                    self.adder.in_update(PC, self.muxINC.out)
                    self.adder.control(self.id_ex.opcode)
                    self.muxPC.update(self.adder.out, 1)
                    self.muxPC.control('1')
                    # self.PC = self.muxPC.out  # updated New PC                # for jal, jalr
                    self.cal_pc = self.muxPC.out  # calculated true pc to jump
                    if self.cal_pc != self.id_ex.ta:
                        self.predict.update_predict(False, self.id_ex.PC_temp)
                        # Flushing of the code
                        self.flush = 2
                        self.num_stalls += 2
                        self.num_stall_controlhz += 2
                    self.ex_mem.branch(PC_temp, self.id_ex.rd,self.id_ex.con_y,self.id_ex.con_mm,self.id_ex.rd_mm,
                                       self.id_ex.con_pwm,self.id_ex.rd_pwm)
                    self.ex_mem.stall = 0

                else:
                    if self.id_ex.con_ee == 0 and self.id_ex.con_me == 0:       # Normal Working
                        self.muxA.control(self.id_ex.con_a)
                        self.alu.in_update(self.muxA.out, '0')
                        self.muxB.control(self.id_ex.con_b)
                        self.alu.in_update(self.muxB.out, '1')
                        self.id_ex.con_inc = self.alu.control  # muxINC signal used in SB instructions
                        if self.id_ex.con_y == '11' and self.id_ex.con_inc == '1':
                            if self.id_ex.opcode == '1100011':
                                PC = self.id_ex.PC_temp
                                self.muxINC.update(self.id_ex.imm, 1)
                                self.muxINC.control(self.id_ex.con_inc)
                                self.adder.in_update(PC, self.muxINC.out)
                                self.adder.control(self.id_ex.opcode)
                                self.muxPC.update(self.adder.out, 1)
                                self.muxPC.control('1')
                                # self.PC = self.muxPC.out  # updated New PC          # For SB format
                                self.cal_pc = self.muxPC.out         # calculated true pc to jump
                                if self.cal_pc != self.id_ex.ta:
                                    self.predict.update_predict(False,self.id_ex.PC_temp)
                                    # Flushing of the code
                                    self.flush = 2
                                    self.num_stalls += 2
                                    self.num_stall_controlhz += 2
                            else:
                                pass
                                # print("EXECUTE: Branch not taken and PC is incremented by 4")
                        self.rz = self.alu.out
                    elif self.id_ex.con_ee == 1 and self.id_ex.con_me == 0:
                        if self.id_ex.opcode == '0110011' or self.id_ex.opcode == '1100011':       # R format,SB format
                            rs1 = int(self.id_ex.rs1,2)
                            rs2 = int(self.id_ex.rs2,2)
                            rd = self.id_ex.rd_ee
                            if rs1==rd and rs2 != rd:
                                self.alu.in_update(self.ex_mem.rz,'0')
                                self.muxB.control(self.id_ex.con_b)
                                self.alu.in_update(self.muxB.out, '1')
                            if rs2 == rd and rs1 != rd:
                                self.alu.in_update(self.ex_mem.rz,'1')
                                self.muxA.control(self.id_ex.con_a)
                                self.alu.in_update(self.muxA.out, '0')
                            if rs2 == rd and rs1 == rd:
                                self.alu.in_update(self.ex_mem.rz, '0')
                                self.alu.in_update(self.ex_mem.rz, '1')

                        if (self.id_ex.opcode == '0010011' or self.id_ex.opcode == '0010011'
                                or self.id_ex.opcode == '0100011'):
                            self.alu.in_update(self.ex_mem.rz, '0')           # I format, Load,Store
                            self.muxB.control(self.id_ex.con_b)
                            self.alu.in_update(self.muxB.out, '1')

                        self.id_ex.con_inc = self.alu.control  # muxINC signal used in SB instructions
                        if self.id_ex.con_y == '11' and self.id_ex.con_inc == '1':
                            if self.id_ex.opcode == '1100011':
                                PC = self.id_ex.PC_temp
                                self.muxINC.update(self.id_ex.imm, 1)
                                self.muxINC.control(self.id_ex.con_inc)
                                self.adder.in_update(PC, self.muxINC.out)
                                self.adder.control(self.id_ex.opcode)
                                self.muxPC.update(self.adder.out, 1)
                                self.muxPC.control('1')
                                # self.PC = self.muxPC.out  # updated New PC          # For SB format
                                self.cal_pc = self.muxPC.out         # calculated true pc to jump
                                if self.cal_pc != self.id_ex.ta:
                                    self.predict.update_predict(False,self.id_ex.PC_temp)
                                    # Flushing of the code
                                    self.flush = 2
                                    self.num_stalls += 2
                                    self.num_stall_controlhz += 2
                            else:
                                pass
                                # print("EXECUTE: Branch not taken and PC is incremented by 4")
                        self.rz = self.alu.out  # common for all
                    elif self.id_ex.con_ee == 0 and self.id_ex.con_me == 1:
                        if self.id_ex.opcode == '0110011' or self.id_ex.opcode == '1100011':       # For R format
                            rs1 = int(self.id_ex.rs1, 2)
                            rs2 = int(self.id_ex.rs2, 2)
                            rd = self.id_ex.rd_me
                            if rs1 == rd and rs2 != rd:
                                self.alu.in_update(self.mem_wr.ry_out, '0')
                                self.muxB.control(self.id_ex.con_b)
                                self.alu.in_update(self.muxB.out, '1')
                            if rs2 == rd and rs1 != rd:
                                self.alu.in_update(self.mem_wr.ry_out, '1')
                                self.muxA.control(self.id_ex.con_a)
                                self.alu.in_update(self.muxA.out, '0')
                            if rs2 == rd and rs1 == rd:
                                self.alu.in_update(self.mem_wr.ry_out, '0')
                                self.alu.in_update(self.mem_wr.ry_out, '1')

                        if (self.id_ex.opcode == '0010011' or self.id_ex.opcode == '0010011'
                                or self.id_ex.opcode == '0100011'):              # I format
                            self.alu.in_update(self.mem_wr.ry_out, '0')
                            self.muxB.control(self.id_ex.con_b)
                            self.alu.in_update(self.muxB.out, '1')

                        self.id_ex.con_inc = self.alu.control
                        if self.id_ex.con_y == '11' and self.id_ex.con_inc == '1':
                            if self.id_ex.opcode == '1100011':
                                PC = self.id_ex.PC_temp
                                self.muxINC.update(self.id_ex.imm, 1)
                                self.muxINC.control(self.id_ex.con_inc)
                                self.adder.in_update(PC, self.muxINC.out)
                                self.adder.control(self.id_ex.opcode)
                                self.muxPC.update(self.adder.out, 1)
                                self.muxPC.control('1')
                                # self.PC = self.muxPC.out  # updated New PC          # For SB format
                                self.cal_pc = self.muxPC.out         # calculated true pc to jump
                                if self.cal_pc != self.id_ex.ta:
                                    self.predict.update_predict(False,self.id_ex.PC_temp)
                                    # Flushing of the code
                                    self.flush = 2
                                    self.num_stalls += 2
                                    self.num_stall_controlhz += 2
                            else:
                                pass
                                # print("EXECUTE: Branch not taken and PC is incremented by 4")
                        self.rz = self.alu.out  # common for all

                    elif self.id_ex.con_ee == 1 and self.id_ex.con_me == 1:
                        if self.id_ex.opcode == '0110011' or self.id_ex.opcode == '1100011':  # For R format, SB format
                            rs1 = int(self.id_ex.rs1, 2)
                            rs2 = int(self.id_ex.rs2, 2)
                            rd_ee = self.id_ex.rd_ee
                            rd_me = self.id_ex.rd_me
                            if rs1==rd_ee and rs2==rd_me:
                                self.alu.in_update(self.ex_mem.rz, '0')
                                self.alu.in_update(self.mem_wr.ry_out, '1')
                            elif rs2==rd_ee and rs1==rd_me:
                                self.alu.in_update(self.ex_mem.rz, '1')
                                self.alu.in_update(self.mem_wr.ry_out, '0')

                        self.id_ex.con_inc = self.alu.control
                        if self.id_ex.con_y == '11' and self.id_ex.con_inc == '1':
                            if self.id_ex.opcode == '1100011':
                                PC = self.id_ex.PC_temp
                                self.muxINC.update(self.id_ex.imm, 1)
                                self.muxINC.control(self.id_ex.con_inc)
                                self.adder.in_update(PC, self.muxINC.out)
                                self.adder.control(self.id_ex.opcode)
                                self.muxPC.update(self.adder.out, 1)
                                self.muxPC.control('1')
                                # self.PC = self.muxPC.out  # updated New PC          # For SB format
                                self.cal_pc = self.muxPC.out         # calculated true pc to jump
                                if self.cal_pc != self.id_ex.ta:
                                    self.predict.update_predict(False,self.id_ex.PC_temp)
                                    # Flushing of the code
                                    self.flush = 2
                                    self.num_stalls += 2
                                    self.num_stall_controlhz += 2
                            else:
                                pass
                                # print("EXECUTE: Branch not taken and PC is incremented by 4")
                        self.rz = self.alu.out  # common for all

                    self.ex_mem.nonbranch_SB(self.id_ex.con_y, self.id_ex.opcode, self.id_ex.muxY_byte_update,
                                             self.id_ex.rm, self.id_ex.rd, self.id_ex.imm, self.id_ex.PC_temp,self.rz
                                             ,self.id_ex.con_mm,self.id_ex.rd_mm,self.id_ex.con_pwm,self.id_ex.rd_pwm)
                    self.ex_mem.stall = 0

            else:
                self.ex_mem.stall = 1

        else:
            self.ex_mem.flush = 1

    def mem_access(self):
        # print('Memory')
        if self.ex_mem.flush == 0:
            self.mem_wr.flush = 0
            if self.ex_mem.stall == 0:
                self.ex_inst += 1
                if self.ex_mem.knob5 == 1:
                    self.mem_wr.knob5 = 1
                    print('IF_ID Pipeline Register')
                    print(self.if_id.print_if_id())
                    print('ID_EX Pipeline Register')
                    print(self.id_ex.print_id_ex())
                    print('EX_MEM Pipeline Register')
                    print(self.ex_mem.print_ex_mem())
                    print('MEM_WRITE Pipeline Register')
                    print(self.mem_wr.print_mem_wr())
                else:
                    self.mem_wr.knob5 = 0

                if self.ex_mem.con_y == '00':  # for R format, I format(ALU),auipc and lui instructions
                    self.muxY.update(self.rz, 0)
                    # print("MEMORY ACCESS: No work!")

                elif self.ex_mem.con_y == '01':  # for load and store instructions
                    self.MAR = self.rz
                    if self.ex_mem.opcode == '0000011':
                        self.MDR = load_from_memory(self.MAR, self.ex_mem.muxY_byte_update,self.mem)
                        # obtains data at required memory address and stores it in MDR

                    elif self.ex_mem.opcode == '0100011':      # Store
                        if self.ex_mem.con_mm == 0 and self.ex_mem.con_pwm == 0:
                            self.MDR = self.ex_mem.rm
                            store_to_memory(self.MAR, self.MDR, self.mem)  # MDR is restored to '0x00000000'
                        elif self.ex_mem.con_mm == 1 and self.ex_mem.con_pwm == 0:
                            self.MDR = self.mem_wr.ry_out
                            store_to_memory(self.MAR, self.MDR, self.mem)  # MDR is restored to '0x00000000'
                        elif self.ex_mem.con_mm == 0 and self.ex_mem.con_pwm == 1:
                            self.MDR = self.pwb.rd_value_prev
                            store_to_memory(self.MAR, self.MDR, self.mem)  # MDR is restored to '0x00000000'

                    self.muxY.update(self.MDR, 1)

                elif self.ex_mem.con_y == '10':  # for jal and jalr instructions
                    self.muxY.update(self.ex_mem.rz, 2)

                elif self.ex_mem.con_y == '11':  # for SB format instructions
                    self.muxY.update(self.ex_mem.rz, 0)
                self.muxY.control(self.ex_mem.con_y)
                self.ry = self.muxY.out
                self.mem_wr.update_in(self.ex_mem.rd, self.ex_mem.opcode,self.ry)
                self.mem_wr.stall = 0

            else:
                self.mem_wr.stall = 1
        else:
            self.mem_wr.flush = 1

    def register_update(self):
        # print('Register')
        self.ex_inst += 1
        if self.mem_wr.knob5 == 1:
            print('IF_ID Pipeline Register')
            print(self.if_id.print_if_id())
            print('ID_EX Pipeline Register')
            print(self.id_ex.print_id_ex())
            print('EX_MEM Pipeline Register')
            print(self.ex_mem.print_ex_mem())
            print('MEM_WRITE Pipeline Register')
            print(self.mem_wr.print_mem_wr())

        self.mem_wr.update_out()
        if self.mem_wr.flush == 0:
            if self.mem_wr.stall == 0:
                # print('REGISTER UPDATE')
                # 0100011 - store, 1100011 - SB format
                if (self.mem_wr.opcode_out == "0100011" or self.mem_wr.opcode_out == "1100011" or
                        self.mem_wr.rd_out == '00000'):
                    # print("WRITEBACK: No work!")
                    pass
                else:
                    self.reg1.load(self.mem_wr.ry_out, self.mem_wr.rd_out)
                    # print("WRITEBACK: Write " + self.mem_wr.ry_out + " into x" + str(int(self.mem_wr.rd_out, 2)))
                    self.pwb.update_pwb(self.mem_wr.rd_out,self.mem_wr.ry_out)    # ------------ New update
                    # print(self.pwb.print_pwb())
            else:
                pass
        else:
            pass

if __name__ == '__main__':
    # print(':::::::::::: Pipeline Execution ::::::::::::')
    start = phase3("Instruction_Memory.mc")
