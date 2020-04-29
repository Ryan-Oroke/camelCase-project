# camelCase-project
### Organization and Structure
##### Templates
Where the HTML files with neccicary JavaScript are kept to be populated by the Flask server. 
##### Static
Where images and CSS files are kept. This is for pathing for Flask. This is also where uploads go for server-side linking. 
##### server.py
The server code that dictates what gets rendered where, and calls functions that query the Mongo database.
##### mongoIO.py
Contains the diffrent DB query functions, as well as other Mongo DB handlers.

## Overview for Setup
### Build Codebase
##### Libraries
Requires Flask
Requires PyMongo
Requires haversine
##### Database
Requires MongoDB

### To Run
Run server.py and connect to localhost:5000

### To Test
Run the mongoIO.py file. 


## In-depth Setup
We are using flask and mongo.
### Flask Install
We're using PyCharm but you are free to use any other IDE.

##### PyCharm
To set up the interpreter you will need to go to `File > Settings...` and then go to `Project: camelCase-project > Project Interpreter` or `Project: flask-server > Project Interpreter` depending on what folder you opened. From here go to the setting button and add a new environment (we are using python 3).

You will need to install Flask, pymongo, and haversine. In the `Project Interpreter` part click the add button and search for these and click install.

Now when you run you should see flask starting up. Just go to:
```
http://localhost:5000/
```

##### Linux
For Linux, you can create a virtualEnv or add all libraries globally by doing the following.
First, you will need to run.
```
pip3 install flask
pip3 install pymongo
pip3 install haversine
```
And then run the following in the `flask-server` directory to run the program.
```
python3 server.py
```

Now when you run you should see flask starting up. Just go to:
```
http://localhost:5000/
```

### Mongo
Install mongo here: [https://docs.mongodb.com/manual/administration/install-community/](https://docs.mongodb.com/manual/administration/install-community/)

Make sure you also install the python driver. It is called `pymongo`. You can get it the same way you got flask.
