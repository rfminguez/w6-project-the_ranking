import requests
from src.database import db
import os
from dotenv import load_dotenv
import re


def get_auth_header():
    load_dotenv()
    api_key = os.getenv("GITHUB_APIKEY")
    return {"Authorization": f"Bearer {api_key}"}


def call_api(api_url, query_params={"page":1, "per_page":100, "state": "all"}):
    res = requests.get(api_url, params=query_params, headers=get_auth_header())
    
    print(f"Request url with params: {res.url}")
    print(f"HTTP Status Code: {res}")
    data = res.json()
    return data


def get_pull_requests_url(owner = "ironhack-datalabs", repo = "datamad0820"):
    base_url = "https://api.github.com"
    endpoint = f"/repos/{owner}/{repo}/pulls"
    url = f"{base_url}{endpoint}"

    print(f"Request data to {url}")
    return url


def get_pull_requests(api_url):
    page_num = 1
    data = []

    # Recorro todas las entradas
    while True:
        new_bucket = call_api(api_url, query_params={"page":page_num, "per_page":100, "state": "all"})
        
        # Si el nuevo bucket está vacío salgo del bucle
        if len(new_bucket) == 0:
            break

        page_num += 1
        data += new_bucket
    
    return data


def get_commit_dates(api_url):
    data = call_api(api_url, query_params={})
    return [commit["commit"]["author"]["date"] for commit in data]


def get_comments(api_url):
    data = call_api(api_url, query_params={})
    return [{"author": comment["user"]["login"], "body": comment["body"]} for comment in data]


def get_students_from_body(pull_request_body):
    # Busco el patrón @usuario dentro del body del pull request
    result = re.findall(r"\@[\w\-]+", pull_request_body)

    # Quito las @ del principio
    return map(lambda s: s.replace("@", ""), result)


def get_students_from_comments(list_of_comments):
    result = []
    for comment in list_of_comments:
        if re.match(r"^join$", comment["body"]):
            result.append(comment["author"])
    return result


def get_list_of_students(pull_request):
    # Primero inserto el usuario que abrió la pull request
    list_of_students = [pull_request["user"]]

    # Luego busco los alumnos que aparecen referenciados en el body
    for student in get_students_from_body(pull_request["body"]):
        if student not in list_of_students:
            list_of_students.append(student)

    # Y por último busco los que aparecen en los comments
    for student in get_students_from_comments(pull_request["comments"]):
        if student not in list_of_students:
            list_of_students.append(student)

    return list_of_students


def get_lab_name(title):
    # Busco el lombre del lab encerrado entre "[" y "]"
    lab_name = re.search(r"\[(.*)\]", title)
    if lab_name:
        return lab_name.group(1)
    return None


def get_meme_images(pull_request_body):
    '''
    receives:   the body of a pull request.
    purpose:    look for images enbedded inside the body of the pull request (image format ".jpg", ".jpeg" and ".png").
    returns:    the images that there are inside the body.
    '''
    # busco el patrón https://<nombre_imagen>.<formato> con una regex
    regex_result = re.search(r"(https://.*\.(jpg|png|jpeg))", pull_request_body)
    result = []
    if regex_result is not None:
        result.append(regex_result.group(0))
    return result


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
            "user": pull_request["user"]["login"],
            "asignees": [asignee["login"] for asignee in pull_request["assignees"]], # Profes que revisan el lab
            "body": pull_request["body"],
            "created_at": pull_request["created_at"],
            "updated_at": pull_request["updated_at"],
            "base_pushed_at": pull_request["base"]["repo"]["pushed_at"],
            "closed_at": pull_request["closed_at"],
            "comments": get_comments(pull_request["_links"]["comments"]["href"]),
            "commit_dates": get_commit_dates(pull_request["commits_url"]),
            "memes": get_meme_images(pull_request["body"])
        }

        # Una vez tengo la pull_request con los datos de comentarios que me he traído con otra llamada a la api:
        # - busco los estudiantes adicionales que pueden estar asociados a la pull request
        list_of_students = get_list_of_students(new_pull_request)
        new_pull_request["students"] = list_of_students

        # Guardo en mongodb
        collection.insert_one(new_pull_request)


def main():
    dump_to_database(db.pull_requests, get_pull_requests(get_pull_requests_url()))
    print("Datos de las pull requests guardados")


if __name__ == "__main__":
    main()
