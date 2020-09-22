from src.app import app
from flask import request
from src.database import db


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
    receives: a lab name via POST method.
    purpose: create a new document in the labs collection.
    returns: _id of the lab once inserted in the DB.
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
    return f"[TO-DO] Search a lab ({lab_id}) and analyze it according to instructions."

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
