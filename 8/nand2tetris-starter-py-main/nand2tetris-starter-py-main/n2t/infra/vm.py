from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VmProgram:  # TODO: your work for Projects 7 and 8 starts here
    code_lines: list[str] #Self explanatory -> stores the lines from the code

    @classmethod
    def load_from(cls, file_or_directory_name: str) -> 'VmProgram':
        with open(file_or_directory_name, 'r') as file:
            code_lines = file.readlines()  # Read lines of code from the file
        return cls(code_lines)
    
    def write_to_file(self, file_name: str, asm_code : list[str]) -> None:
        with open(file_name, 'w') as file:
            for line in asm_code:
                file.write(line + '\n')

    def translate(self) -> list[str]: 
        lineNum:int = 0 #For the labels to be unique when translating
                        #into assembly
        asm_code: list[str] = []

        for line in self.code_lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue   
            if 'push' in line or 'pop' in line:   #Memory Access
                parts:list[str] = line.split()
                if(parts[0] == 'push'): #PushOp
                    asm_code += self.translate_push(line)
                else: #PopOp
                    asm_code += self.translate_pop(line)
            elif 'label' in line: #Label
                asm_code += self.translate_label(line)
            elif 'if-goto' in line: #Conditional branch
                asm_code += self.translate_conditional_branch(line)
            elif 'goto' in line: #Unconditional branch
                asm_code += self.translate_unconditional_branch(line)
            elif 'function' in line: #function definition
                asm_code += self.translate_function(line)
            elif 'return' in line: #function return
                asm_code += self.translate_return(line)
            elif 'call' in line: #function call
                asm_code += self.translate_call(line, lineNum)
                lineNum += 1
            else: #Arithmetic/Logic
                asm_code += (self.arithm_map(lineNum))[line.split()[0]]
                if(line == 'eq' or line == 'lt' or line == 'gt'):
                    lineNum += 1
        
        asm_code += ['(END)', '@END', '0,JMP'] #For the End Loop
        return asm_code
  
    @staticmethod
    def translate_push(line:str) -> list[str]:
        listOfSegs : list[str] = ['local', 'argument', 'this', 'that',
                        'constant', 'static', 'temp', 'pointer']
        mapOfSegs : dict[str, str] = {'local' : 'LCL', 'argument' : 'ARG',
                                       'this' : 'THIS', 'that' : 'THAT'}

        parts:list[str] = line.split()
        str1:str
        str2:str
        map:dict[str, str] = {'0' : 'THIS', '1' : 'THAT'}
        asm_code:list[str] = []

        if(parts[1] in listOfSegs[:4]): #LCL,ARG,THIS,THAT
            str1 = '@' + parts[2]
            str2 = '@' + mapOfSegs[parts[1]]
            asm_code += [str1, 'D = A', str2, 'A = M + D', 'D = M', 
                         '@SP', 'A = M', 'M = D', '@SP', 'M = M + 1']
        if(parts[1] == 'constant'):
            str1 = '@' + parts[2]
            asm_code += [str1, 'D = A', '@SP', 'A = M', 
                         'M = D', '@SP', 'M = M+1']
        if(parts[1] == 'static'):
            str1 = '@foo.' + parts[2]
            asm_code += [str1, 'D = M', '@SP', 'A = M', 'M = D', 
                         '@SP', 'M = M + 1']
        if(parts[1] == 'temp'):
            str1 = '@' + parts[2]
            str2 = '@5'
            asm_code += [str1, 'D = A', str2, 'A = A + D', 'D = M', 
                         '@SP', 'A = M', 'M = D', '@SP', 'M = M + 1']
        if(parts[1] == 'pointer'):
            str1 = '@' + map[parts[2]]
            asm_code += [str1, 'D = M', '@SP', 'A = M', 
                         'M = D', '@SP', 'M = M + 1'] 
        return asm_code   

    @staticmethod
    def translate_pop(line:str) -> list[str]:
        listOfSegs : list[str] = ['local', 'argument', 'this', 'that',
                        'constant', 'static', 'temp', 'pointer']
        mapOfSegs : dict[str, str] = {'local' : 'LCL', 'argument' : 'ARG',
                                       'this' : 'THIS', 'that' : 'THAT'}

        parts:list[str] = line.split()
        str1:str
        str2:str
        map:dict[str, str] = {'0' : 'THIS', '1' : 'THAT'}     
        asm_code:list[str] = []

        if(parts[1] in listOfSegs[:4]): #LCL,ARG,THIS,THAT
            str1 = '@' + parts[2]
            str2 = '@' + mapOfSegs[parts[1]]
            asm_code += [str1, 'D = A', str2, 'D = M + D', '@R13', 'M = D', 
                         '@SP', 'M = M - 1', 'A = M', 'D = M', '@R13', 
                         'A = M', 'M = D']
        if(parts[1] == 'static'):
            str1 = '@foo.' + parts[2]
            asm_code += ['@SP', 'M = M - 1', 'A = M', 
                         'D = M', str1, 'M = D']
        if(parts[1] == 'temp'):
            str1 = '@' + parts[2]
            str2 = '@5'
            asm_code += [str1, 'D = A', str2, 'D = A + D', '@R13', 
                         'M = D', '@SP', 'M = M - 1', 'A = M', 'D = M', 
                         '@R13', 'A = M', 'M = D']    
        if(parts[1] == 'pointer'):
            str1 = '@' + map[parts[2]]
            asm_code += ['@SP', 'M = M - 1', 'A = M', 
                         'D = M', str1, 'M = D']
        return asm_code

    @staticmethod
    def arithm_map(lineNum:int) -> dict[str, list[str]]:
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
                           '@EQUAL' + str(lineNum), 'D;JEQ', '@NOTEQ' + str(lineNum), 
                           '0;JMP', '(EQUAL' + str(lineNum) + ')', '@SP', 'A = M', 
                           'M = -1', '@ENDOP' + str(lineNum), '0;JMP',
                           '(NOTEQ' + str(lineNum) + ')', '@SP', 'A = M', 'M = 0', 
                           '(ENDOP' + str(lineNum) + ')',
                           '@SP', 'M = M + 1'],
                  'gt'  : ['@SP', 'M = M - 1', 'A = M', 'D = M',
                           '@SP', 'M = M - 1', 'A = M', 'D = M - D',
                           '@GT' + str(lineNum), 'D;JGT', '@NOTGT' + str(lineNum), 
                           '0;JMP', '(GT' + str(lineNum) + ')', '@SP', 'A = M', 
                           'M = -1', '@ENDOP' + str(lineNum), '0;JMP',
                           '(NOTGT' + str(lineNum) + ')', '@SP', 'A = M', 'M = 0', 
                           '(ENDOP' + str(lineNum) + ')',
                           '@SP', 'M = M + 1'],
                  'lt'  : ['@SP', 'M = M - 1', 'A = M', 'D = M',
                           '@SP', 'M = M - 1', 'A = M', 'D = M - D',
                           '@LT' + str(lineNum), 'D;JLT', 
                           '@NOTLT' + str(lineNum), '0;JMP',
                           '(LT' + str(lineNum) + ')', '@SP', 'A = M', 'M = -1', 
                           '@ENDOP' + str(lineNum), '0;JMP',
                           '(NOTLT' + str(lineNum) + ')', '@SP', 'A = M', 'M = 0', 
                           '(ENDOP' + str(lineNum) + ')',
                           '@SP', 'M = M + 1'],
                  'and' :  ['@SP', 'M = M - 1', 'A = M', 'D = M',
                            '@SP', 'M = M - 1', 'A = M', 'M = M & D',
                            '@SP', 'M = M + 1'],
                  'or'  : ['@SP', 'M = M - 1', 'A = M', 'D = M',
                            '@SP', 'M = M - 1', 'A = M', 'M = M | D',
                            '@SP', 'M = M + 1'],
                  'not' : ['@SP', 'A = M', 'M = !M',
                           '@SP', 'M = M + 1']}
    
    @staticmethod
    def translate_label(line:str) -> list[str]:
        parts:list[str] = line.split()
        return ['(' + parts[1] + ')']
    
    @staticmethod
    def translate_unconditional_branch(line:str) -> list[str]:
        parts:list[str] = line.split()
        retlst:list[str] = ["@" + parts[1], "0;JMP"]
        return retlst
    
    @staticmethod
    def translate_conditional_branch(line:str) -> list[str]:
        parts:list[str] = line.split()
        retlst:list[str] = ["@SP", "M=M-1", "A = M", "D = M",
                            "@" + parts[1], "D;JNE"]
        return retlst
    
    @staticmethod
    def translate_function(line:str) -> list[str]:
        parts:list[str] = line.split()
        functionName:str = parts[1]
        nVars:int = int(parts[2])
        retlst:list[str] = ['(' + functionName + ')']
        for i in range(nVars):
            retlst += VmProgram.translate_push("push constant 0")
        return retlst
    
    @staticmethod
    def translate_return(line:str) -> list[str]:
        retlst:list[str] = []
        retlst += VmProgram.load_helper("R14", "5")
        retlst += VmProgram.translate_pop("pop argument 0")
        retlst += ["@ARG", "D=M+1", "@SP", "M=D"]
        retlst += VmProgram.load_helper("THAT", "1")
        retlst += VmProgram.load_helper("THIS", "2")
        retlst += VmProgram.load_helper("ARG", "3")
        retlst += VmProgram.load_helper("LCL", "4")
        retlst += ["@R14", "A=M", "0;JMP"]

        return retlst

    @staticmethod
    def translate_call(line:str, lineNum:int) -> list[str]:
        parts:list[str] = line.split()
        retlst:list[str] = ["@" + parts[1] + "Ret." + str(lineNum), "D=A", "@SP",
                            "A=M", "M=D", "@SP", "M = M+1"]
        retlst += VmProgram.push_helper("LCL")
        retlst += VmProgram.push_helper("ARG")
        retlst += VmProgram.push_helper("THIS")
        retlst += VmProgram.push_helper("THAT")
        retlst += ["@" + parts[2], "D=A", "@5", "D=D+A",
                   "@SP", "A=M", "D=A-D", "@ARG", "M=D",
                   "@SP", "D=M", "@LCL", "M=D"]
        retlst += VmProgram.translate_unconditional_branch("goto " + parts[1])
        retlst += VmProgram.translate_label("label " + parts[1] + "Ret." + str(lineNum))
        return retlst
     
    @staticmethod
    def push_helper(memSeg : str) -> list[str]:
        retLst:list[str] = ['@' + memSeg, "D=M", "@SP", 
                            "A=M", "M=D", "@SP", "M=M+1"]
        return retLst

    @staticmethod
    def load_helper(dest: str, offset:str) ->list[str]:
        retLst:list[str] = ["@LCL", "D=M", "@" + offset,
                            "A=D-A", "D=M", "@" + dest,
                            "M=D"]
        return retLst
    
if __name__ == '__main__':
    program = VmProgram.load_from('Main.vm')
    asm_code = program.translate()
    print(asm_code)
    program.write_to_file('Main.asm', asm_code) 
