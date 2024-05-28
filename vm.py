
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

    def run_frame(self, frame):
        pass

    def execute(self, code_obj, global_names=None, local_names=None):
        """Entry point"""
        frame = self.make_frame(code_obj, global_names=global_names,
                                local_names=local_names)
        self.run_frame(frame)

