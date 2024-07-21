import argparse
from typing import List, Dict
from assembler import Assembler
from HackSimulator import HackComputer
import json

def file_read(file_name: str) -> List[str]:
    lines: List[str] = []
    with open(file_name, 'r') as file:
        lines = file.readlines()

    check_file = file_name.split(".")
    if check_file[1] == "asm":
        assembler: Assembler = Assembler.create()
        lines = assembler.assemble(lines)

    return lines

def file_write(str_list: List[str], file_name: str) -> None:
    ram_dict: Dict[str, int] = {}

    for entry in str_list:
        address, content = entry.split(":")
        ram_dict[address] = int(content)

    data: Dict[str, Dict[str, int]] = {"RAM": ram_dict}

    with open(file_name, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def parse_file_name(file_name: str) -> str:
    file: str = (file_name.split("/"))[-1]
    real_file_name = (file.split("."))[0]
    return (real_file_name + ".json")

def simulate(file_name: str, cycles: int) -> None:
    machine_code: List[str] = file_read(file_name)

    hackSim : HackComputer = HackComputer.create()
    RAMSlots : List[str] = hackSim.execute_instruction_set(machine_code, cycles)

    real_file_name: str = parse_file_name(file_name)
    file_write(RAMSlots, real_file_name)
        
    return

def main():
    parser = argparse.ArgumentParser(description="Simulate the execution of Hack assembly code.")
    parser.add_argument("input_file", type=str, help="The input file containing Hack assembly or machine code.")
    parser.add_argument("--cycles", type=int, default=10000, help="Number of cycles to execute.")

    args = parser.parse_args()
    
    simulate(args.input_file, args.cycles)

if __name__ == '__main__':
    main()
