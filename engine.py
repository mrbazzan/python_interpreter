
class Interpreter:
    def __init__(self):
        self.stack = []

    def LOAD_VALUE(self, value):
        self.stack.append(value)

    def ADD_TWO_VALUES(self):
        second = self.stack.pop()
        first = self.stack.pop()
        total = first + second
        self.stack.append(total)

    def PRINT_ANSWER(self):
        answer = self.stack.pop()
        print(answer)

    def execute(self, code_obj):
        instruction_sets = code_obj.get("instructions")
        numbers = code_obj.get("numbers")

        for instruction_set in instruction_sets:
            instruction, ptr = instruction_set

            if instruction == "LOAD_VALUE":
                value = numbers[ptr]
                self.LOAD_VALUE(value)

            elif instruction == "ADD_TWO_VALUES":
                self.ADD_TWO_VALUES()

            elif instruction == "PRINT_ANSWER":
                self.PRINT_ANSWER()

