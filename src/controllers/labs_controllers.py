from src.app import app
from flask import request
from src.database import db
from bson.objectid import ObjectId, InvalidId
from flask import jsonify
from datetime import datetime
import numpy as np


def lab_already_in_db(collection, lab_name):
    result = collection.find_one({"name": lab_name})
    return result is not None and len(result) > 0


def insert_new_lab(collection, lab_name):
    new_lab = {
        "name": lab_name,
        "prefix": f"[{lab_name}]"
    }

    result = collection.insert_one(new_lab)
    return {"_id": str(result.inserted_id)}


@app.route("/lab/create", methods = ['POST'])
def create_lab():
    '''
    receives:   a lab name via POST method.
    purpose:    create a new document in the labs collection.
    returns:    _id of the lab once inserted in the DB.
    '''
    collection = db.labs

    lab_name = request.json["name"]

    if lab_already_in_db(collection, lab_name):
        return f"El lab {lab_name} ya existe en la BD."

    return insert_new_lab(collection, lab_name)


@app.route("/lab/<lab_id>/search")
def search_into_lab(lab_id):
    '''
    receives:   a lab name.
    purpose:    analyze students submissions on specific lab.
                    what we have to do is first select all the user_id in the students DB 
                    and then analyze the activity of theses students in the lab given as 
                    parameter. 

    return: For each student in the lab:
            - number of open PR
            - number of closed PR
            - percentage of completeness (closed vs open)
            - number of missing PR from students
            - list of unique memes used for that lab
            - instructor grade time in hours (pr_closetime - last_commit_time)
            Important:  remember that some labs are not individual and you have to
                        find the student names in the body of the PR.
    '''
    try:
        lab_by_id_query = {"_id": ObjectId(lab_id)}

        # Hago la consulta quitando el campo _id de los datos devueltos porque es un objeto y no es JSON serializable.
        lab = db.labs.find_one(lab_by_id_query, projection={'_id': False})
        
        if lab is None:
            return f"Lab con id '{lab_id}' no encontrado."

        # Creo un diccionario vacío con el resultado
        result = {}
        result["name"] = lab["name"]

        # Busco los pull requests abiertos asociados a ese proyecto
        open_pull_requests_query =  {"lab_name": lab["name"], "state": "open"}
        open_pull_requests = db.pull_requests.find(open_pull_requests_query).count()
        result["open_pull_requests"] = open_pull_requests

        # Busco los pull requests cerrados asociados a ese proyecto
        closed_pull_requests_query =  {"lab_name": lab["name"], "state": "closed"}
        closed_pull_requests = db.pull_requests.find(closed_pull_requests_query).count()
        result["closed_pull_requests"] = closed_pull_requests

        # Calculo porcentaje Pull Requests cerradas vs Pull Requests abiertas
        total_pull_requests = open_pull_requests + closed_pull_requests
        percent_open_pull_requests = round(open_pull_requests / total_pull_requests, 2)
        percent_closed_pull_requests = round(closed_pull_requests / total_pull_requests, 2) 
        result["percent_open_pull_requests"] = percent_open_pull_requests * 100
        result["percent_closed_pull_requests"] = percent_closed_pull_requests * 100

        # Alumnos que enviaron pull requests a este lab
        pull_requests_by_lab_name = {"lab_name": lab["name"]}
        pull_requests_students_cursor = db.pull_requests.find(pull_requests_by_lab_name, projection={ "students": True })
        students_with_pull_requests = []
        for pull_request in pull_requests_students_cursor:
            students_with_pull_requests += pull_request["students"]
        result["students_with_pull_request"] = students_with_pull_requests

        # Alumnos que no enviaron pull requests a este lab.
        # Busca entre los alumnos que hay registrados en la colección de "students" los
        # que no están entre los si han hecho pull request al proyecto.
        students_query = {}
        students_cursor = db.students.find(students_query, projection={'name': True})
        students_without_pull_request = []
        for student in students_cursor:
            if student["name"] not in students_with_pull_requests:
                students_without_pull_request.append(student["name"])
        result["students_without_pull_request"] = students_without_pull_request

        # Missing pull requests (el conteo de la lista de alumnos de arriba, los que no han enviado pull request):
        result["missing_pull_requests"] = len(students_without_pull_request)

        # Listado de memes únicos en el lab
        pull_requests_meme_cursor = db.pull_requests.find(pull_requests_by_lab_name, projection={ "memes": True })
        memes = []
        for pull_request in pull_requests_meme_cursor:
            for meme in pull_request["memes"]:
                if meme not in memes:
                    memes.append(meme)
        result["memes"] = memes

        # Instructors grade time.
        # Esto solo lo hago solo con los pull requests cerrados.
        pull_request_times_cursor = db.pull_requests.find(closed_pull_requests_query, projection={"asignees": True, "closed_at": True, "commit_dates": True})
        instructors = {}
        for pull_request in pull_request_times_cursor:
            instructor_name = pull_request["asignees"][0]
            # Si el instructor no está en el diccionario lo añado
            if instructor_name not in instructors.keys():
                instructors[instructor_name] = []
            close_time_str = pull_request["closed_at"]
            # Los commits están ordenados de más antiguo a más reciente así que me quedo con el último
            open_time_str = pull_request["commit_dates"][-1]
            # Hago la resta de close_time - open time en horas y las añado al total de cada instructor
            # Formato de la fecha original: "2020-09-10T16:18:20Z"
            close_time = datetime.strptime(close_time_str, "%Y-%m-%dT%H:%M:%SZ")
            open_time = datetime.strptime(open_time_str, "%Y-%m-%dT%H:%M:%SZ")
            #instructors[instructor_name].append((open_time_str, open_time, close_time_str, close_time))
            # El tiempo lo devuelve en segundos, yo lo convierto en horas (dividiendo por los 3600 segundos que hay en 1 hora)
            instructors[instructor_name].append((close_time - open_time).total_seconds() / 3600)

        avg_instructor_grade_time = {}
        max_instructor_grade_time = {}
        min_instructor_grade_time = {}
        for instructor in instructors.keys():
            avg_instructor_grade_time[instructor] = np.mean(instructors[instructor])
            max_instructor_grade_time[instructor] = max(instructors[instructor])
            min_instructor_grade_time[instructor] = min(instructors[instructor])
        
        result["avg_instructor_grade_time_in_h"] = avg_instructor_grade_time
        result["max_instructor_grade_time_in_h"] = max_instructor_grade_time
        result["min_instructor_grade_time_in_h"] = min_instructor_grade_time

        # Para terminar devuelvo el resultado con toda la información que he obtenido del lab
        return(result)

    except InvalidId:
        return f"La id '{lab_id}' no es válida."    


@app.route("/lab/memeranking")
def meme_ranking():
    '''
    receives: no params.
    returns: more used memes for datamad0820 divided by lab.
    '''
    return f"[TO-DO] Return all memes grouped by lab."


@app.route("/lab/<lab_id>/meme")
def get_random_meme(lab_id):
    '''
    receives: a lab name
    returns: a random meme from the ones used for each student pull request.
    '''
    return f"[TO-DO] Return a random meme from the lab '{lab_id}' pull requests."
