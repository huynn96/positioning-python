from flask import Flask, request
from datetime import datetime
import time
import MySQLdb
import json
import math
from scipy import integrate, constants
from scipy.signal import butter, lfilter
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
    def calDirOff():
        a, ats, d, dts, stepParamsA, stepParamsB = parseData(json.loads(request.data))
        vecs = extract_feture(a, ats)
        result = loaded_model.predict(vecs)
        distanceCount = 0
        directionCal = 0
        peaks = []
        if 1 in result:
            peaks = stepCounting(a, ats)
            distanceCount = distance(peaks, ats, stepParamsA, stepParamsB)
            directionCal = direction(d, dts, peaks, ats)
        steps = 0 if len(peaks) == 0 else len(peaks) - 1;
        print(steps)
        return pd.Series([steps, distanceCount, directionCal]).to_json(orient='values')

    def direction(d, dts, peaks, ats):
        result = d[0]
        a = 3/3.08
        if len(peaks) > 2:
            a = 1 / ((ats[peaks[2]] - ats[peaks[1]]) * 3.08)

        for direction in d:
            result = (1-a) * direction + a * result
        return result

    def stepCounting(a, ats): 
        g = constants.value(u'standard acceleration of gravity')
        a = [x- g for x in a]
        accFiltered = butter_bandpass_filter(a, 1, 3, 50, order=6)

        windowSize = 16
        peaks = []
        for i in range(0, len(accFiltered) - 2, 1):
            window = accFiltered[i:i+windowSize]
            median = len(window)//2
            if window[median] == np.max(window) and np.std(window) > 0.1:
                if len(peaks) == 0:
                    # print(i + median)
                    # print(np.std(window))
                    peaks.append(i + median)
                else:
                    if ats[i + median] - ats[peaks[len(peaks) - 1]] >= 0.33:
                        # print(i + median)
                        # print(np.std(window))
                        peaks.append(i + median)   
        # print(peaks)

        plt.plot(ats, a, '.-')
        plt.plot(ats, accFiltered, linestyle='dashed', color='red')
        plt.xlabel('time (s)')
        plt.ylabel('acceleration (m/s^2)')
        # plt.show()
        return peaks

    def stepLength(peak1, peak2, ats, stepParamsA, stepParamsB):
        frequence = 1 / (ats[peak2] - ats[peak1])
        return stepParamsA + stepParamsB * frequence

    def distance(peaks, ats, stepParamsA, stepParamsB):
        result = 0
        for i in range(1, len(peaks) - 1, 1):
            result += stepLength(peaks[i - 1], peaks[i], ats, stepParamsA, stepParamsB)
        return result

    def parseData(requestData):
        a = []
        ats = []
        d = []
        dts = []
        for row in requestData['accelerations']:
            a.append(math.sqrt(row['x'] * row['x'] + row['y'] * row['y'] + row['z'] * row['z']))
            ats.append(row['createdAt'])
        for row in requestData['directions']:
            d.append(row['direction'])
            dts.append(row['createdAt'])
        ats =  [x/1000000000. for x in ats]
        ats = [x - ats[0] for x in ats]
        dts =  [x/1000000000. for x in dts]
        dts = [x - ats[0] for x in dts]
        return a, ats, d, dts, requestData['stepParamsA'], requestData['stepParamsB']

    def extract_feture(a, ats):
        windowSize = 45
        vecs = []
        # print(len(a))
        for i in range(0, len(a) - windowSize, windowSize / 2):
            window = a[i:i+windowSize]
            vecs.append([np.std(window)])
            # print(integrate.simps([1,1,1,1], [1, 1.5, 2, 2.5]))
        return vecs

    def butter_bandpass(lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a


    def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
        b, a = butter_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y

    return app
