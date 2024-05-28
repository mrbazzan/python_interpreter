
# A PYTHON INTERPRETER

     written in Python

This interpreter is only focused on the last step in
the execution of a Python program. Its input is
instruction sets called ``bytecode``.

Bytecode is an intermediate representation of Python code.

NB: The bytecode is produced by Python 3.5 or earlier

```
Python               Bytecode                 Ouput
source  ------>->                ------>->
```

Dummy Example
-------------

```python

from engine import Interpreter

instruction_set = {
    "instructions": [
        ("LOAD_VALUE",  0),
        ("LOAD_VALUE", 1),
        ("ADD_TWO_VALUES", None),
        ("LOAD_VALUE", 2),
        ("ADD_TWO_VALUES", None),
        ("PRINT_ANSWER", None)
    ],
    "numbers" : [6, 7, 8]
}

interpreter = Interpreter()
interpreter.execute(instruction_set)

# It outputs `21`
```

For more information, read **interpreter.txt**


[Source](https://aosabook.org/en/500L/a-python-interpreter-written-in-python.html)
