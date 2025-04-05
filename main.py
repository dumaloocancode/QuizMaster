from QuizCraft import create_app, create_database
from QuizCraft.models import *
import os

# ------- SETTING UP THE APP --------
app = create_app()
create_database(app)

# ----- IMPORT ALL THE CONTROLLERS ------
from QuizCraft.controllers import *

if __name__ == '__main__':
    app.run(debug = True)