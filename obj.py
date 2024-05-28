
import types
import inspect


def make_cell(value):
    """Create a real Python closure and grab a cell"""
    fn = (lambda x: lambda: x)(value)
    return fn.__closure__[0]


class Frame:
    def __init__(self, code_obj, global_names, local_names, call_frame):
        self.code_obj = code_obj
        self.global_names = global_names
        self.local_names = local_names
        self.call_frame = call_frame

        # https://github.com/nedbat/byterun/pull/37
        if call_frame and call_frame.global_names is global_names:
            self.builtin_names = call_frame.builtin_names

        # https://docs.python.org/3/reference/executionmodel.html#builtins-and-restricted-execution
        else:
            try:
                self.builtin_names = global_names["__builtins__"]
                if hasattr(self.builtin_names, "__dict__"):
                    self.builtin_names = self.builtin_names.__dict__
            except KeyError:
                self.builtin_names = {"None": None}

        self.data_stack = []
        self.block_stack = []
        self.last_instruction = 0


class Function:
    __slots__ = [
        "func_code", "func_name", "func_defaults", "func_globals",
        "func_locals", "func_dict", "func_closure",
        "__name__", "__dict__", "__doc__",
        "_vm", "_func",
    ]

    def __init__(self, name, code_obj, globs, defaults, closure, vm):
        self._vm = vm
        self.func_code = code_obj
        self.func_name = self.__name__ = name or code_obj.co_name
        self.func_defaults = tuple(defaults)
        self.func_globals = globs
        self.func_locals = self._vm.frame.local_names
        self.__dict__ = {}
        self.func_closure = closure
        self.__doc__ = code_obj.co_consts[0] if code_obj.co_consts else None

        kw = {
            "argdefs": self.func_defaults,
        }
        if closure:
            kw["closure"] = tuple(make_cell(0) for _ in closure)
        self._func = types.FunctionType(code_obj, globs, **kw)

    def __call__(self, *args, **kwargs):
        """When calling Function, a new frame is created and run"""
        callargs = inspect.getcallargs(self._func, *args, **kwargs)
        frame = self._vm.make_frame(
            self.func_code, callargs, self.func_globals, {}
        )
        return self._vm.run_frame(frame)

