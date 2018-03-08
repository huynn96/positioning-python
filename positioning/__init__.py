from flask import Flask, request
from datetime import datetime
import time
import MySQLdb
import json
import math
from scipy import integrate
import numpy as np
from sklearn.externals import joblib
from flask import jsonify
import pandas as pd
import matplotlib.pyplot as plt

# local imports
from config import app_config


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db = MySQLdb.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        passwd=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DATABASE']
    )
    loaded_model = joblib.load('positioning/acceleration/model_svm.sav')

    @app.route('/cal-do', methods=['POST'])
    def hello_world():
        vecs = extract_feture(json.loads(request.data))
        result = loaded_model.predict(vecs)
        print(result)
        
        return pd.Series(result).to_json(orient='values')

    def extract_feture(accelerationData):
        a = []
        ats = []
        for row in accelerationData:
            a.append(math.sqrt(row['x'] * row['x'] + row['y'] * row['y'] + row['z'] * row['z']))
            ats.append(row['createdAt'])

        windowSize = 200
        vecs = []

        ats =  [x/1000000000. for x in ats]
        ats = [x - ats[0] for x in ats]
        print(ats)
        for i in range(0, len(a) - windowSize, windowSize / 2):
            window = a[i:i+windowSize]
            # plt.plot(ats[i:i+windowSize], window, '.-')
            vecs.append([np.median(window), np.mean(window), np.min(window), np.max(window), np.std(window)])
            print(integrate.simps(window, ats[i:i+windowSize]))
            # plt.show()
        return vecs

    return app
