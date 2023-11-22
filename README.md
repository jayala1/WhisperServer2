# WhisperServer2

# Description
AI generated code using GPT-4 for a web server with login page. Upload your audio. Get it transcribed by Distil-Whisper, and the get it summarized by LMstudio inference server python bindings to an open source LLM.


# Instructions Work in progress.

Ensure you have python 3.11 installed

Ensure FFMPEG is also installed. https://ffmpeg.org/download.html

Download LMStudio, select your model, go to the server section and start the inference server. Ensure you update the routes.py with the IP address of the computer that is running the LMstudio inference server

Also ensure you open the port for UDP and TCP(just in case) to that machine for whatever port you are using for the lmstudio inference server.

Download and extract

open cmd and ensure you are in root of the extracted folder

Run python -m venv .env to create virtual enviroment folder

run the following: .env\Scripts\activate to activate it.

This will create a virtual enviroment for the python code to run you should see (env) in the CMD now. If not, python is not an enviroment path in your system settings

run the pip install -r requirements.txt This will install all the required packages for the virtual env to run

after that, run python init_db.py to initialize the db and create it. This will also download the models for whisper and summarization.

Then run python run.py This might take a while to start up fully to get all the models loaded or downloaded

Then go to address 127.0.0.1:5000/register Add an account

Then go to address 127.0.0.1:5000/login to login to account

# Changes needed

- Better error handling

- Queuing up jobs for transcribing if being used by more than one person.

- Checking preformance




