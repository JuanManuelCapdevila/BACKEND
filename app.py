from flask import Flask, request, jsonify
import subprocess
import os
import re

app = Flask(__name__)

# Ruta para ejecutar el modelo OPL
@app.route('/optimize', methods=['POST'])
def ejecutar_modelo():
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.json

        # Generar archivo .dat con los datos recibidos
        generate_dat_file(data)

        # Ejecutar el modelo OPL utilizando los datos
        result = run_opl_model()

        # Devolver el resultado de la ejecución
        return jsonify({"resultado": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_dat_file(data):
    """
    Generar el archivo .dat que es utilizado por el modelo OPL
    basado en los datos recibidos desde el request body.
    """
    try:
        with open("input_data.dat", "w") as f:
            # Escribir los parámetros principales en el archivo .dat
            f.write(f"maxVehicles = {data['maxVehicles']};\n")
            f.write(f"capacity = {data['capacity']};\n")
            f.write(f"depotx = {data['depotx']};\n")
            f.write(f"depoty = {data['depoty']};\n")
            f.write(f"horizon = {data['horizon']};\n")

            # Escribir los nodos en formato adecuado para OPL
            f.write("custNode = {\n")
            for node in data['nodes']:
                f.write(f"    <{node['nodoID']}, {node['latitud']}, {node['longitud']}, {node['demanda']}, "
                        f"{node['tiempoInicio']}, {node['tiempoFin']}, {node['servicioDuración']}>,\n")
            f.write("};\n")

    except Exception as e:
        raise Exception(f"Error al generar el archivo .dat: {str(e)}")


def run_opl_model():
    """
    Función para ejecutar el modelo OPL y retornar los resultados.
    Asumiendo que el archivo modelo.mod y input_data.dat están en el mismo directorio.
    """
    try:
        # Define el comando para ejecutar el modelo OPL
        command = [
            'oplrun',  # Comando para ejecutar OPL (asegúrate de tener CPLEX y OPL configurados)
            'models/cvrptw.mod',  # Ruta al archivo del modelo OPL
            'input_data.dat'  # Archivo con los datos de entrada
        ]
        
        # Ejecutar el comando y capturar el resultado
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Error al ejecutar el modelo OPL: {result.stdout}")
        
        # Procesar la salida del modelo OPL y devolver el resultado deseado
        return parse_solution(result.stdout)

    except Exception as e:
        raise Exception(f"Error al ejecutar el modelo: {str(e)}")



import re

def parse_solution(result):
    # Buscar el valor objetivo
    objective_pattern = r"OBJECTIVE:\s*([\d.]+)"
    objective_match = re.search(objective_pattern, result)
    objective_value = objective_match.group(1) if objective_match else "No disponible"
    
    # Buscar el número de vehículos usados
    vehicles_pattern = r"NÃºmero de vehÃ­culos usados: (\d+)"
    vehicles_match = re.findall(vehicles_pattern, result)
    vehicles_used = vehicles_match[-1] if vehicles_match else "No disponible"
    
    # Buscar el orden de los nodos atendidos (previous)
    previous_pattern = r"previous\((.*?)\)"
    previous_match = re.search(previous_pattern, result)
    previous_order = previous_match.group(1) if previous_match else "No disponible"
    previous_order = previous_order.split()  # Convertimos el string en una lista de números
    
    # Buscar el vehículo asignado a cada nodo (vehicle)
    vehicle_pattern = r"vehicle\((.*?)\)"
    vehicle_match = re.search(vehicle_pattern, result)
    vehicle_assignments = vehicle_match.group(1) if vehicle_match else "No disponible"
    vehicle_assignments = vehicle_assignments.split()  # Convertimos el string en una lista de números
    
    # Buscar el tiempo de inicio de servicio (startServ)
    start_pattern = r"startServ\((.*?)\)"
    start_match = re.search(start_pattern, result)
    start_serv_times = start_match.group(1) if start_match else "No disponible"
    start_serv_times = start_serv_times.split()  # Convertimos el string en una lista de números
    
    # Buscar las cargas de los vehículos (load)
    load_pattern = r"load\((.*?)\)"
    load_match = re.search(load_pattern, result)
    load_values = load_match.group(1) if load_match else "No disponible"
    load_values = load_values.split()  # Convertimos el string en una lista de números
    
    # Buscar el tiempo de finalización del servicio (endServ)
    end_pattern = r"endServ\((.*?)\)"
    end_match = re.search(end_pattern, result)
    end_serv_times = end_match.group(1) if end_match else "No disponible"
    end_serv_times = end_serv_times.split()  # Convertimos el string en una lista de números

    # Crear un diccionario con los resultados
    parsed_result = {
        "objective_value": objective_value,
        "vehicles_used": vehicles_used,
        "previous": previous_order,
        "vehicle": vehicle_assignments,
        "startServ": start_serv_times,
        "load": load_values,
        "endServ": end_serv_times,
    }

    
    return parsed_result




if __name__ == '__main__':
    app.run(debug=True)
