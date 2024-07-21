from __future__ import annotations

from typing import List

class HackComputer:
    pc: int = 0
    aReg: int = 0
    dReg: int = 0
    RAM: List[int] = []
    RAM_touched: List[bool] = []

    end_check: int = 0

    def __init__(self):
        self.RAM = [0] * 24576
        self.RAM[0] = 256 #init SP Pointer
        self.RAM[1] = 300 #init LCL Pointer
        self.RAM[2] = 400 #init ARG Pointer
        self.RAM[3] = 3000 #init THIS Pointer
        self.RAM[4] = 3010 #init THAT Pointer

        self.RAM_touched = [False] * 24576

    @classmethod
    def create(cls) -> HackComputer:
        return cls()

    def execute_instruction_set(self, instruction_set: List[str], cycles: int) -> List[str]:
        ret: List[str] = []

        num_cycle: int = 0
        while(self.pc < len(instruction_set) and num_cycle < cycles):
            self._execute_instruction(instruction_set[self.pc])
            
            if(self.pc == len(instruction_set) - 1):
                self.end_check = self.end_check + 1

            if(self.end_check == 3): 
                break

            num_cycle = num_cycle + 1


        for i in range(0,16384):
            if(self.RAM_touched[i]):
                ret.append(f"{i}:{self.RAM[i]}")
        return ret
    
    def _execute_instruction(self, instruction: str) -> None:
        op_code: str = instruction[0]

        if(op_code == "0"): #A Instruction
            address: int = int(instruction[-15:], 2)
            self.aReg = address
            self.pc = self.pc + 1
        else: #C Instruction  
            j: str = instruction[-3:]
            d: str = instruction[-6:-3]
            c: str = instruction[4:10]
            a: str = instruction[3]

            comp: int = self._compute(a, c)
            if(d != "000"):
                if(d[0] == "1"):
                    self.aReg = comp
                if(d[1] == "1"):
                    self.dReg = comp
                if(d[2] == "1"):
                    self.RAM[self.aReg] = comp
                    self.RAM_touched[self.aReg] = True
            if(j != "000"):
                self._jump(comp, j)
            else:
                self.pc = self.pc + 1

        return
    
    def _compute(self, a: str, c: str) -> int:
        comp: int = 0
        if(a == "0"):
            if(c == "101010"): #0
                comp = 0
            elif(c == "111111"): #1
                comp = 1
            elif(c == "111010"): #-1
                comp = -1
            elif(c == "001100"): #D
                comp = self.dReg
            elif(c == "110000"): #A
                comp = self.aReg
            elif(c == "001101"): #!D
                comp = ~self.dReg
            elif(c == "110001"): #!A
                comp = ~self.aReg
            elif(c == "001111"): #-D
                comp = -self.dReg
            elif(c == "110011"): #-A
                comp = -self.aReg
            elif(c == "011111"): #D+1
                comp = self.dReg + 1
            elif(c == "110111"): #A+1
                comp = self.aReg + 1
            elif(c == "001110"): #D-1
                comp = self.dReg - 1
            elif(c == "110010"): #A-1
                comp = self.aReg -1
            elif(c == "000010"): #D+A
                comp = self.dReg + self.aReg
            elif(c == "010011"): #D-A
                comp = self.dReg - self.aReg
            elif(c == "000111"): #A-D
                comp = self.aReg - self.dReg
            elif(c == "000000"): #A&D
                comp = self.aReg & self.dReg
            elif(c == "010101"): #A|D
                comp = self.aReg | self.dReg
            else:
                pass
        else:
            if(c == "110000"): #M
                comp = self.RAM[self.aReg]
            elif(c == "110001"): #!M
                comp = ~self.RAM[self.aReg]
            elif(c == "110011"): #-M
                comp = -self.RAM[self.aReg]
            elif(c == "110111"): #M+1
                comp = self.RAM[self.aReg] + 1
            elif(c == "110010"): #M-1
                comp = self.RAM[self.aReg] - 1
            elif(c == "000010"): #D+M
                comp = self.dReg + self.RAM[self.aReg]
            elif(c == "010011"): #D-M
                comp = self.dReg - self.RAM[self.aReg]
            elif(c == "000111"): #M-D
                comp = self.RAM[self.aReg] - self.dReg
            elif(c == "000000"): #D&M
                comp = self.dReg & self.RAM[self.aReg]
            elif(c == "010101"): #D|M
                comp = self.dReg | self.RAM[self.aReg]
            else: 
                pass
        return comp
    
    def _jump(self, comp: int, j: str) -> None:
        if(j == "001"): #JGT
            if(comp > 0):
                self.pc = self.aReg
            else:
                self.pc = self.pc + 1
        elif(j == "010"): #JEQ
            if(comp == 0):
                self.pc = self.aReg
            else:
                self.pc = self.pc + 1
        elif(j == "011"): #JGE
            if(comp >= 0):
                self.pc = self.aReg
            else:
                self.pc = self.pc + 1
        elif(j == "100"): #JLT
            if(comp < 0):
                self.pc = self.aReg
            else:
                self.pc = self.pc + 1
        elif(j == "101"): #JNE
            if(comp != 0):
                self.pc = self.aReg
            else:
                self.pc = self.pc + 1
        elif(j == "110"): #JLE
            if(comp <= 0):
                self.pc = self.aReg
            else:
                self.pc = self.pc + 1
        else: #JMP
            self.pc = self.aReg