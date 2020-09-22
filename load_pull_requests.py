import requests
from src.database import db
import os
from dotenv import load_dotenv


def setup_url(endpoint):
    base_url = "https://api.github.com"
    url = f"{base_url}{endpoint}"

    print(f"Request data to {url}")
    return url


def setup_auth_header():
    load_dotenv()
    api_key = os.getenv("GITHUB_APIKEY")
    return {"Authorization": f"Bearer {api_key}"}


def get_pull_requests(endpoint, query_params={"page":1, "per_page":100, "state": "all"}):
    res = requests.get(setup_url(endpoint), params=query_params, headers=setup_auth_header())
    
    print(f"Request url with params: {res.url}")
    print(f"HTTP Status Code: {res}")
    data = res.json()
    return data


def setup_endpoint(owner = "ironhack-datalabs", repo = "datamad0820"):
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


def dump_to_database(collection, data):
    print(f"Total de documentos a insertar: {len(data)}")

    # Inserto cada pull request en la base de datos.
    for pull_request in data:
        new_pull_request = {
            "id": pull_request["id"],
            "state": pull_request["state"],
            "locked": pull_request["locked"],
            "title": pull_request["title"],
            "users": [pull_request["user"]["login"]], # [TO-DO] Aquí hay que añadir los usuarios adicionales en caso de lab por parejas.
            "asignees": [asignee["login"] for asignee in pull_request["assignees"]], # Profes que revisan el lab
            "body": pull_request["body"],
            "created_at": pull_request["created_at"],
            "updated_at": pull_request["updated_at"],
            "closed_at": pull_request["closed_at"],
            "comments": pull_request["_links"]["comments"]["href"],
            "review_comments": pull_request["_links"]["review_comments"]["href"],
            "memes": [] # [TO-DO] Buscar memes y guardarlos aquí.

        }

        collection.insert_one(new_pull_request)


def main():
    dump_to_database(db.pull_requests, get_data(setup_endpoint()))
    print("Datos de las pull requests guardados")


if __name__ == "__main__":
    main()
