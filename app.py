from docplex.mp.model import Model
from flask import request, jsonify

from docplex.mp.model import Model
from docplex.mp.model_reader import ModelReader
from flask import request, jsonify
import os

class Optimizer:
    def __init__(self, data):
        self.data = data
        self.model_path = os.path.join(os.path.dirname(__file__), 'model', 'cvrptw.mod')

    def solve_model(self):
        mdl = ModelReader().read(self.model_path)
        mdl.add_data(self.data)
        solution = mdl.solve()

        if solution:
            return {'solution': solution.as_dict()}
        else:
            return {'message': 'No se encontró solución'}

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()
    optimizer = Optimizer(data)
    result = optimizer.solve_model()
    return jsonify(result), 201
