from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Assembler:
    @classmethod
    def create(cls) -> Assembler:
        return cls()

    def assemble(self, assembly: Iterable[str]) -> Iterable[str]:
        machine_code = []
        symbol_table = {}

        predefined_symbols = {
            'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
            'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5,
            'R6': 6, 'R7': 7, 'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11,
            'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15,
            'SCREEN': 16384, 'KBD': 24576
        }    
        symbol_table.update(predefined_symbols)

        #pass1
        addr = 0
        for line in assembly:
            #Remove Whitespaces
            line = line.strip()
            #Skip empty Lines and comments
            if not line or line.startswith('//'):
                continue
            if(line.startswith('(') and line.endswith(')')):
                label = line[1:-1]
                symbol_table[label] = addr
            else:
                #Address of the current line (for remembering labels)
                addr += 1

        #pass2
        addr = 16
        for line in assembly:
            line = line.strip()
            #Skip empty lines, comments, and labels
            if not line or line.startswith('//') or line.startswith('('):
                continue
            #Remove Inline comment
            instr = line.split('//', 1)[0].strip()
            if(instr.startswith('@')): #Instr A
                num = instr[1:]
                if(num.isdigit()): #If number
                    address = int(num)
                elif num in symbol_table: #If symbol but already in table
                    address = symbol_table[num]
                else: #If new symbol
                    address = addr
                    symbol_table[num] = address
                    addr+=1
                machine_code.append(format(address, "016b"))
            else: #C instr
                dest, comp, jump = '', '', ''
                if '=' in instr:
                    dest, comp = instr.split('=')
                if ';' in instr:
                    comp, jump = instr.split(';') 

                dest_binary = self.dest_table(dest)
                comp_binary = self.comp_table(comp)
                jump_binary = self.jump_table(jump)

                machine_code.append(f'111{comp_binary}{dest_binary}{jump_binary}')
        for line in machine_code:
            print(line)  
        return machine_code  # TODO: your work for Project 6 starts here
        
    def dest_table(self, dest: str) -> str:
        dest_map = {
            '': '000',
            'M': '001',
            'D': '010',
            'MD': '011',
            'A': '100',
            'AM': '101',
            'AD': '110',
            'AMD': '111'
        }
        return dest_map.get(dest, '000')

    def comp_table(self, comp: str) -> str:
        comp_map = {
            '0': '0101010',
            '1': '0111111',
            '-1': '0111010',
            'D': '0001100',
            'A': '0110000',
            '!D': '0001101',
            '!A': '0110001',
            '-D': '0001111',
            '-A': '0110011',
            'D+1': '0011111',
            'A+1': '0110111',
            'D-1': '0001110',
            'A-1': '0110010',
            'D+A': '0000010',
            'D-A': '0010011',
            'A-D': '0000111',
            'D&A': '0000000',
            'D|A': '0010101',
            'M': '1110000',
            '!M': '1110001',
            '-M': '1110011',
            'M+1': '1110111',
            'M-1': '1110010',
            'D+M': '1000010',
            'D-M': '1010011',
            'M-D': '1000111',
            'D&M': '1000000',
            'D|M': '1010101'
        }
        return comp_map[comp]

    def jump_table(self, jump: str) -> str:
        jump_map = {
            '': '000',
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'
        }
        return jump_map.get(jump, '000')
