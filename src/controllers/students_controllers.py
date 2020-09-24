from src.app import app
from flask import request, jsonify
from src.database import db
import requests


def user_already_in_db(collection, username):
    result = collection.find_one({"name": username})
    return result is not None and len(result) > 0


def user_exists_in_github(username):
    base_url = "https://github.com/"
    url = f"{base_url}{username}"
    response = requests.get(url)
    return response.status_code == 200


def insert_new_student(collection, name):
    new_student = {
        "name": name
    }

    result = collection.insert_one(new_student)
    return {"_id": str(result.inserted_id)}


@app.route("/student/create/<student_name>")
def create_student(student_name):
    '''
    receives: a string with the name of a student.
    purpose:    create a new entry in the students database.
                before inserting in the database validate that the user exists in github.
    returns: student_id
    '''
    collection = db.students

    if user_already_in_db(collection, student_name):
        return f"El usuario {student_name} ya existe en la BD."

    if user_exists_in_github(student_name):
        return jsonify(insert_new_student(collection, student_name))
    else:
        return f"El usuario {student_name} no existe en Github."

    return "No se ha guardado el alumno en la base de datos. Problema desconocido."


@app.route("/student/all")
def search_students():
    '''
    receives: no param.
    return: a list with all the student objects in the database.
    '''
    collection = db.students

    # Quito el campo _id de los datos a mostrar porque es un objeto y no es JSON serializable.
    cursor = collection.find({}, {'_id': False})

    return(jsonify(list(cursor)))
