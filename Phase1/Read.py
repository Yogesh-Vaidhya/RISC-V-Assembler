from Machine_code_generator import *
from Error import *

f = open("read.asm", "r")
g = open("upload.mc", "w")
h = open("memory.txt","w")

# Reading lines
line_array = f.readlines()

# parse the complete code once to save label in label
# Initialisation
label_dict = {}
line_counter = 0
program_counter = 0
mc_list = []
labels=[]

temp=0       #To find in data segment or in text segment
for line in line_array:
    line = line.replace(',', ' ')  # replace ',' with ' ' for easy split
    words = line.split()  # index al words in a line
    if words:  # if line is not empty
        # print(words)
        line_counter += 1          # Neglecting the empty lines
        if words[0] == '.data':
            temp=1
            continue
        elif words[0] == '.text':
            temp=0
            continue
        elif words[0][0] == '#':
            continue
        elif words[0][-1] == ':' and temp==1:
            continue
        elif words[0][-1] == ':' and temp==0:
            label_dict[words[0].replace(':', '')] = [line_counter, program_counter]
            labels.append(words[0].replace(':', ''))
            continue
        program_counter += 4            # PC incremented to next instruction

# parse the complete code again to find the error in the instruction
line_counter = 0
program_counter = 0
temp=0
t=1
count1=0
for line in line_array:                   # Reading line by line
    line = line.replace(',', ' ')         # replace ',' with ' ' for easy split
    words = line.split()                  # index al words in a line
    line_counter = line_counter + 1
    if words:                             # if line is not empty
        if words[0] == '.data':
            temp=1
            continue
        elif words[0] == '.text':
            temp=0
            continue
        elif words[0][-1] == ':':
            continue
        elif words[0][0] == '#':
            continue
        else:
            if temp == 0:
                length=len(words)
                t=Error_finder(words,line_counter,length,labels)
            if t == -1:
                count1=count1+1
            program_counter += 4

if count1==0:
    # print('No Error in the code')
    # parse the complete code again to read the instructions
    line_counter = 0
    program_counter = 0
    temp=0
    for line in line_array:                   # Reading line by line
        line = line.replace(',', ' ')         # replace ',' with ' ' for easy split
        words = line.split()                  # index al words in a line
        if words:                             # if line is not empty
            # print(words)
            line_counter += 1
            if words[0] == '.data':
                temp=1
                continue
            elif words[0] == '.text':
                temp=0
                continue
            elif words[0][-1] == ':':
                continue
            elif words[0][0] == '#':
                continue
            else:
                if temp==0:
                    # pc = str(hex(program_counter))
                    # print(pc, end=" ")
                    mc = Machine_code(words,program_counter,label_dict)                  # Creating Class object
                    mc_list.append([program_counter, mc.generate()])       # Generating machine code
                    program_counter += 4                      # PC incremented to next instruction

    # g.write('PC Machine Code\n')
    temp='0x0'         # Used to show termination of program
    for i in mc_list:
        g.write(str(hex(i[0]))+' '+i[1][0:2]+i[1][2:].upper()+'\n')
        if i==mc_list[-1]:
            temp=str(hex(i[0]+4))
    g.write(temp+' '+'0x'+'ef000011'.upper()+'\n')     # Loading data in upload.mc file
    # printing the labels
    # print(label_dict)
    # Memory .data segment
    # Initialisation
    fin = ''
    hexa = []
    length = []
    mem = {}
    ty = []
    mem_list = []
    temp=0
    for line in line_array:
        b = line.rstrip('\n')
        if b == ".data":
            temp=1
            continue
        elif b == ".text":
            temp=0
            break
        elif temp==1:
            list = b.split(" ")
            c = list[0].replace(":", '')
            d = list[1].replace(".", '')
            if d == "word":                                     # if .word 23 24 45 56 67 or .word 23
                e = 4
                for i in range(0,len(list)-2):                 # i in(0,5) or i in (0,1):for array or simple var
                    ty.append('w')                              # creating type list of data
                    st = hex(int(list[i + 2]))                  # hex format of the data is string
                    st = st.replace('0x','')
                    st=st.upper()
                    hexa.append(st)
                    length.append(e)                           # getting length of hex data in bytes
            elif d == "byte":
                e = 1
                for i in range(0, len(list) - 2):
                    ty.append('b')
                    st = hex(int(list[i + 2]))
                    st = st.replace("0x", '')
                    st=st.upper()
                    hexa.append(st)
                    length.append(e)
            elif d == "half":
                e = 2
                for i in range(0, len(list) - 2):
                    ty.append('h')
                    st = hex(int(list[i + 2]))
                    st = st.replace("0x", '')
                    st=st.upper()
                    hexa.append(st)
                    length.append(e)
            else:
                var = ''
                for word in list[2:]:
                    if word != list[-1]:
                        var = var+word+' '
                    else:
                        var = var+word
                s = len(var)
                var = var[1:s-1]              # .asciiz "hello"   removing 1st and last "
                ty.append('a')
                st = ''
                for ch in var:
                    st = st + hex(ord(ch)).replace("0x", '')   # ord is use to get ascii value-->hexa(string)-->replace 0x
                st = st + '00'                                 # for null character at end
                st = st.upper()
                e = len(st)
                hexa.append(st)
                length.append(e)

    e = 268435456                                              # by default:initial address
    address = []
    total = sum(length)                                       # generating sum
    for i in range(0, total, 4):                             # generating address to be filled in .data
        if i == 0:
            address.append("0x10000000")
        else:
            e = e + 4
            s = str(hex(e)).upper()
            address.append('0x'+s[2:])
    s = ""
    s1 = ""
    for i in range(len(length)):
        if ty[i] == 'w' or ty[i] == 'b' or ty[i] == 'h':
            s = ""
            for j in range(8 - len(hexa[i])):
                s = s + '0'                     # generating complete 8digit lengthof data:eg::20-->14(hex)-->00000014
            hexa[i] = s + hexa[i]
            it = 0
            jt = 2
            s = ""
            s1 = ""
            for k in range(0, 4):
                s = hexa[i][it:jt]
                s1 = s + s1
                it = it + 2
                jt = jt + 2
            hexa[i] = s1                        # reversing the hex format for little endian :00001234-->34120000
            if ty[i] == 'w':
                fin = fin + hexa[i]
            elif ty[i] == 'b':                  # generating final  data string to be filled in memory address
                fin = fin + hexa[i][0:2]
            else:
                fin = fin + hexa[i][0:4]
        else:
            fin = fin + hexa[i]
    j = 0
    for i in range(0, len(fin), 8):
        if i + 8 > len(fin):
            s = fin[i:]                         # if in last is less than 8 digit, then error so use if else
            mem_list.append(s)
        else:
            s = fin[i:i + 8]
            mem_list.append(s)
        mem.update({address[j]: mem_list[j]})
        j = j + 1

    l = ''
    count=0
    for key in mem:
        count=count+1
        l = l+(key+':'+mem[key]+'\n')
    h.write(l)

    e = 268435456
    for key in mem:
        j=0
        for i in range(0,4):
            s = str(hex(e)).upper()
            if mem[key][j:j + 2]!= '':
                g.write('0x'+s[2:]+' '+'0x'+ mem[key][j:j+2]+'\n')
            j=j+2
            e=e+1
    if count==0:
        g.write('0x10000000'+' '+'0x00\n')

# closing file
h.close()
f.close()
g.close()

