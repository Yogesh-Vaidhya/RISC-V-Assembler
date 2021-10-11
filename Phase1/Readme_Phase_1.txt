Readme File For Phase 1
1. Download the .zip file and extract it.
2. Goto the location where folder is extracted in Terminal or in Command Prompt.
3. Folder should contain all the given files
   Namely read.asm, Read.py, Error.py, Machine_code_generator.py, upload.mc, memory.txt.
4. read.asm file contains fibonacci RISC V assembly code and can be editied to have different assembly code,to generate different machine codes.
ASSUMPTIONS:-
	1.Pseudo Instructions not handled.
	2.Floating point operations not supported.
	3.Input Format for Phase 1:
	   1. Input should be given in the “read.asm” file.
           2. After label not instruction should be present in that line.
	      i.e. Instruction
	           Label:               // separately in one line
		   Instruction
              e.g. addi x1,x2,4
                   fact:              // fact label separately in one line 
                   beq x0,x0,fact
	   3.Load, Store and Jalr are supported with brackets.
		i.e  
                     lw x1,0(x2)
	     	     sw x1,0(x2)
	             jalr x1,0(x2)

5. After editing the .asm file if needed
6. In terminal run python file Read.py which will generate upload.mc-(Machine code file + Memory Data segment) and memory.txt
   To Run file using command prompt - goto the location where folder is extracted and type - python Read.py
     This will generate the .mc file having name upload.mc

     I have Run this code using Pycharm IDE(basically for python language)
     
7. All the error in the .asm file if any is printed in the terminal.
   If error is present no machine code or any memory is generated.