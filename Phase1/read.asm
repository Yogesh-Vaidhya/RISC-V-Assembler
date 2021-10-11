#Fibonacci
.data
num: .word 5
.text
auipc x10,65536
lw x10,0(x10)
addi x15,x0,2
addi x16,x0,1
jal x1,fib
beq x0,x0,exit
fib:
addi x2,x2,-8
sw x10,4(x2)
sw x1,0(x2)
bge x10,x15,L1
beq x10,x16,L2
lw x1,0(x2)
lw x10,4(x2)
addi x2,x2,8
add x12,x12,x0
jalr x0,0(x1)
L2:
lw x1,0(x2)
lw x10,4(x2)
addi x2,x2,8
add x12,x16,x0
jalr x0,0(x1)
L1:
addi x10,x10,-1
jal x1,fib
add x6,x0,x12
lw x10,4(x2)
addi x10,x10,-2
jal x1,fib
add x12,x6,x12
lw x1,0(x2)
lw x10,4(x2)
addi x2,x2,8
jalr x0,0(x1)
exit: