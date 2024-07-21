from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VmProgram:  # TODO: your work for Projects 7 and 8 starts here
    code_lines: list[str]  # Stores the lines of code
    
    @classmethod
    def load_from(cls, file_or_directory_name: str) -> 'VmProgram':
        with open(file_or_directory_name, 'r') as file:
            code_lines = file.readlines()  # Read lines of code from the file
        return cls(code_lines)
    
    def write_to_file(self, file_name: str, asm_code : str) -> None:
        asm_code = self.translate()
        with open(file_name, 'w') as file:
            for line in asm_code:
                file.write(line + '\n')

    def translate(self) -> None: 
        lineNum = 0 #For the labels to be unique, because the translated code doesnt work sxvanairad
     
        asm_code = []
        listOfSegs = ['local', 'argument', 'this', 'that',
                        'constant', 'static', 'temp', 'pointer']
        mapOfSegs = {'local' : 'LCL', 'argument' : 'ARG', 'this' : 'THIS', 'that' : 'THAT'}

        for line in self.code_lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue   
            if 'push' in line or 'pop' in line:   #Memory Access
                parts = line.split()
                if(parts[0] == 'push'): #PushOp
                    if(parts[1] in listOfSegs[:4]): #LCL,ARG,THIS,THAT
                        str1 = '@' + parts[2]
                        str2 = '@' + mapOfSegs[parts[1]]
                        asm_code += [str1, 'D = A', str2, 'A = M + D', 'D = M', '@SP', 'A = M', 'M = D', '@SP', 'M = M + 1']
                    if(parts[1] == 'constant'):
                        str1 = '@' + parts[2]
                        asm_code += [str1, 'D = A', '@SP', 'A = M', 'M = D', '@SP', 'M = M+1']
                    if(parts[1] == 'static'):
                        str1 = '@foo.' + parts[2]
                        asm_code += [str1, 'D = M', '@SP', 'A = M', 'M = D', '@SP', 'M = M + 1']
                    if(parts[1] == 'temp'):
                        str1 = '@' + parts[2]
                        str2 = '@5'
                        asm_code += [str1, 'D = A', str2, 'A = A + D', 'D = M', '@SP', 'A = M', 'M = D', '@SP', 'M = M + 1']
                    if(parts[1] == 'pointer'):
                        map = {'0' : 'THIS', '1' : 'THAT'}
                        str1 = '@' + map[parts[2]]
                        asm_code += [str1, 'D = M', '@SP', 'A = M', 'M = D', '@SP', 'M = M + 1']
                else: #PopOp
                    if(parts[1] in listOfSegs[:4]): #LCL,ARG,THIS,THAT
                        str1 = '@' + parts[2]
                        str2 = '@' + mapOfSegs[parts[1]]
                        asm_code += [str1, 'D = A', str2, 'D = M + D', '@R13', 'M = D', '@SP', 'M = M - 1', 'A = M', 'D = M', '@R13', 'A = M', 'M = D']
                    if(parts[1] == 'static'):
                        str1 = '@foo.' + parts[2]
                        asm_code += ['@SP', 'M = M - 1', 'A = M', 'D = M', str1, 'M = D']
                    if(parts[1] == 'temp'):
                        str1 = '@' + parts[2]
                        str2 = '@5'
                        asm_code += [str1, 'D = A', str2, 'D = A + D', '@R13', 'M = D', '@SP', 'M = M - 1', 'A = M', 'D = M', '@R13', 'A = M', 'M = D']    
                    if(parts[1] == 'pointer'):
                        map = {'0' : 'THIS', '1' : 'THAT'}
                        str1 = '@' + map[parts[2]]
                        asm_code += ['@SP', 'M = M - 1', 'A = M', 'D = M', str1, 'M = D']
            else: #Arithmetic/Logic
                asm_code += (self.arithm_map(lineNum))[line]
                if(line == 'eq' or line == 'lt' or line == 'gt'):
                    lineNum += 1
        
        asm_code += ['(END)', '@END', '0,JMP'] #For the End Loop
        return asm_code
  
    @staticmethod
    def arithm_map(lineNum):
        return {'add' : ['@SP', 'M = M - 1', 'A = M', 'D = M', '@R13', 'M = D', 
                            '@SP', 'M = M - 1', 'A = M', 'D = M',
                            '@R13', 'D = D + M',
                            '@SP', 'A = M', 'M = D',
                            '@SP', 'M = M + 1'],
                  'sub' : ['@SP', 'M = M - 1', 'A = M', 'D = M', '@R13', 'M = D', 
                            '@SP', 'M = M - 1', 'A = M', 'D = M',
                            '@R13', 'D = D - M',
                            '@SP', 'A = M', 'M = D',
                            '@SP', 'M = M + 1'],
                  'neg' : ['@SP', 'M = M - 1', 'A = M', 'D = M',
                           '@0', 'D = A - D',
                           '@SP', 'A = M', 'M = D',
                           '@SP', 'M = M + 1'],        
                  'eq'  : ['@SP', 'M = M - 1', 'A = M', 'D = M',
                           '@SP', 'M = M - 1', 'A = M', 'D = M - D',
                           '@EQUAL' + str(lineNum), 'D;JEQ', '@NOTEQ' + str(lineNum), '0;JMP',
                           '(EQUAL' + str(lineNum) + ')', '@SP', 'A = M', 'M = -1', '@ENDOP' + str(lineNum), '0;JMP',
                           '(NOTEQ' + str(lineNum) + ')', '@SP', 'A = M', 'M = 0', '(ENDOP' + str(lineNum) + ')',
                           '@SP', 'M = M + 1'],
                  'gt'  : ['@SP', 'M = M - 1', 'A = M', 'D = M',
                           '@SP', 'M = M - 1', 'A = M', 'D = M - D',
                           '@GT' + str(lineNum), 'D;JGT', '@NOTGT' + str(lineNum), '0;JMP',
                           '(GT' + str(lineNum) + ')', '@SP', 'A = M', 'M = -1', '@ENDOP' + str(lineNum), '0;JMP',
                           '(NOTGT' + str(lineNum) + ')', '@SP', 'A = M', 'M = 0', '(ENDOP' + str(lineNum) + ')',
                           '@SP', 'M = M + 1'],
                  'lt'  : ['@SP', 'M = M - 1', 'A = M', 'D = M',
                           '@SP', 'M = M - 1', 'A = M', 'D = M - D',
                           '@LT' + str(lineNum), 'D;JLT', '@NOTLT' + str(lineNum), '0;JMP',
                           '(LT' + str(lineNum) + ')', '@SP', 'A = M', 'M = -1', '@ENDOP' + str(lineNum), '0;JMP',
                           '(NOTLT' + str(lineNum) + ')', '@SP', 'A = M', 'M = 0', '(ENDOP' + str(lineNum) + ')',
                           '@SP', 'M = M + 1'],
                  'and' :  ['@SP', 'M = M - 1', 'A = M', 'D = M',
                            '@SP', 'M = M - 1', 'A = M', 'M = M & D',
                            '@SP', 'M = M + 1'],
                  'or'  : ['@SP', 'M = M - 1', 'A = M', 'D = M',
                            '@SP', 'M = M - 1', 'A = M', 'M = M | D',
                            '@SP', 'M = M + 1'],
                  'not' : ['@SP', 'A = M', 'M = !M',
                           '@SP', 'M = M + 1']}
    
if __name__ == '__main__':
    program = VmProgram.load_from('StackTest.vm')
    asm_code = program.translate()
    print(asm_code)
    program.write_to_file('StackTest.asm', asm_code)  
