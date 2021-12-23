import random
import sqlalchemy as sa
import numpy
import requests
#
from flask import Flask, request
from sqlalchemy import create_engine, MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, update
from sqlalchemy.orm import sessionmaker
from flask_restful import Api, Resource, reqparse
from datetime import datetime


def get_comp_hist(a):
    ac = list(numpy.random.normal(loc = 0.0, scale = 1.0, size = 21))
    for i in range(len(ac)):
        ac[i] = int(ac[i])
    for i in range(len(ac)):
        a = a + ac[i] / 100 * a
        ac[i] = str(int(a))
    return ac

def update_in_service(session, table, id, **vals):
    stmt = (
        update(table).where(table.c.id==str(id)).
        values(**vals)
    )
    session.execute(stmt) 
    session.commit()

def insert_in_table(session, table, **vals):
    insert_stmnt = table.insert().values(**vals)
    session.execute(insert_stmnt) 
    session.commit()

def initial_game(id, gamers):
    engine = create_engine("mysql+pymysql://%s:%s@%s:3306/%s" % (USER, PASS, HOST, DB_NAME))
    metadata = MetaData()
    metadata.reflect(engine)
    if (str(id) + '_companies' in metadata.tables.keys()) and (str(id) + '_gamers' in metadata.tables.keys()) and (str(id) + '_game' in metadata.tables.keys()):
        return "Игра уже идет"
    companies = Table(str(id)+'_companies', metadata, 
        Column('id', Integer(), primary_key=True),
        Column('story', String(200), nullable=False),
        Column('act_num', Integer(), nullable=False),
        Column('act_purchase', Integer(), nullable=False),
        Column('act_sale', Integer(), nullable=False)
    )
    gamers = Table(str(id)+'_gamers', metadata, 
        Column('id', Integer(), primary_key=True),
        Column('balance', Integer(), nullable=False),
        Column('sum_balance', Integer(), nullable=False),
        Column('company_1', Integer(), nullable=False),
        Column('company_2', Integer(), nullable=False),
        Column('company_3', Integer(), nullable=False),
        Column('company_4', Integer(), nullable=False),
        Column('company_5', Integer(), nullable=False)
    )
    companies.create(engine)
    gamers.create(engine)
    #
    Session = sessionmaker(bind = engine)
    session = Session()
    for i in COMPANIES:
        story = get_comp_hist(100)
        act_sale = story[-1]
        act_purchase = story[-2]
        story = ' '.join(story[:-2])
        insert_in_table(session, companies, id=i, story=story, act_num=100, act_purchase=act_purchase, act_sale=act_sale)
    for i in GAMERS:
        insert_in_table(session, gamers, id=i, balance=10000, sum_balance=10000, company_1=0, company_2=0, company_3=0, company_4=0, company_5=0)
    return "Игра началась"

def buy(gameId, companyId, gamerId, count):
    engine = create_engine("mysql+pymysql://%s:%s@%s:3306/%s" % (USER, PASS, HOST, DB_NAME))
    metadata = MetaData()
    metadata.reflect(engine)
    gamers = Table(str(gameId)+'_gamers', metadata, autoload_with=engine)
    companies = Table(str(gameId)+'_companies', metadata, autoload_with=engine)
    Session = sessionmaker(bind = engine)
    session = Session()
    comp = session.query(companies).all()[companyId-1]
    s = comp[3]
    comp_resid = comp[2] - count
    gamer = session.query(gamers).all()[gamerId-1]
    gamer_resid = gamer[1] - count * s
    gamer_comp = companyId + 2
    update_in_service(session, companies, companyId, act_num=comp_resid)
    if companyId == 1:
        res_gamer_comp = gamer[gamer_comp] + count
        update_in_service(session, gamers, gamerId, balance=gamer_resid, company_1=res_gamer_comp)
    if companyId == 2:
        res_gamer_comp = gamer[gamer_comp] + count
        update_in_service(session, gamers, gamerId, balance=gamer_resid, company_2=res_gamer_comp)
    if companyId == 3:
        res_gamer_comp = gamer[gamer_comp] + count
        update_in_service(session, gamers, gamerId, balance=gamer_resid, company_3=res_gamer_comp)
    if companyId == 4:
        res_gamer_comp = gamer[gamer_comp] + count
        update_in_service(session, gamers, gamerId, balance=gamer_resid, company_4=res_gamer_comp)
    if companyId == 5:
        res_gamer_comp = gamer[gamer_comp] + count
        update_in_service(session, gamers, gamerId, balance=gamer_resid, company_5=res_gamer_comp)
    return "Success"

def stop_game(id):
    engine = create_engine("mysql+pymysql://%s:%s@%s:3306/%s" % (USER, PASS, HOST, DB_NAME))
    metadata = MetaData()
    metadata.reflect(engine)
    companies = Table(str(id)+'_companies', metadata, autoload_with=engine)
    gamers = Table(str(id)+'_gamers', metadata, autoload_with=engine)
    Session = sessionmaker(bind = engine)
    session = Session()
    counter = 1
    prices = [0, 0, 0, 0, 0]
    gamers_list = session.query(gamers).all()
    companies_list = session.query(companies).all()
    ress = [0, 0]
    for gamer in gamers_list:
        res = gamer[1]
        comp = companies_list[0]
        prices[0] = comp[4]
        res = res + comp[4] * gamer[3]
        comp = companies_list[1]
        prices[1] = comp[4]
        res = res + comp[4] * gamer[4]
        comp = companies_list[2]
        prices[2] = comp[4]
        res = res + comp[4] * gamer[5]
        comp = companies_list[3]
        prices[3] = comp[4]
        res = res + comp[4] * gamer[6]
        comp = companies_list[4]
        prices[4] = comp[4]
        res = res + comp[4] * gamer[7]
        update_in_service(session, gamers, counter, balance=res, company_1=0, company_2=0, company_3=0, company_4=0, company_5=0)
        ress[counter-1] = res
        counter = counter + 1
    #
    requests.get('http://stateful:5001/api/v1/stats/stop?id=%s&res_1=%sres_2=%s' % (id, ress[0], ress[1]))
    #
    return {"1": prices[0], "2": prices[1], "3": prices[2], "4": prices[3], "5": prices[4]}

def get_company_info(gameId, id):
    engine = create_engine("mysql+pymysql://%s:%s@%s:3306/%s" % (USER, PASS, HOST, DB_NAME))
    metadata = MetaData()
    metadata.reflect(engine)
    companies = Table(str(gameId)+'_companies', metadata, autoload_with=engine)
    Session = sessionmaker(bind = engine)
    session = Session()
    comp = session.query(companies).all()[id - 1]
    return {'story': comp[1], 'act_num': comp[2], 'price': comp[3]}

def get_gamer_info(gameId, id):
    engine = create_engine("mysql+pymysql://%s:%s@%s:3306/%s" % (USER, PASS, HOST, DB_NAME))
    metadata = MetaData()
    metadata.reflect(engine)
    gamers = Table(str(gameId)+'_gamers', metadata, autoload_with=engine)
    Session = sessionmaker(bind = engine)
    session = Session()
    gamer = session.query(gamers).all()[id - 1]
    return {'Balance': gamer[1], 'company_1': gamer[3], 'company_2': gamer[4], 'company_3': gamer[5], 'company_4': gamer[6], 'company_5': gamer[7]}

#######################

app = Flask(__name__)
api = Api(app)

PASS = '123456'
USER = 'worker'
HOST = 'db'
# HOST = '127.0.0.1'
DB_NAME = 'games'
#
GAMERS = [1, 2]
COMPANIES = [1, 2, 3, 4, 5]

# app.secret_key = 'some secret salt'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s/%s' % (USER, PASS, HOST, DB_NAME)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
    
class StartGame(Resource):
    def get(self, id=0):
        id = int(request.args.get('id'))
        ans = initial_game(id, GAMERS)
        return ans, 200
    
class Auction(Resource):
    def get(self, gameId=0, companyId=0, gamerId=0, count=0):
        companyId = int(request.args.get('company_id'))
        count = int(request.args.get('count'))
        gamerId = int(request.args.get('gamer_id'))
        gameId = int(request.args.get('game_id'))
        ans = buy(gameId, companyId, gamerId, count)
        return ans, 200

class StopGame(Resource):
    def get(self, id=0):
        id = int(request.args.get('id'))
        ans = stop_game(id)
        return ans, 200
    
class GetCompanyInfo(Resource):
    def get(self, gameId=0, id=0):
        gameId = int(request.args.get('game_id'))
        id = int(request.args.get('id'))
        ans = get_company_info(gameId, id)
        return ans, 200

class GetGamerBalance(Resource):
    def get(self, gameId=0, id=0):
        gameId = int(request.args.get('game_id'))
        id = int(request.args.get('id'))
        ans = get_gamer_info(gameId, id)
        return ans, 200

api.add_resource(StartGame, "/api/v1/start-game", "/api/v1/start-game/", "/api/v1/start-game/<int:id>")
api.add_resource(Auction, "/api/v1/auction", "/api/v1/auction/")
api.add_resource(StopGame, "/api/v1/stop-game", "/api/v1/stop-game/", "/api/v1/stop-game/<int:id>")
api.add_resource(GetCompanyInfo, "/api/v1/company/info", "/api/v1/company/info/")
api.add_resource(GetGamerBalance, "/api/v1/gamer/info", "/api/v1/gamer/info/")

if __name__ == '__main__':
    app.run()
