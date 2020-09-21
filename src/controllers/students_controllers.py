from src.app import app
from flask import request
# from src.database import db

@app.route("/student/create/<student_name>")
def create_student(student_name):
    '''
    receives: a string with the name of a student.
    purpose: create a new entry in the students database.
    returns: student_id
    '''
    return f"[TO-DO] Create Student '{student_name}' and save into DB."

@app.route("/student/all")
def search_students():
    '''
    receives: no param.
    return: a list with all the student objects in the database.
    '''
    return f"[TO-DO] Lista de todos los estudiantes en la DB."
