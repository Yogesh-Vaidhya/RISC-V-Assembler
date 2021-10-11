def Error_finder(words,line_counter,length,labels):
    if (words[0] == 'add' or words[0] == 'and' or words[0] == 'or' or words[0] == 'sll' or words[0] == 'slt' or
         words[0] == 'sra' or words[0] == 'srl' or words[0] == 'sub' or words[0] == 'xor' or words[0] == 'mul' or
          words[0] == 'div' or words[0] == 'rem' or words[0] == 'addi' or words[0] == 'andi' or words[0] == 'ori' or
           words[0] == 'lb' or words[0] == 'ld' or words[0] == 'lh' or words[0] == 'lw' or words[0] == 'jalr' or
            words[0] == 'sb' or words[0] == 'sw' or words[0] == 'sd' or words[0] == 'sh' or words[0] == 'beq' or
             words[0] == 'bne' or words[0] == 'bge' or words[0] == 'blt' or words[0] == 'auipc'
              or words[0] == 'lui' or words[0] == 'jal'):
        if(words[0] == 'add' or words[0] == 'and' or words[0] == 'or' or words[0] == 'sll' or words[0] == 'slt' or
            words[0] == 'sra' or words[0] == 'srl' or words[0] == 'sub' or words[0] == 'xor' or words[0] == 'mul' or
             words[0] == 'div' or words[0] == 'rem'):
            if length==4 and words[1][0] == 'x' and words[1][1:].isdecimal() and words[2][0] == 'x' \
                    and words[2][1:].isdecimal() and words[3][0] == 'x' \
                        and words[3][1:].isdecimal():
                if 0 <= int(words[1][1:]) <= 31:
                    if 0 <= int(words[2][1:]) <= 31:
                        if 0 <= int(words[3][1:]) <= 31:
                            return 1
                        else:
                            print('ERROR in .asm file in line', line_counter, '\nRegister', words[3],
                                  'is not recognized, Please Correct')
                            return -1
                    else:
                        print('ERROR in .asm file in line', line_counter, '\nRegister', words[2],
                              'is not recognized, Please Correct')
                        return -1
                else:
                    print('ERROR in .asm file in line', line_counter, '\nRegister', words[1],
                          'is not recognized, Please Correct')
                    return -1
            else:
                print('ERROR in .asm file in line', line_counter, '\n', words[0],
                      'Instruction has Syntax Error,Please Correct')
                return -1
        elif words[0] == 'addi' or words[0] == 'andi' or words[0] == 'ori':
            if length==4 and words[1][0] == 'x' and words[1][1:].isdecimal() and words[2][0] == 'x' and \
                    words[2][1:].isdecimal() and (words[3][0:2]=='0x'or string_int(words[3])==1):
                if 0 <= int(words[1][1:]) <= 31:
                    if 0 <= int(words[2][1:]) <= 31:
                        if (words[3][0:2] =='0x' and string_hex(words[3][2:])==1 and len(words[3])>=3) \
                                or string_int(words[3])==1:
                            if words[3][0:2] == '0x':
                                immediate = int(words[3][2:],16)
                            else:
                                immediate = int(words[3])
                            if -2048 <= immediate <= 2047:
                                return 1
                            else:
                                print('ERROR in .asm file in line', line_counter,'\nImmediate ',words[3],'is out of '
                                                                                                         'range(should '
                                                                                            'be between -2048 and '
                                                                                            '2047), Please Correct')
                                return -1
                        else:
                            print('ERROR in .asm file in line', line_counter, '\nRegister', words[3],
                                  'is not recognized, Please Correct')
                            return -1
                    else:
                        print('ERROR in .asm file in line', line_counter, '\nRegister', words[2],
                              'is not recognized, Please Correct')
                        return -1
                else:
                    print('ERROR in .asm file in line', line_counter, '\nRegister', words[1],
                          'is not recognized, Please Correct')
                    return -1
            else:
                print('ERROR in .asm file in line', line_counter, '\n', words[0],
                      'Instruction has Syntax Error,Please Correct')
                return -1
        elif words[0] == 'lb' or words[0] == 'ld' or words[0] == 'lh' or words[0] == 'lw' or words[0] == 'sb' \
                or words[0] == 'sw' or words[0] == 'sd' or words[0] == 'sh' or words[0]=='jalr':
            if length==3 and words[1][0]=='x' and words[1][1:].isdecimal() and words[2][-1]==')':
                if 0 <= int(words[1][1:]) <= 31:
                    words[2] = words[2].replace('(', ' ')
                    words[2] = words[2].replace(')', '')
                    sub = words[2].split()
                    if len(sub)==2 and sub[1][0] == 'x' and sub[1][1:].isdecimal() \
                        and ((sub[0][0:2] == '0x'and string_hex(sub[0][2:])==1 and len(sub[0])>=3) or string_int(sub[0])==1):
                        if sub[0][0:2] == '0x':
                            immediate = int(sub[0][2:],16)
                        else:
                            immediate = int(sub[0])
                        if -2048 <= immediate <= 2047:
                            return 1
                        else:
                            print('ERROR in .asm file in line', line_counter, '\nImmediate ', sub[0], 'is out of range(should '
                                                                                           'be between -2048 and '
                                                                                           '2047), Please Correct')
                            return -1
                    else:
                        print('ERROR in .asm file in line', line_counter, '\n', words[0],
                              'Instruction has Syntax Error\nFormat should be like',words[0],'x1,0(x2)Please Correct')
                        return -1
                else:
                    print('ERROR in .asm file in line', line_counter, '\nRegister', words[1],
                          'is not recognized, Please Correct')
                    return -1
            else:
                print('ERROR in .asm file in line', line_counter, '\n', words[0],
                      'Instruction has Syntax Error,Please Correct')
                return -1
        elif words[0] == 'auipc' or words[0] == 'lui':
            if length==3 and words[1][0]=='x' and words[1][1:].isdecimal() and (words[2][0:2]=='0x' or string_int(words[2])==1):
                if 0 <= int(words[1][1:]) <= 31:
                    if (words[2][0:2] == '0x' and string_hex(words[2][2:]) == 1 and len(words[2]) >= 3) or string_int(words[2])==1:
                        if words[2][0:2] == '0x':
                            immediate = int(words[2][2:], 16)
                        else:
                            immediate = int(words[2])
                        if 0<= immediate <= 1048575:
                            return 1
                        else:
                            print('ERROR in .asm file in line', line_counter, '\nImmediate ', words[2], 'is out of range(should '
                                                                                           'be between 0 and '
                                                                                           '1048575), Please Correct')
                            return -1
                    else:
                        print('ERROR in .asm file in line', line_counter, '\n', words[2],
                              'is not recognized, Please Correct')
                        return -1

                else:
                    print('ERROR in .asm file in line', line_counter, '\nRegister', words[1],
                          'is not recognized, Please Correct')
                    return -1
            else:
                print('ERROR in .asm file in line', line_counter, '\n', words[0],
                      'Instruction has Syntax Error,Please Correct')
                return -1
        elif words[0] == 'beq' or words[0] == 'bne' or words[0] == 'bge' or words[0] == 'blt':
            if length == 4 and words[1][0] == 'x' and words[1][1:].isdecimal() and words[2][0] == 'x' and words[2][1:].isdecimal():
                if 0 <= int(words[1][1:]) <= 31:
                    if 0 <= int(words[2][1:]) <= 31:
                        point=0
                        if string_int(words[3])==1:
                            immediate = int(words[3])
                            if -2048 <= immediate <= 2047:
                                return 1
                            else:
                                print('ERROR in .asm file in line', line_counter, '\noffset ', words[3], 'is out of range(should '
                                                                                            'be between -2048 and '
                                                                                            '2047), Please Correct')
                                return -1
                        for key in labels:
                            if words[3] == key:
                                point = 1
                                break
                        if point==1:
                            return 1
                        else:
                            print('ERROR in .asm file in line', line_counter, '\n Label is not recognized, Please '
                                                                              'Correct')
                            return -1
                    else:
                        print('ERROR in .asm file in line', line_counter, '\nRegister', words[2],
                              'is not recognized, Please Correct')
                        return -1
                else:
                    print('ERROR in .asm file in line', line_counter, '\nRegister', words[1],
                          'is not recognized, Please Correct')
                    return -1

            else:
                print('ERROR in .asm file in line', line_counter, '\n', words[0],
                      'Instruction has Syntax Error,Please Correct')
                return -1

        elif words[0] == 'jal':
            if length == 3 and words[1][0] == 'x' and words[1][1:].isdecimal():
                if 0 <= int(words[1][1:]) <= 31:
                    point=0
                    if string_int(words[2])==1:
                        immediate = int(words[2])
                        if -2048 <= immediate <= 2047:
                            return 1
                        else:
                            print('ERROR in .asm file in line', line_counter, '\noffset ', words[2], 'is out of range(should '
                                                                                        'be between -2048 and '
                                                                                        '2047), Please Correct')
                            return -1
                    for key in labels:
                        if words[2] == key:
                            point = 1
                            break
                    if point==1:
                        return 1
                    else:
                        print('ERROR in .asm file in line', line_counter, '\n Label is not recognized, Please Correct')
                        return -1
                else:
                    print('ERROR in .asm file in line', line_counter, '\n', words[1],
                          'is not recognized, Please Correct')
                    return -1
            else:
                print('ERROR in .asm file in line', line_counter, '\n', words[0],
                      'Instruction has Syntax Error,Please Correct')
                return -1
    else:
        print('ERROR in .asm file in line',line_counter,'\n',words[0], 'Instruction not supported in this compiler, Please change '
                                                          'the instruction')
        return -1


def string_hex(word):
    temp=1
    for i in word:
        if(i=='0' or i=='1' or i=='2'or i=='3'or i=='4'or i=='5'or i=='6'or i=='7'or i=='8'or i=='9'or i=='10'or i=='a'or i=='b'
              or i=='c'or i=='d'or i=='e'or i=='f'or i=='A'or i=='B' or i=='C'or i=='D'or i=='E'or i=='F'):
            continue
        else:
            temp=0
            break
    return temp


def string_int(word):
    temp=1
    for i in word:
        if i== '0' or i== '1' or i== '2'or i== '3'or i== '4'or i== '5'or i== '6'or i== '7'or i== '8'or i== '9' or i== '-':
            continue
        else:
            temp=0
            break
    return temp
