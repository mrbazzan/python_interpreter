
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
            method = getattr(self, instruction)
            if arg is None:
                method()
            else:
                method(arg)


instruction_sets = [
{
    "instructions": [
        ("LOAD_VALUE", 0),
        ("LOAD_VALUE", 1),
        ("ADD_TWO_VALUES", None),
        ("LOAD_VALUE", 2),
        ("ADD_TWO_VALUES", None),
        ("PRINT_ANSWER", None)
    ],
    "numbers" : [6, 7, 8]
},
{
    "instructions": [
        ("LOAD_VALUE", 0),
        ("STORE_NAME", 0),
        ("LOAD_VALUE", 1),
        ("STORE_NAME", 1),
        ("LOAD_NAME", 0),
        ("LOAD_NAME", 1),
        ("ADD_TWO_VALUES", None),
        ("PRINT_ANSWER", None)],
    "numbers": [1, 2],
    "names":   ["a", "b"]
}
]

for instruction_set in instruction_sets:
    interpreter = Interpreter()
    interpreter.execute(instruction_set)
    print(interpreter.environment)

