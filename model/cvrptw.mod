// --------------------------------------------------------------------------
// Licensed Materials - Property of IBM
// Problem: Capacitated Vehicle Routing Problem with Time Windows (CVRPTW)
// --------------------------------------------------------------------------

using CP;

// ------------------------------------------------------------
// Definición del problema
// ------------------------------------------------------------
/*
En el CVRPTW, una flota de vehículos con capacidad limitada parte de un depósito,
atiende a una lista de clientes con demanda conocida y regresa al depósito.
Cada cliente debe ser atendido en un intervalo de tiempo específico.
El objetivo es minimizar la distancia total recorrida.
*/

// ------------------------------------------------------------
// Definición de datos y parámetros
// ------------------------------------------------------------
tuple Node {
  key int id;      // Identificador único
  float x;         // Coordenada X (latitud)
  float y;         // Coordenada Y (longitud)
  int demand;      // Demanda del cliente
  int begin;       // Inicio de la ventana de tiempo (en minutos)
  int end;         // Fin de la ventana de tiempo (en minutos)
  int service;     // Tiempo de servicio requerido (en minutos)
}

// Parámetros generales
int maxVehicles = ...;  // Máximo número de vehículos
int capacity = ...;     // Capacidad de cada vehículo
float depotx = ...;     // Coordenada X del depósito
float depoty = ...;     // Coordenada Y del depósito
int horizon = ...;      // Horizonte temporal (en minutos)
int TIME_FACTOR = 10;   // Factor para ajustar unidades de tiempo

// Conjunto de clientes cargados
{Node} custNode = ...; 

// Rango y variables relacionadas con nodos y vehículos
int n = 1 + max(c in custNode) c.id;
range C = 0 .. n - 1;                      // Clientes
range N = 0 .. n + 2 * maxVehicles - 1;    // Todos los nodos (clientes y auxiliares)
range V = 0 .. maxVehicles - 1;            // Vehículos
range SINKS = n + maxVehicles .. n + 2 * maxVehicles - 1; // Nodos sumideros

{int} C_AND_SINKS = {i | i in C} union {i | i in SINKS}; // Clientes + Sumideros
int sourceOf[v in V] = n + v;
int sinkOf[v in V] = n + maxVehicles + v;

Node node[i in N] = 
  (i in C) 
    ? item(custNode, <i>) 
    : <i, depotx, depoty, 0, 0, TIME_FACTOR * horizon, 0>;

// Matriz de tiempos de viaje entre nodos
int ttToNode[toNode in N, fromNode in N] = ftoi(floor(
  TIME_FACTOR * sqrt(
    (node[toNode].x - node[fromNode].x) ^ 2 + 
    (node[toNode].y - node[fromNode].y) ^ 2)
));

// ------------------------------------------------------------
// Declaración de variables de decisión
// ------------------------------------------------------------
dvar int previous[i in N] in N;  // Nodo anterior en la ruta
dvar int vehicle[i in N] in V;  // Vehículo asignado a cada nodo
dvar int load[i in V] in 0 .. capacity;  // Carga transportada por cada vehículo
dvar int startServ[i in N] in 
  TIME_FACTOR * node[i].begin .. TIME_FACTOR * node[i].end; // Inicio de servicio
dvar int endServ[i in N] in 
  TIME_FACTOR * (node[i].begin + node[i].service) .. 
  TIME_FACTOR * (node[i].end + node[i].service); // Fin de servicio
dvar int used in 1 .. maxVehicles; // Número de vehículos usados

// ------------------------------------------------------------
// Configuración y función objetivo
// ------------------------------------------------------------
execute {
  cp.addKPI(used, "Número de vehículos usados");
  cp.param.TimeLimit = 10;
  cp.param.LogPeriod = 50000;
}

minimize 
  (sum(i in C_AND_SINKS) ttToNode[i][previous[i]]) / TIME_FACTOR; // Minimizar distancia total

// ------------------------------------------------------------
// Restricciones
// ------------------------------------------------------------
subject to {
  // Restricción de subcircuito
  subCircuit(previous);
  forall (i in N) previous[i] != i;

  // Fuentes y sumideros
  forall (v in V) {
    previous[sourceOf[v]] == sinkOf[(v + 1) % maxVehicles];
    vehicle[sourceOf[v]] == v;
    vehicle[sinkOf[v]] == v;
    startServ[sourceOf[v]] == 0;
  }

  // Asignación de vehículos a clientes
  forall (i in C)
    vehicle[i] == vehicle[previous[i]];

  // Gestión de carga en vehículos
  pack(load, vehicle, all(i in N) node[i].demand);

  // Gestión de tiempos de servicio
  forall (i in N) 
    endServ[i] == startServ[i] + TIME_FACTOR * node[i].service;
  forall (i in C_AND_SINKS) 
    startServ[i] == maxl(
      TIME_FACTOR * node[i].begin, 
      endServ[previous[i]] + ttToNode[i][previous[i]]
    );

  // Restricción sobre el número de vehículos usados
  used == sum(v in V) (previous[sinkOf[v]] != sourceOf[v]);

  // Inferencia para mejorar la búsqueda
  inferred(vehicle);
  inferred(load);
  inferred(startServ);
  inferred(endServ);
  inferred(used);
}
