import requests
from src.database import db
import os
from dotenv import load_dotenv
import re


def get_url(endpoint):
    base_url = "https://api.github.com"
    url = f"{base_url}{endpoint}"

    print(f"Request data to {url}")
    return url


def get_auth_header():
    load_dotenv()
    api_key = os.getenv("GITHUB_APIKEY")
    return {"Authorization": f"Bearer {api_key}"}


def get_pull_requests(endpoint, query_params={"page":1, "per_page":100, "state": "all"}):
    res = requests.get(get_url(endpoint), params=query_params, headers=get_auth_header())
    
    print(f"Request url with params: {res.url}")
    print(f"HTTP Status Code: {res}")
    data = res.json()
    return data


def get_endpoint(owner = "ironhack-datalabs", repo = "datamad0820"):
    return f"/repos/{owner}/{repo}/pulls"


def get_data(endpoint):
    page_num = 1
    data = []

    # Recorro todos los pull requests
    while True:
        new_bucket = get_pull_requests(endpoint, query_params={"page":page_num, "per_page":100, "state": "all"})
        
        # Si el nuevo bucket está vacío salgo del bucle
        if len(new_bucket) == 0:
            break

        page_num += 1
        data += new_bucket
    
    return data


def get_students_from_body(pull_request_body):
    # Busco el patrón @usuario dentro del body del pull request
    result = re.findall(r"\@\w+", pull_request_body)

    # Quito las @ del principio
    return map(lambda s: s.replace("@", ""), result)


def get_list_of_students(pull_request):
    # Primero inserto el usuario asociado a la pull request
    list_of_students = [pull_request["user"]["login"]]
    # Luego busco los alumnos que aparecen referenciados en el body
    for student in get_students_from_body(pull_request["body"]):
        if student not in list_of_students:
            list_of_students.append(student)
    return list_of_students


def get_lab_name(title):
    # Busco el lombre del lab encerrado entre "[" y "]"
    lab_name = re.search(r"\[(.*)\]", title)
    if lab_name:
        return lab_name.group(1)
    return None
    

def dump_to_database(collection, data):
    '''
    receives two arguments:   
        - a link to a mongodb collection.
        - the api data of all pull requests (a huge list of JSON documents).

    purpose:    
        save a subset of each pull request data in a mongodb collection.
    '''
    print(f"Total de documentos a insertar: {len(data)}")

    # Inserto estos datos de cada pull request en la base de datos.
    for pull_request in data:
        new_pull_request = {
            "id": pull_request["id"],
            "lab_name": get_lab_name(pull_request["title"]),
            "state": pull_request["state"],
            "locked": pull_request["locked"],
            "title": pull_request["title"],
            "students": get_list_of_students(pull_request),
            "asignees": [asignee["login"] for asignee in pull_request["assignees"]], # Profes que revisan el lab
            "body": pull_request["body"],
            "created_at": pull_request["created_at"],
            "updated_at": pull_request["updated_at"],
            "base_pushed_at": pull_request["base"]["repo"]["pushed_at"],  # Ej. "pushed_at": "2020-09-18T10:34:21Z" "2020-09-21T16:45:53Z"
            "closed_at": pull_request["closed_at"],
            "comments": pull_request["_links"]["comments"]["href"],
            "review_comments": pull_request["_links"]["review_comments"]["href"],
            "memes": [] # [TO-DO] Buscar memes y guardarlos aquí.
        }

        collection.insert_one(new_pull_request)


def main():
    dump_to_database(db.pull_requests, get_data(get_endpoint()))
    print("Datos de las pull requests guardados")


if __name__ == "__main__":
    main()
