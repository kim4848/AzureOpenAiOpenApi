class FunctionDefinition:
    def __init__(self, name: str, description: str, parameters: dict, endpoint: str, method: str):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.endpoint = endpoint
        self.method = method

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "endpoint": self.endpoint,
            "method": self.method
        }

class Tool:
    def __init__(self, function: FunctionDefinition):
        self.type = "function"
        self.function = function

    def to_dict(self):
        return {
            "type": self.type,
            "function": self.function.to_dict()
        }
