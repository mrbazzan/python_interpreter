
class Interpreter:
    def __init__(self):
        self.environment = {}
        self.stack = []

    def LOAD_VALUE(self, value):
        self.stack.append(value)

    def STORE_NAME(self, name):
        exp = self.stack.pop()
        self.environment[name] = exp

    def LOAD_NAME(self, name):
        self.stack.append(self.environment[name])

    def ADD_TWO_VALUES(self):
        second = self.stack.pop()
        first = self.stack.pop()
        total = first + second
        self.stack.append(total)

    def PRINT_ANSWER(self):
        answer = self.stack.pop()
        print(answer)

    def _parse_ptr(self, ptr, instruction, code_obj):
        """
        Helper method to get the right value for
        :ptr: associated with each instruction
        """

        arg = None
        numbers = ["LOAD_VALUE"]
        names = ["STORE_NAME", "LOAD_NAME"]

        if instruction in numbers:
            arg = code_obj["numbers"][ptr]
        elif instruction in names:
            arg = code_obj["names"][ptr]

        return arg

    def execute(self, code_obj):
        instruction_sets = code_obj.get("instructions")

        for instruction_set in instruction_sets:
            instruction, ptr = instruction_set
            arg  = self._parse_ptr(ptr, instruction, code_obj)

            if instruction == "LOAD_VALUE":
                self.LOAD_VALUE(arg)

            elif instruction == "STORE_NAME":
                self.STORE_NAME(arg)

            elif instruction == "LOAD_NAME":
                self.LOAD_NAME(arg)

            elif instruction == "ADD_TWO_VALUES":
                self.ADD_TWO_VALUES()

            elif instruction == "PRINT_ANSWER":
                self.PRINT_ANSWER()

