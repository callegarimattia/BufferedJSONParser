# My solution to the streaming JSON parser problem for kind people at deepJudge.ai
# Mattia Callegari - 18.09.2024

# I decided to implement a simple FSM to parse the JSON object.
# The parser is stateful and it can be fed with chunks of data.
# The parser will return the parsed JSON object only when the get method is called.
# You can find the FSM in the encode function.
# I also left attached the tests that I used to develop the solution using TDD.
# Attached is also the diagram of the FSM that I used to implement the solution.


class StreamingJsonParser:
    def __init__(self) -> None:
        self.obj: dict = {}
        self.buffer = ""

    # Consumes a string and appends it to the buffer
    def consume(self, data: str) -> None:
        self.buffer += data

    # Returns the parsed JSON object
    # The object is parsed when get is called only if the buffer is not empty
    # If the buffer is empty, the object is returned as is
    def get(self) -> dict:
        if self.buffer == "":
            return self.obj
        self.obj = encode(self.buffer)
        self.buffer = ""
        return self.obj


# encode takes a string as input and returns the parsed JSON object
# if a key is truncated, it will ignore that key
# if the value is truncated, it will return a string with the key and the truncated value
# only dictionaries and strings are supported
# truncated dictionaries will be partially parsed with the same rules
# We assume that quotes are always double quotes.
def encode(data: str) -> dict:
    if len(data) == 0:
        return {}

    current_key = ""
    current_dict = {}
    current_string = ""
    state = "key"
    index = 1
    current_char = ""
    stack = []

    # remove all whitespaces
    # {"f o o ": "bar"} -> {"foo":"bar"} (this is not ideal, but it's a simplification)
    data = data.replace(" ", "")

    while index < len(data):
        current_char = data[index]

        if state == "key":
            if current_char == '"':
                state = "key_start"
            else:
                raise ValueError("Invalid JSON")

        elif state == "key_start":
            if current_char == '"':
                state = "key_end"
            else:
                current_key += current_char

        elif state == "key_end":
            if current_char == ":":
                state = "value"
            else:
                raise ValueError("Invalid JSON")

        elif state == "value":
            if current_char == '"':
                state = "string"
            elif current_char == "{":
                stack.append((current_key, current_dict))
                current_key = ""
                current_dict = {}
                state = "key"
            else:
                raise ValueError("Invalid JSON")

        elif state == "string":
            if current_char == '"':
                current_dict[current_key] = current_string
                current_key = ""
                current_string = ""
                state = "value_end"
            else:
                current_string += current_char

        elif state == "value_end":
            if current_char == ",":
                state = "key"
            elif current_char == "}":
                # if the stack is not empty, it means that a dictionary was present
                if len(stack) > 0:
                    key, parent = stack.pop()
                    parent[key] = current_dict
                    current_dict = parent
                    state = "value_end"
                else:
                    break
            else:
                raise ValueError("Invalid JSON")

        index += 1

    # if the state is string, it's a truncated string
    if state == "string":
        current_dict[current_key] = current_string

    # if the stack is not empty, it means that a truncated dictionary was present
    while len(stack) > 0:
        key, parent = stack.pop()
        parent[key] = current_dict
        current_dict = parent

    return current_dict
