from src.app import app
from src.config import PORT
import src.controllers.labs_controllers
import src.controllers.students_controllers 

app.run("0.0.0.0", PORT, debug=True)

