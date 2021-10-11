class Machine_code:
    def __init__(self, words,program_counter,label_dict):
        self.words = words
        self.program_counter = program_counter
        self.label_dict = label_dict

    def generate(self):
        bin = ''
        if (self.words[0] == 'add' or self.words[0] == 'and' or self.words[0] == 'or' or self.words[0] == 'sll' or
                self.words[0] == 'slt' or
                self.words[0] == 'sra' or self.words[0] == 'srl' or self.words[0] == 'sub' or self.words[0] == 'xor' or
                self.words[0] == 'mul' or
                self.words[0] == 'div' or self.words[0] == 'rem'):
            bin = self.rformat

        elif (self.words[0] == 'addi' or self.words[0] == 'andi' or self.words[0] == 'ori' or self.words[0] == 'lb' or
              self.words[0] == 'ld' or self.words[0] == 'lh' or self.words[0] == 'lw' or self.words[0] == 'jalr'):
            bin = self.iformat

        elif self.words[0] == 'sb' or self.words[0] == 'sw' or self.words[0] == 'sd' or self.words[0] == 'sh':
            bin = self.sformat

        elif self.words[0] == 'beq' or self.words[0] == 'bne' or self.words[0] == 'bge' or self.words[0] == 'blt':
            bin = self.sbformat

        elif self.words[0] == 'auipc' or self.words[0] == 'lui':
            bin = self.uformat

        elif self.words[0] == 'jal':
            bin = self.ujformat
        else:
            bin='-1'
        bin = int(bin, 2)
        bin = hex(bin)
        length = 8 - (len(bin) - 2)
        ze = '0' * length
        bin = bin[0:2] + ze + bin[2:]
        return bin

    @property               ##  Because generator function is calling another function then it returns the value
    def rformat(self):
        rs1 = integer_to_bin_5_unsigned(self.words[2])
        rs2 = integer_to_bin_5_unsigned(self.words[3])
        rd = integer_to_bin_5_unsigned(self.words[1])
        opcode = "0110011"
        funct3 = ''
        funct7 = ''
        if self.words[0] == 'add':
            funct3 = "000"
            funct7 = "0000000"
        elif self.words[0] == 'and':
            funct3 = "111"
            funct7 = "0000000"
        elif self.words[0] == 'or':
            funct3 = "110"
            funct7 = "0000000"
        elif self.words[0] == 'sll':
            funct3 = "001"
            funct7 = "0000000"
        elif self.words[0] == 'slt':
            funct3 = "010"
            funct7 = "0000000"
        elif self.words[0] == 'sra':
            funct3 = "101"
            funct7 = "0100000"
        elif self.words[0] == 'srl':
            funct3 = "101"
            funct7 = "0000000"
        elif self.words[0] == 'sub':
            funct3 = "000"
            funct7 = "0100000"
        elif self.words[0] == 'xor':
            funct3 = "100"
            funct7 = "0000000"
        elif self.words[0] == 'mul':
            funct3 = "000"
            funct7 = "0000001"
        elif self.words[0] == 'div':
            funct3 = "100"
            funct7 = "0000001"
        elif self.words[0] == 'rem':
            funct3 = "110"
            funct7 = "0000001"
        bin = funct7 + rs2 + rs1 + funct3 + rd + opcode
        return bin


    @property
    def iformat(self):
        rd = integer_to_bin_5_unsigned(self.words[1])
        opcode = ''
        funct3 = ''
        immediate = ''
        rs1 = ''
        if self.words[0] == 'addi':
            rs1 = integer_to_bin_5_unsigned(self.words[2])
            if self.words[3][0:2] == '0x':
                immediate = integer_to_bin_signed(str(int(self.words[3][2:],16)), 12)
            else:
                immediate = integer_to_bin_signed(self.words[3], 12)
            opcode = "0010011"
            funct3 = "000"
        elif self.words[0] == 'ori':
            rs1 = integer_to_bin_5_unsigned(self.words[2])
            if self.words[3][0:2] == '0x':
                immediate = integer_to_bin_signed(str(int(self.words[3][2:], 16)), 12)
            else:
                immediate = integer_to_bin_signed(self.words[3], 12)
            opcode = "0010011"
            funct3 = "110"
        elif self.words[0] == 'andi':
            rs1 = integer_to_bin_5_unsigned(self.words[2])
            if self.words[3][0:2] == '0x':
                immediate = integer_to_bin_signed(str(int(self.words[3][2:],16)), 12)
            else:
                immediate = integer_to_bin_signed(self.words[3], 12)
            opcode = "0010011"
            funct3 = "111"
        elif self.words[0] == 'lb':
            self.words[2] = self.words[2].replace('(', ' ')
            self.words[2] = self.words[2].replace(')', '')
            sub = self.words[2].split()
            rs1 = integer_to_bin_5_unsigned(sub[1])
            if sub[0][0:2] == '0x':
                immediate = integer_to_bin_signed(str(int(sub[0][2:], 16)),12)
            else:
                immediate = integer_to_bin_signed(sub[0], 12)
            opcode = "0000011"
            funct3 = "000"
        elif self.words[0] == 'ld':
            self.words[2] = self.words[2].replace('(', ' ')
            self.words[2] = self.words[2].replace(')', '')
            sub = self.words[2].split()
            rs1 = integer_to_bin_5_unsigned(sub[1])
            if sub[0][0:2] == '0x':
                immediate = integer_to_bin_signed(str(int(sub[0][2:], 16)), 12)
            else:
                immediate = integer_to_bin_signed(sub[0], 12)
            funct3 = "011"
            opcode = "0000011"
        elif self.words[0] == 'lh':
            self.words[2] = self.words[2].replace('(', ' ')
            self.words[2] = self.words[2].replace(')', '')
            sub = self.words[2].split()
            rs1 = integer_to_bin_5_unsigned(sub[1])
            if sub[0][0:2] == '0x':
                immediate = integer_to_bin_signed(str(int(sub[0][2:], 16)), 12)
            else:
                immediate = integer_to_bin_signed(sub[0], 12)
            funct3 = "001"
            opcode = "0000011"
        elif self.words[0] == 'lw':
            self.words[2] = self.words[2].replace('(', ' ')
            self.words[2] = self.words[2].replace(')', '')
            sub = self.words[2].split()
            rs1 = integer_to_bin_5_unsigned(sub[1])
            if sub[0][0:2] == '0x':
                immediate = integer_to_bin_signed(str(int(sub[0][2:], 16)), 12)
            else:
                immediate = integer_to_bin_signed(sub[0], 12)
            funct3 = "010"
            opcode = "0000011"
        elif self.words[0] == 'jalr':
            if self.words[2][-1]==')':
                self.words[2] = self.words[2].replace('(', ' ')
                self.words[2] = self.words[2].replace(')', '')
                sub = self.words[2].split()
                rs1 = integer_to_bin_5_unsigned(sub[1])
                if sub[0][0:2] == '0x':
                    immediate = integer_to_bin_signed(str(int(sub[0][2:], 16)), 12)
                else:
                    immediate = integer_to_bin_signed(sub[0], 12)
            else:
                rs1 = integer_to_bin_5_unsigned(self.words[2])
                if self.words[3][0:2] == '0x':
                    immediate = integer_to_bin_signed(str(int(self.words[3][2:], 16)), 12)
                else:
                    immediate = integer_to_bin_signed(self.words[3], 12)
            opcode = "1100111"
            funct3 = "000"
        bin = immediate + rs1 + funct3 + rd + opcode
        return bin

    @property
    def sformat(self):
        rs1 = integer_to_bin_5_unsigned(self.words[1])
        self.words[2] = self.words[2].replace('(', ' ')
        self.words[2] = self.words[2].replace(')', '')
        sub = self.words[2].split()
        rs2 = integer_to_bin_5_unsigned(sub[1])
        if sub[0][0:2] == '0x':
            immediate = integer_to_bin_signed(str(int(sub[0][2:], 16)),12)
        else:
            immediate = integer_to_bin_signed(sub[0], 12)
        opcode = "0100011"
        funct3 = ''
        if self.words[0] == 'sb':
            funct3 = '000'
        elif self.words[0] == 'sw':
            funct3 = '010'
        elif self.words[0] == 'sd':
            funct3 = '011'
        elif self.words[0] == 'sh':
            funct3 = '001'
        bin = immediate[0:7] + rs1 + rs2 + funct3 + immediate[7:] + opcode
        return bin

    @property
    def sbformat(self):
        opcode='1100011'
        rs1 = integer_to_bin_5_unsigned(self.words[1])
        rs2 = integer_to_bin_5_unsigned(self.words[2])
        funct3 = ''
        if self.words[0]=='beq':
            funct3='000'
        elif self.words[0]=='bne':
            funct3='001'
        elif self.words[0]=='blt':
            funct3='100'
        elif self.words[0]=='bge':
            funct3='101'
        temp=0
        for char in self.words[3]:
            if char.isalpha():
                temp=temp+1
        if temp>0:
            relative_pc = self.label_dict[self.words[3]][1] - self.program_counter
            # print(relative_pc)
            immediate = (integer_to_bin_signed(relative_pc,13))
            # print(immediate)
        else:
            if (int(self.words[3])%2)==1:
                self.words[3]=str(int(self.words[3])-1)
            # print(self.words[3])
            immediate=integer_to_bin_signed(self.words[3],13)
        bin = immediate[0]+immediate[2:8]+ rs2 + rs1 + funct3 + immediate[8:12]+immediate[1]+ opcode
        return bin

    @property
    def uformat(self):
        rs1 = integer_to_bin_5_unsigned(self.words[1])
        if self.words[2][0:2] == '0x':
            immediate = integer_to_bin_signed(str(int(self.words[2][2:], 16)), 20)
        else:
            immediate = integer_to_bin_signed(self.words[2], 20)
        if self.words[0] == 'auipc':
            opcode = '0010111'
            bin = immediate[:] + rs1 + opcode
            return bin
        elif self.words[0] == 'lui':
            opcode = '0110111'
            bin = immediate[:] + rs1 + opcode
            return bin

    @property
    def ujformat(self):
        rs1 = integer_to_bin_5_unsigned(self.words[1])
        temp=0
        for char in self.words[2]:
            if char.isalpha():
                temp=temp+1
        if temp>0:
            relative_pc = self.label_dict[self.words[2]][1] - self.program_counter
            # print(relative_pc)
            immediate = (integer_to_bin_signed(relative_pc, 21))
            # print(immediate)
        else:
            if (int(self.words[2])%2)==1:
                self.words[2]=str(int(self.words[2])-1)
            # print(self.words[2])
            immediate=integer_to_bin_signed(self.words[2],21)
            # print(immediate)
        opcode = '1101111'
        bin = immediate[0] + immediate[10:20] + immediate[9] + immediate[1:9] + rs1 + opcode
        return bin


def integer_to_bin_5_unsigned(n):
    n = n[1:]         # As n-x4, taking count only 4
    n = int(n)
    bin = ''
    for i in range(0, 5):
        bin = str(int(n % 2)) + bin
        n = n / 2
    return bin


def integer_to_bin_signed(n, bits):
    n = int(n)
    bin = ''
    if n < 0:
        n = (2 ** bits) + n
    for iterator in range(0, bits):
        bin = str(int(n % 2)) + bin
        n = n / 2
    return bin
