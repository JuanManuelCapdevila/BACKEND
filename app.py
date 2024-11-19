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
@app.route('/config', methods=['GET', 'PUT', 'POST'])
def config():
    if request.method == 'GET':
        # Obtener la configuración actual
        config = Config.query.first()
        if config:
            return jsonify(config.to_dict()), 200
        else:
            return jsonify({'message': 'No existe una configuración establecida'}), 404

    elif request.method == 'PUT':
        # Actualizar la configuración existente
        data = request.get_json()
        config = Config.query.first()
        if config:
            for key, value in data.items():
                setattr(config, key, value)
            db.session.commit()
            return jsonify({'message': 'Configuración actualizada'}), 200
        else:
            return jsonify({'message': 'No existe una configuración para modificar'}), 404

    elif request.method == 'POST':
        # Crear una nueva configuración
        data = request.get_json()
        new_config = Config(**data)
        db.session.add(new_config)
        db.session.commit()
        return jsonify({'message': 'Configuración creada exitosamente'}), 201

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