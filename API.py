from flask import Flask, request, jsonify
from datetime import datetime
import pymongo
import json
import bson
from bson import ObjectId 
from bson import json_util 

app = Flask(__name__)

MONGO_HOST="localhost"
MONGO_PUERTO="27017"
MONGO_TIEMPO_FUERA=1000

MONGO_URI="mongodb://"+MONGO_HOST+":"+MONGO_PUERTO+"/"

try:
    cliente=pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=MONGO_TIEMPO_FUERA)
    cliente.server_info()
    db = cliente["my_database"]
    services_collection  =  db["services"]
    mailing_collection = db["mailing"] 
    print("Conección a Mongo exitosa")
    
except pymongo.errors.ServerSelectionTimeoutError as errorTiempo:
    print("Tiempo excedido"+errorTiempo)
except pymongo.errors.ConnectionFailure as errorConexion:
    print("Fallo al conectarse a Mongodb"+errorConexion)



@app.route("/services", methods=["POST"]) # Incertar registros en la base
def add_service_route():
    service = request.get_json()
    service["id"] = generate_service_id()
    current_time = datetime.now()
    service['created_at'] = current_time
    service['updated_at'] = current_time
    rating = request.json.get('rating', None)

    if rating is not None and (not isinstance(rating, int) or rating < 1 or rating > 5):
        return jsonify({"error": "Invalid rating. Please enter a number between 1 and 5."}), 400

    add_service(service)
    return jsonify({"message": "Service added successfully", "service_id": service["id"]}), 201


# Counter for generating sequential service IDs
service_id_counter = 0

def generate_service_id():
    global service_id_counter
    service_id_counter += 1
    return service_id_counter

# Counter file path
COUNTER_FILE = "service_id_counter.json"

def load_counter():
    try:
        with open(COUNTER_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return 0

def save_counter(counter_value):
    with open(COUNTER_FILE, "w") as f:
        json.dump(counter_value, f)

def generate_service_id():
    global service_id_counter
    service_id_counter = load_counter()
    service_id_counter += 1
    save_counter(service_id_counter)
    return service_id_counter


def add_service(service):
        services_collection.insert_one(service)
        print("Servicio agregado exitosamente")

def add_mailing_record_route():
    mailing_record = request.get_json()
    add_mailing_record(mailing_record)
    return jsonify({"message": "Mailing record added successfully"}), 201
def add_mailing_record(mailing_record):
        mailing_collection.insert_one(mailing_record)
        print("Mailing record added successfully")


@app.route("/consult_services", methods=["GET"])
def get_services():
        services = list(services_collection.find())

    
        for service in services:
            service["_id"] = str(service["_id"])


        return jsonify({"services": services}), 200 

    

@app.route("/services/<int:service_id>",  methods=["GET"]) 
def  get_service_by_id(service_id):
     
     db = cliente["my_database"]
     

     #  Buscar  el  servicio  por  su  ID  en  la  colección
     service  =  services_collection.find_one({"id":  service_id})

     #  Verificar  si  se  encontró  el  servicio
     if  service is  None :
         return  jsonify({"error ":  "No  existe  un  servicio  con  el  ID  especificado"}),  404

     #  Convertir  el  ObjectId  a  una  cadena  antes  de  devolver  el  resultado  JSON
     service['_id']  =  str(service['_id'])

     #  Devolver  el  servicio  encontrado
     return  json_util.dumps(service),  200


@app.route("/update_services/<int:service_id>", methods=["PUT"])
def update_services(service_id):

    updated_service_data = request.get_json()

    # Verifica si el documento con el ID dado existe
    existing_service = services_collection.find_one({"id": (service_id)})

    if existing_service:

         # Valida el rating recibido
        rating = updated_service_data.get("rating")
        if rating is not None:
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return jsonify({"error": "La calificación debe ser un número entre 1 y 5"}), 400

        # Actualiza el documento con los nuevos datos
        services_collection.update_one({"id": (service_id)}, {"$set": updated_service_data})
        updated_service_data["id"] = str(existing_service["id"])  # Mantén el formato del id

        return jsonify({"message": "Servicio actualizado con éxito", "updated_service": updated_service_data}), 200
    else:
        return jsonify({"error": "Servicio no encontrado con el ID dado"}), 404
    
app.run(debug=True)