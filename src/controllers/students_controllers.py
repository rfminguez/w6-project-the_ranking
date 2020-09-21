from src.app import app
from flask import request, jsonify
from src.database import db
import requests


def user_already_in_db(collection, username):
    return collection.find({"name": username}).count() > 0


def user_exists_in_github(username):
    base_url = "https://github.com/"
    url = f"{base_url}{username}"
    response = requests.get(url)
    return response.status_code == 200


@app.route("/student/create/<student_name>")
def create_student(student_name):
    '''
    receives: a string with the name of a student.
    purpose:    create a new entry in the students database.
                before inserting in the database validate that the user exists in github.
    returns: student_id
    '''
    collection = db.students

    new_student_document = {
        "name": student_name
    }

    if user_already_in_db(collection, student_name):
        return f"El usuario {student_name} ya existe en la BD."

    # Si el usuario existe en github los inserta en la base de datos
    if user_exists_in_github:
        result = collection.insert_one(new_student_document)
        return {"_id": str(result.inserted_id)}

    return f"El usuario {student_name} no existe en Github."


@app.route("/student/all")
def search_students():
    '''
    receives: no param.
    return: a list with all the student objects in the database.
    '''
    collection = db.students

    # Quito el campo _id porque es un objeto y no es JSON serializable.
    cursor = collection.find({}, {'_id': False})

    return(jsonify(list(cursor)))

