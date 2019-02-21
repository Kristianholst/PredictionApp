from flask import Flask, jsonify, make_response, send_from_directory,request
from flask_pymongo import PyMongo
import json
from bson import ObjectId
from flask import Response
from collections import defaultdict
from transformdict import transformdict, transformdictreversed
from joblib import dump, load
import requests 
from validationschema import schema
import jsonschema
import os
import os.path
import sys
from datetime import datetime
from functools import wraps, update_wrapper
from flask_cors import CORS


app = Flask(__name__)
CORS(app) #allow crossdomain

app.config['MONGO_DBNAME'] = 'test'
app.config['MONGO_URI'] = os.environ['MONGODB_URI'] 
mongo = PyMongo(app)


@app.route('/', methods=['GET'])
def index():
    return "Find documentation on API on https://github.com/Kristianholst/PredictionApp"



@app.route('/find', methods=['PUT'])
def getonedict():
    data=request.data
    dataDict = json.loads(data)
    
    idtofind=dataDict['pid']
    user =mongo.db.income.find_one( { 'pid': idtofind }, {  '_id': 0 } ) 

    #not found
    if user:
        result=jsonify(user)
        return result
        
    else:
        print('None found')
        return Response('ID not found', status=404)      

@app.route('/predict', methods=['PUT'])
def predict():
    data=request.data
    
    ##first of all validate input from user:
    
    try:
        jsonschema.validate(json.loads(data), schema)
        
    except jsonschema.exceptions.ValidationError as e:
        return("Error in input validation. Please check input"+str(e))

    ##making request data to jason dict
    userdata = json.loads(data)

    #fetching database data
    idtofind=userdata['pid']
    dbdata =mongo.db.income.find_one( { 'pid': idtofind }, {  '_id': 0  } ) 
    
    #return if no user found
    if not dbdata:
        return Response('ID not found', status=404)  

    ##make dict to feed prediction. Combines both internal and user
    #supplied data. Made this way to effectively keep track of variable order
    ##and too make categorical transform to feed prediction model

    collist=['age','workclass','education','educational-num','marital-status','occupation','relationship','race','gender',
        'capital-gain','capital-loss','hours-per-week','native-country']
    
    preddict={}
    
    #making dict with 0 values
    for col in collist:
        preddict[col]=0

    #populating dict

    for col in preddict:
        if col in dbdata:
            preddict[col]=dbdata[col]
        elif col in userdata:
            preddict[col]=userdata[col]

    ##import transformdict
    catnames=['workclass','education','marital-status','occupation','relationship','race','gender','native-country'] 
    for name in catnames:
        preddict[name]=transformdict[name][preddict[name]]

    ##prediction model

    model = load('model.joblib')

    #return probabilites from model

    predictionvalue=model.predict_proba([list(preddict.values())])
    preddict['Prediction']=predictionvalue[0][1]

    #transform predictiondict to more readable form
    for name in catnames:
        preddict[name]=transformdictreversed[name][preddict[name]]

    ##bonus provide request with additional third party data

    extdata=requests.get("https://jsonplaceholder.typicode.com/users/"+ str(idtofind))
    jsonrespons=extdata.json()

    #handle if not found in external database

    try:
        preddict['address']=jsonrespons['address']
    except:
        preddict['address']=extdata.reason

 
    return jsonify(preddict)

# We use this to prevent caching of `/api-docs.yml`
# Credits: https://arusahni.net/blog/2014/03/flask-nocache.html
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Last-Modified"] = datetime.now()
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        return response
    return update_wrapper(no_cache, view)

SWAGGER_UI_DIST_DIR = "swagger-ui-dist"

@app.route("/swagger-ui/")
def swagger_ui():
    print("rew")
    return send_from_directory(SWAGGER_UI_DIST_DIR, "index.html")

@app.route("/swagger-ui/<asset>")
def swagger_assets(asset):
    print(asset)
    return send_from_directory(SWAGGER_UI_DIST_DIR, asset)

@app.route("/api-docs.yml")
@nocache
def swagger_api_docs_yml():
    print("API:3")
    return send_from_directory(".", "api-docs.yml")

if __name__ == '__main__':
    app.run(debug=True)