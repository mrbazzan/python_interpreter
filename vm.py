
import dis
import sys
import operator
from obj import Block, Frame, Function


class VirtualMachineError(Exception):
    pass


class VirtualMachine:
    def __init__(self):
        self.call_stack = [] # It manages all the frame
        self.frame = None # The current frame
        self.return_value = None # The return value passed between frames
        self.exception = None

    def top(self):
        return self.frame.data_stack[-1]

    def pop(self):
        return self.frame.data_stack.pop()

    def push(self, *vals):
        return self.frame.data_stack.extend(vals)

    def popn(self, n):
        if not n:
            return []
        ret = self.frame.data_stack[-n:]
        self.frame.data_stack[-n:] = []
        return ret

    def jump(self, ip):
        """Change the last instruction to ip(instruction pointer)"""
        self.frame.last_instruction = ip

    def push_block(self, b_type, handler=None):
        self.frame.block_stack.append(
            Block(b_type, handler, len(self.frame.data_stack))
        )

    def pop_block(self):
        self.frame.block_stack.pop()

    def byte_SETUP_LOOP(self, dest):
        self.push_block('loop', dest)

    def byte_GET_ITER(self):
        self.push(iter(self.pop()))

    def byte_FOR_ITER(self, jump):
        obj = self.top()
        try:
            v = next(obj)
            self.push(v)
        except StopIteration:
            # if we have run through the obj, pop the obj
            # and the jump out of the setup loop
            self.pop()
            self.jump(jump)

    def byte_BREAK_LOOP(self):
        return 'break'

    def byte_POP_BLOCK(self):
        self.pop_block()

    BINARY_OPERATORS = {
        'POWER': pow,
        'ADD': operator.add,
        'SUBTRACT': operator.sub,
        'MULTIPLY': operator.mul,
        'MODULO': operator.mod,
    }

    def binaryOperator(self, op):
        x, y = self.popn(2)
        self.push(self.BINARY_OPERATORS[op](x, y))

    COMPARE_OPERATORS = [
        operator.lt, operator.le, operator.eq,
        operator.ne, operator.gt, operator.ge
    ]

    def byte_COMPARE_OP(self, opnum):
        x, y = self.popn(2)
        self.push(self.COMPARE_OPERATORS[opnum](x, y))

    def byte_JUMP_FORWARD(self, jump):
        self.jump(jump)

    def byte_JUMP_ABSOLUTE(self, jump):
        self.jump(jump)

    def byte_POP_JUMP_IF_TRUE(self, jump):
        truthy = self.pop()
        if truthy:
            self.jump(jump)

    def byte_POP_JUMP_IF_FALSE(self, jump):
        truthy = self.pop()
        if not truthy:
            self.jump(jump)

    def byte_LOAD_CONST(self, const):
        self.push(const)

    def byte_POP_TOP(self):
        self.pop()

    def byte_LOAD_NAME(self, name):
        f = self.frame
        if name in f.local_names:
            val = f.local_names[name]
        elif name in f.global_names:
            val = f.global_names[name]
        elif name in f.builtin_names:
            val = f.builtin_names[name]
        else:
            raise NameError("name '%s' is not defined" % name)
        self.push(val)

    def byte_STORE_NAME(self, name):
        self.frame.local_names[name] = self.pop()

    def byte_LOAD_FAST(self, name):
        if name in self.frame.local_names:
            val = self.frame.local_names[name]
        else:
            raise UnboundLocalError(
                "local variable '%s' referenced before assignment" % name
            )
        self.push(val)

    def byte_STORE_FAST(self, name):
        self.frame.local_names[name] = self.pop()

    def byte_LOAD_GLOBAL(self, name):
        f = self.frame
        if name in f.global_names:
            val = f.global_names[name]
        elif name in f.builtin_names:
            val = f.builtin_names[name]
        else:
            raise NameError("global name '%s' is not defined" % name)
        self.push(val)

    def byte_CALL_FUNCTION(self, arg):
        num_named_args, num_pos_args = divmod(arg, 256)

        named_args = {}
        for _ in range(num_named_args):
            k, v = self.popn(2)
            named_args[k] = v

        pos_args = self.popn(num_pos_args)

        func = self.pop()
        retval = func(*pos_args, **named_args)
        self.push(retval)

    def byte_MAKE_FUNCTION(self, argc):
        """
        :argc: number of keyword argument
        """
        name = self.pop()
        code = self.pop()
        defaults = self.popn(argc)
        globs = self.frame.global_names
        fn = Function(name, code, globs, defaults, None, self)
        self.push(fn)

    def byte_RETURN_VALUE(self):
        self.return_value = self.pop()
        return "return"

    def push_frame(self, frame):
        self.call_stack.append(frame)
        self.frame = frame

    def pop_frame(self):
        self.call_stack.pop()

        # Instead of this "if" block, could we have?
        # frame = self.call_stack.pop()
        # self.frame = frame.call_frame
        # I think we could but frame is not properly collected then
        # because we still store an instance of a discarded frame, and
        # I think moreover it is better to use the order in the call stack
        if self.call_stack:
            self.frame = self.call_stack[-1]
        else:
            self.frame = None

    def make_frame(self, code_obj, callargs={}, global_names=None, local_names=None):
        if global_names is not None and local_names is None:
            local_names = global_names
        elif self.call_stack:
            global_names = self.frame.global_names
            local_name = {}
        else:
            global_names = local_names = {
                "__builtins__": __builtins__,
                "__name__": "__main__",
                "__doc__": None,
                "__package__": None,
            }
        local_names.update(callargs)
        frame = Frame(code_obj, global_names, local_names, self.frame)
        return frame

    def unwind_block(self, block):
        """
        Unwind the values on the data stack corresponding
        to a given block.

        Remove the added items in the frame's data stack after
        the block was setup
        """
        while len(self.frame.data_stack) > block.f_ds_height:
            self.pop()

    def manage_block_stack(self, why):
        block = self.frame.block_stack[-1]

        self.pop_block()
        self.unwind_block(block)

        if block.type == 'loop' and why == 'break':
            why = None
            self.jump(block.handler)
            return why

        # If the line below is excluded, this function return None
        # which can be an issue when RETURN_VALUE instruction is processed
        # (it should return "return" so the while loop in `run_frame` can stop).
        return why

    def parse_byte_and_args(self):
        f = self.frame
        offset = f.last_instruction
        byte_code = f.code_obj.co_code[offset]
        f.last_instruction += 1
        byte_name = dis.opname[byte_code]

        # check if the bytecode has an argument
        if byte_code >= dis.HAVE_ARGUMENT:
            # NB: An instruction with argument is three bytes long; the last
            # two bytes are the argument
            arg = f.code_obj.co_code[f.last_instruction:f.last_instruction+2]
            f.last_instruction += 2

            # resolve the argument's 2 bytes
            arg_val = arg[0] + (arg[1] * 256)

            if byte_code in dis.hasconst:  # look up a constant
                arg = f.code_obj.co_consts[arg_val]
            elif byte_code in dis.hasname:
                arg = f.code_obj.co_names[arg_val]
            elif byte_code in dis.haslocal:
                arg = f.code_obj.co_varnames[arg_val]
            elif byte_code in dis.hasjrel: # calculate a relative jump
                arg = f.last_instruction + arg_val
            else:  # for instructions like BUILD_LIST, POP_JUMP_IF_FALSE
                arg = arg_val

            argument = [arg]
        else:
            argument = []

        return byte_name, argument

    def dispatch(self, byte_name, argument):
        """
        Get the corresponding method for each bytename.
        Exceptions are set on the virtual machine
        """

        # keep state of the interpreter. It is one of:
        # None, continue, break, exception, return
        why = None
        try:
            bytename_fn = getattr(self, "byte_%s" % byte_name, None)
            if bytename_fn is None:
                if byte_name.startswith("UNARY_"):
                    pass
                elif byte_name.startswith("BINARY_"):
                    self.binaryOperator(byte_name[len("BINARY_"):])
                else:
                    raise VirtualMachineError(
                        "unsupported bytecode type: %s" % byte_name
                    )
            else:
                why = bytename_fn(*argument)
        except:
            # sys.exc_info -> (type, value, traceback)
            self.exception = sys.exc_info()[:2] + (None, )
            why = "exception"

        return why

    def run_frame(self, frame):
        """
        Run a frame. Exceptions are raised, the return value is returned.
        """
        self.push_frame(frame)

        while True:
            byte_name, arguments = self.parse_byte_and_args()
            why = self.dispatch(byte_name, arguments)

            # this is especially useful for when we use the 'break'
            # statement, there is a need to take care of the values
            # in the data stack and block stack.
            while why and frame.block_stack:
                why = self.manage_block_stack(why)

            if why:
                break

        self.pop_frame()

        if why == 'exception':
            exc, val, tb = self.exception
            e = exc(val)
            e.__traceback__ = tb
            raise e

        return self.return_value

    def execute(self, code_obj, global_names=None, local_names=None):
        """Entry point"""
        frame = self.make_frame(code_obj, global_names=global_names,
                                local_names=local_names)
        self.run_frame(frame)

