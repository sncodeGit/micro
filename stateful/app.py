import random
import sqlalchemy as sa
import numpy
import os
import pandas as pd
#
from flask import Flask, request
from sqlalchemy import create_engine, MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, update
from sqlalchemy.orm import sessionmaker
from flask_restful import Api, Resource, reqparse
from datetime import datetime

def stop_game(id, res_1, res_2):
    df = pd.DataFrame()
    if not os.path.exists(str(id)+'.csv'):
        df = pd.DataFrame({'sum': [0, 0]})
    else:
        df = pd.read_csv(str(id)+'.csv')
    df.iloc[0, 0] = df.iloc[0, 0] + res_1
    df.iloc[1, 0] = df.iloc[1, 0] + res_2
    print(df)
    df.to_csv(str(id)+'.csv', index=False)
    return 'OK'
        
def get_stats(id):
    df = pd.DataFrame()
    if not os.path.exists(str(id)+'.csv'):
        return 'No stats right now'
    else:
        df = pd.read_csv(str(id)+'.csv')
    return {'1': str(int(df.iloc[0, 0])), '2': str(int(df.iloc[1, 0]))}
    

########################

app = Flask(__name__)
api = Api(app)

class StopGame(Resource):
    def get(self, id=0, res_1=0, res_2=0):
        id = int(request.args.get('id'))
        res_1 = int(request.args.get('res_1'))
        res_2 = int(request.args.get('res_2'))
        ans = stop_game(id, res_1, res_2)
        return ans, 200
    
class GetStats(Resource):
    def get(self, id=0):
        id = int(request.args.get('id'))
        ans = get_stats(id)
        return ans, 200

api.add_resource(StopGame, "/api/v1/stats/stop", "/api/v1/stats/stop/")
api.add_resource(GetStats, "/api/v1/stats/get", "/api/v1/stats/get/", "/api/v1/stats/get/<int:id>")

if __name__ == '__main__':
    app.run()
