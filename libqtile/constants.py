class Obj:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

constants = [
    "TOP",
    "LEFT",
    "BOTTOM",
    "RIGHT",
    "FLOATING",
    "STRETCH",
    "CENTER",
    "UNSPECIFIED",
    "TRANSPARENT",
]

for name in constants:
    vars()[name] = Obj(name)

