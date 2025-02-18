'''Defines a class for threat classification.
This class impelemnts some methods for cleaning of the inputs and uses trained classifiers for prediction.'''

import json
import urllib.parse

import joblib
from .request import Request

class ThreatClassifier(object):
    def __init__(self):
        self.clf = joblib.load(r"website/ML-models/final_model_pred.pkl")     
        self.pt_clf = joblib.load(r"website/ML-models/pt_final_model.pkl")

    def __unquote(self, text):
        k = 0
        uq_prev = text
        while(k < 100):
            uq = urllib.parse.unquote_plus(uq_prev)
            if uq == uq_prev:
                break
            else:
                uq_prev = uq
    
        return uq_prev

    def __remove_new_line(self, text):
        text = text.strip()
        return ' '.join(text.splitlines())

    def __remove_multiple_whitespaces(self, text):
        return ' '.join(text.split())

    def __clean_pattern(self, pattern):
        pattern = self.__unquote(pattern)
        pattern = self.__remove_new_line(pattern)
        pattern = pattern.lower()
        pattern = self.__remove_multiple_whitespaces(pattern)

        return pattern

    def __is_valid(self, parameter):
        return parameter != None and parameter != ''

    def classify_request(self, req):
        if not isinstance(req, Request):
            raise TypeError("Object should be a Request!!!")

        parameters = []
        locations = []

        if self.__is_valid(req.request):
            parameters.append(self.__clean_pattern(req.request))
            locations.append('Request')
        for i in req.body:
            if self.__is_valid(i):
                parameters.append(self.__clean_pattern(i))
                locations.append('Body')

        if 'Cookie' in req.headers and self.__is_valid(req.headers['Cookie']):
            parameters.append(self.__clean_pattern(req.headers['Cookie']))
            locations.append('Cookie')

        if 'User-Agent' in req.headers and self.__is_valid(req.headers['User-Agent']):
            parameters.append(self.__clean_pattern(req.headers['User-Agent']))
            locations.append('User Agent')

        if 'Accept-Encoding' in req.headers and self.__is_valid(req.headers['Accept-Encoding']):
            parameters.append(self.__clean_pattern(req.headers['Accept-Encoding']))
            locations.append('Accept Encoding')

        if 'Accept-Language' in req.headers and self.__is_valid(req.headers['Accept-Language']):
            parameters.append(self.__clean_pattern(req.headers['Accept-Language']))
            locations.append('Accept Language')

        #print(parameters)

        req.threats = {}

        if len(parameters) != 0:
            predictions = self.clf.predict(parameters)

            for idx, pred in enumerate(predictions):
                if pred != 'valid':
                    req.threats[pred] = locations[idx]

        request_parameters = {}
        if self.__is_valid(req.request):
            request_parameters = urllib.parse.parse_qs(self.__clean_pattern(req.request))

        body_parameters = {}
        for i in req.body:
            if self.__is_valid(i):
                body_parameters = urllib.parse.parse_qs(self.__clean_pattern(str(i)))

            if len(body_parameters) == 0:
                ###Check if it is JSON data
                try:
                    body_parameters = json.loads(self.__clean_pattern(str(i)))
                except:
                    pass

        print('bpdy bar is ' , body_parameters)

        parameters = []
        locations = []

        for name, value in request_parameters.items():
            for elem in value:
                parameters.append([len(elem)])
                locations.append('Request')
        if body_parameters is int:
            body_parameters=str(body_parameters)

            for name, value in body_parameters.items():
                ###Output of the form parse is a list so we need to iterate, and JSON returns only one element so no need to iterate
                if isinstance(value, list):
                    for elem in value:
                        parameters.append([len(elem)])
                        locations.append('Body')
                else:
                    parameters.append([len(value)])
                    locations.append('Body')

        if len(parameters) != 0:
            pt_predictions = self.pt_clf.predict(parameters)

            for idx, pred in enumerate(pt_predictions):
                if pred != 'valid':
                    req.threats[pred] = locations[idx]

        if len(req.threats) == 0:
            req.threats['valid'] = ''

