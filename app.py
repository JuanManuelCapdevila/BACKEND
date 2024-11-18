from flask import Flask, request, jsonify
from models import db, Config, Node

# VRPTW -> Vehicle Routing Problem with Time Windows

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vrptw.db'
db.init_app(app)

# Crear todas las tablas
with app.app_context():
    db.create_all()

# Ruta para configurar el problema
@app.route('/config', methods=['POST', 'GET'])
def config():
    if request.method == 'POST':
        data = request.get_json()
        config = Config(**data)
        db.session.add(config)
        db.session.commit()
        return jsonify({'message': 'Configuración guardada'}), 201
    else:
        configs = Config.query.all()
        return jsonify([config.to_dict() for config in configs]), 200

# Ruta para agregar nodos a una configuración
@app.route('/optimization', methods=['POST'])
def cvrptw():
    data = request.get_json()
    config_id = data.pop('config_id')
    config = Config.query.get(config_id)

    nodes = []
    for node_data in data['nodes']:
        node = Node(
            config=config,
            latitud=node_data['latitud'],
            longitud=node_data['longitud'],
            demanda=node_data['demanda'],
            tiempoInicio=node_data['tiempoInicio'],
            tiempoFin=node_data['tiempoFin'],
            servicioDuración=node_data['servicioDuración']
        )
        nodes.append(node)

    db.session.add_all(nodes)
    db.session.commit()
    return jsonify({'message': 'Nodos agregados'}), 201

# Función auxiliar para serializar un objeto
def to_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}
Config.to_dict = to_dict
Node.to_dict = to_dict

if __name__ == '__main__':
    app.run(debug=True)