
import dis
import sys
from obj import Frame, Function


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

    def push_frame(self, frame):
        self.call_stack.append(frame)
        self.frame = frame

    def pop_frame(self):
        self.call_stack.pop()
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
                    pass
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
        pass

    def execute(self, code_obj, global_names=None, local_names=None):
        """Entry point"""
        frame = self.make_frame(code_obj, global_names=global_names,
                                local_names=local_names)
        self.run_frame(frame)

