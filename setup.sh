

#!/bin/bash


python3 -m venv venv


source venv/bin/activate


pip install --upgrade pip


pip install -r requirements.txt  


export FLASK_APP=main.py
export FLASK_ENV=development  


flask run


deactivate
