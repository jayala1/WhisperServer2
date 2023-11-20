# WhisperServer2
Ensure you have python 3.11 installed

Download and extract

open cmd and ensure you are in root of the extracted folder

Run python -m venv .env to create virtual enviroment folder

run the following: .env\Scripts\activate to activate it.

This will create a virtual enviroment for the python code to run you should see (env) in the CMD now. If not, python is not an enviroment path in your system settings

run the pip install -r requirements.txt This will install all the required packages for the virtual env to run

after that, run python init_db.py to initialize the db and create it.

Then run python run.py This might take a while to start up fully to get all the models loaded or downloaded

Then go to address 127.0.0.1:5000/register Add an account

Then go to address 127.0.0.1:5000/login to login to account

Limited error handling
