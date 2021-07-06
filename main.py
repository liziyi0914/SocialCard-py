from flask import Flask,request,abort
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from models import *
from playhouse.shortcuts import model_to_dict as m2d
from playhouse.shortcuts import dict_to_model as d2m
import hmac
import base64
import uuid
import datetime
import json

app = Flask(__name__)
CORS(app)
api = Api(app)

@app.before_request
def _db_connect():
    database.connect()

@app.teardown_request
def _db_close(exc):
    if not database.is_closed():
        database.close()

@app.teardown_request
def log(exc):
    Logs.create(path=request.path,ua=request.user_agent,ip=request.remote_addr,tracker=request.args.get('tracker',type=str,default=''))

def models(m):
    return [m2d(i) for i in m]

def parseJson():
    return json.loads(request.data.decode('utf-8'))

def checkAuth(token):
    ts = Tokens.select().where(Tokens.token==token)
    if(ts.count()==0):
        abort(403)
    t = ts.get()
    if(datetime.datetime.now()-t.update_time>datetime.timedelta(days=1)):
        abort(403)



class Profile(Resource):
    def get(self,profile_path):
        return m2d(Profiles.get(Profiles.path==profile_path))
    def post(self,profile_path):
        obj = parseJson()
        checkAuth(obj['token'])
        profile = d2m(Profiles,obj['data'])
        profile.save()
    def delete(self,profile_path):
        obj = parseJson()
        checkAuth(obj['token'])
        Profiles.get(Profiles.path==profile_path).delete_instance()

class ProfileList(Resource):
    def get(self):
        return models(Profiles.select())

class Group(Resource):
    def get(self,id):
        return models(ProfileGroups.select().where(ProfileGroups.profile_id==id))
    def post(self,id):
        obj = parseJson()
        checkAuth(obj['token'])
        profileGroup = d2m(ProfileGroups,obj['data'])
        profileGroup.save()
    def delete(self,id):
        obj = parseJson()
        checkAuth(obj['token'])
        ProfileGroups.get(ProfileGroups.id==id).delete_instance()

class GroupList(Resource):
    def get(self):
        return models(ProfileGroups.select())

class Card(Resource):
    def get(self,card_name):
        return m2d(Cards.get(Cards.name==card_name))
    def post(self,card_name):
        obj = parseJson()
        checkAuth(obj['token'])
        card = d2m(Cards,obj['data'])
        card.save()
    def delete(self,card_name):
        obj = parseJson()
        checkAuth(obj['token'])
        Cards.get(Cards.name==card_name).delete_instance()

class CardList(Resource):
    def get(self):
        return models(Cards.select())

class CompleteProfile(Resource):
    def get(self,profile_path):
        cs = models(Cards.select().join(ProfileGroups).join(Profiles).where(Profiles.path==profile_path))
        gs = list({c['group']['id']:c['group'] for c in cs}.values())
        def f(c):
            c['group'] = c['group']['id']
            return c
        def g(gr):
            gr['profile'] = gr['profile']['id']
            return gr
        p = {
                'profile': gs[0]['profile'],
                'groups': list(map(g,gs)),
                'cards': list(map(f,cs))
                }
        return p

class Login(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user', type=str, help='Invailed user', required=True)
        parser.add_argument('pwd', type=str, help='Invailed pwd', required=True)
        args = parser.parse_args()
        user = Users.get(Users.name==args['user'])
        pwd = args['pwd']
        if(hmac.new(user.salt.encode('utf-8'),pwd.encode('utf-8'),digestmod='sha256').hexdigest()==user.pwd):
            t = str(uuid.uuid4()).replace('-','')
            if(Tokens.select().where(Tokens.user==user).count()==0):
                Tokens.create(user=user,token=t)
            else:
                Tokens.update({Tokens.token:t,Tokens.update_time:datetime.datetime.now()}).where(Tokens.user==user).execute()
            return {'token':t}

class Token(Resource):
    def get(self,token):
        checkAuth(token)


api.add_resource(Profile,'/profile/<profile_path>')
api.add_resource(ProfileList,'/profiles')
api.add_resource(CompleteProfile,'/completeProfile/<profile_path>')
api.add_resource(Group,'/group/<id>')
api.add_resource(GroupList,'/groups')
api.add_resource(Card,'/card/<card_name>')
api.add_resource(CardList,'/cards')
api.add_resource(Login,'/login')
api.add_resource(Token,'/token/<token>')

def create_app():
    return app
