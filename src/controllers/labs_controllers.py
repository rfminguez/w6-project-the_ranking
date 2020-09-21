from src.app import app
from flask import request
from src.database import db

@app.route("/lab/create")
def create_lab():
    '''
    POST method
    receives: a string with the lab-prefix to analyze (i.e. [lab-scavengers]).
    purpose: create a new entry in the labs database.
    returns: lab_id
    '''
    return f"[TO-DO] Receive a lab via POST method and save it into DB."

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
