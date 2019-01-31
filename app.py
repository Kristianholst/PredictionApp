from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import json
from bson import ObjectId
from flask import Response
from collections import defaultdict
from transformdict import transformdict, transformdictreversed
from joblib import dump, load
import requests 





app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'test'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'

mongo = PyMongo(app)



@app.route('/find', methods=['GET'])
def getonedict():
    data=request.data
    dataDict = json.loads(data)
    
    idtofind=dataDict['pid']
    ##implement not found

    
    user =mongo.db.income.find_one( { 'pid': idtofind }, {  '_id': 0 } ) 
    print(type(user))
    #not found
    if user:
        result=jsonify(user)
        return result
        
    else:
        print('None found')
        return Response('ID not found', status=404)      

@app.route('/predict', methods=['GET'])
def predict():
    data=request.data
    userdata = json.loads(data)
    
    #fetching own self reported data/not necessary
    idtofind=userdata['pid']
    
    #fetching database data
    dbdata =mongo.db.income.find_one( { 'pid': idtofind }, {  '_id': 0  } ) 
    
    #return if no user found
    if not dbdata:
        print('None')
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

    
    
    ##import model

    model = load('model.joblib')

    predictionvalue=model.predict_proba([list(preddict.values())])
    preddict['Prediction']=predictionvalue[0][1]

    #transform predictiondict to more readable form
    for name in catnames:
        preddict[name]=transformdictreversed[name][preddict[name]]

    ##bonus provide request with additional third party data

    extdata=requests.get("https://jsonplaceholder.typicode.com/users/"+ str(idtofind))
    jsonrespons=extdata.json()

    try:
        preddict['address']=jsonrespons['address']
    except:
        preddict['address']=extdata.reason




    return jsonify(preddict)



    ##implement not found



if __name__ == '__main__':
    app.run(debug=True)