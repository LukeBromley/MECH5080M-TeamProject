import os
from Library.model import Model

model = Model()
model.load_junction(os.path.join(os.path.dirname(__file__), "../Frontend/example_junction.junc"))


print(1)
