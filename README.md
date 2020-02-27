# camelCase-project
info info info

## How to set up for development
### Flask part
I'm using PyCharm but you can use what you want.

##### PyCharm
To set up the interpreter you will need to go to `File > Settings...` and then go to `Project: camelCase-project > Project Interpreter` or `Project: flask-server > Project Interpreter` depending on what folder you opened. From here go to the setting button and add a new environment (we are using python 3).

You will need to install Flask. In the `Project Interpreter` part click the add button and search for Flask and click install.

To run you can use PyCharm.

##### Linux
For Linux, you can create a virtualEnv or just do everything globally like the following.
First, you will need to run.
```
pip3 install flask
```
And then run the following in the `flask-server` directory to run the program.
```
python3 server.py
```

### React part
install react
```
npm install react
npm install create-react-app
```

To install dependencies you will need to run the following in the `react-app` directory.
```
npm install
```

To build type the following in the `react-app` directory.
```
npm run build
```
