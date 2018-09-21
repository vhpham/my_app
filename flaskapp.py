# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 21:49:34 2018

@author: vietpham

"""
from flask import Flask, render_template,request,send_file,jsonify,redirect, url_for, flash, make_response, g

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    SelectField, SelectMultipleField, FormField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import ValidationError, DataRequired, InputRequired
from passlib.hash import pbkdf2_sha256 as sha256
import json, datetime
from werkzeug.wrappers import Response
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, jwt_optional, \
                                get_raw_jwt)
from flask_bootstrap import Bootstrap

debug = True
app = Flask(__name__)
app.secret_key = '3000hanover'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=60)
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['WTF_CSRF_ENABLED'] = True
jwt = JWTManager(app)
bootstrap = Bootstrap(app)
#app.config['JWT_BLACKLIST_ENABLED'] = True
#app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


debugFlag = False
admin_pwd = "hungpv168"
user_pwd = "vietpham"

def generate_hash(password):
    return sha256.hash(password)


def verify_hash(password, hash):
    return sha256.verify(password, hash)
    
blacklist = set()
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist    

class User(object):
    def __init__(self, id, username, password, roles='user'):
        self.id = id
        self.username = username
        self.password = generate_hash(password)
        self.registered_on = datetime.datetime.now()
        self.roles = roles
            

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In', id="btnLogin")
    
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
    
class LiveForm(FlaskForm):
    noLive = BooleanField("No Live")
    hasLive = BooleanField("Live Available")
    def validate_noLive(form, field):
        if len(field.data) > 1:
            raise ValidationError('Name must be less than 50 characters')             
    
class TypeForm(FlaskForm):
    o1x2 = BooleanField("1x2")
    oOU = BooleanField("Over/Under")
    oGoal = BooleanField("1/2 Goal")
    oAH = BooleanField("Asian Handicap")
    
class PeriodForm(FlaskForm):
    frmDate = DateField("From", format='%d-%m-%Y', id="fromdate")
    toDate = DateField("To", format='%d-%m-%Y', id="todate")
#    start_date = DateField('Start', validators=[DataRequired()], format = '%d/%m/%Y', description = 'Time that the event will occur', widget=widgets.DatePickerWidget)
    
class QueryForm(FlaskForm):
    type = SelectField(u'Type', choices = [('FA','FA'),('UEFA','UEFA'),('WC','WC')], validators = [DataRequired()],id="typeSel")
    #live = MultiCheckboxField('Live Available', choices=[('hasLive','noLive'),('Live Avaible','No Live')], id="liveRadio")
    #bet = MultiCheckboxField('Bet Type', choices=[('1x2','1x2'),('OU','Over/Under'),('1/2','1/2 Goal'),('AH','Asian Handicap')], id="betRadio")
    live = FormField(LiveForm)
    bet = FormField(TypeForm)
    period = FormField(PeriodForm)
    match = SelectField(u'Match', choices = [], validators = [DataRequired()],id="matchSel")
    submit = SubmitField('Plot', id="btnPlot")    
    
# An example store of users. In production, this would likely
# be a sqlalchemy instance or something similar.
users_to_roles = {
    'foo': ['admin'],
    'bar': ['user']
}
    
users = [
    User(1, 'admin', admin_pwd, roles='admin'),
    User(2, 'hungpv168', user_pwd),
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}
    
###########################################################################################################################

# You can override the error returned to the user if the
# user_loader_callback returns None. If you don't override
# this, # it will return a 401 status code with the JSON:
# {"msg": "Error loading the user <identity>"}.
# You can use # get_jwt_claims() here too if desired
@jwt.user_loader_error_loader
def custom_user_loader_error(identity):
    ret = {
        "msg": "User {} not found".format(identity)
    }
    return jsonify(ret), 404

    
# Protect a view with jwt_required, which requires a valid jwt
# to be present in the headers.
@app.route('/get_match', methods=['GET','POST'])
@jwt_required
def get_match():
    # Access the identity of the current user with get_jwt_identity
    wc = [u'Liverpool-NYC',u'NYC-SJS']
    wc_ch = []
    for idx,val in enumerate(wc):
        wc_ch.append({"id":idx,"text":val})
    return jsonify({'match': wc_ch}), 200
    
# Provide a method to create access tokens. The create_jwt()
# function is used to actually generate the token
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json() or request.form
    print(params)
    username = params.get('username', None)
    password = params.get('password', None)

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if username not in username_table.keys():
        return jsonify({"msg": "This user{0} is not allowed".format(username)}), 400

    headers = request.headers
    print(headers)
    headers = dict()
    # fetch the user data
    user = username_table[username]
    if verify_hash(password, user.password):
        access_token = create_access_token(identity=user.id)
        ret = {'access_token': access_token}
        return jsonify(ret), 200 
#        response = make_response("Hello World")
#        response.headers.set('Authorization', 'Bearer {0}'.format(access_token))        
#        response.headers.set('Cookie', request.headers.get('Cookie'))
#        print(response.headers)
#        return response
    else:
        return jsonify({"msg": "Password is wrong"}), 400

@app.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200

@app.after_request
def after(response):
    # todo with response
    val = getattr(g, 'auth', None)
    if val is not None:
        response.headers['Authorization'] = 'Bearer ' + str(val)
    return response
    
 
@app.route('/user_login', methods=['GET','POST'])
@jwt_optional
def user_login():
    current_user = get_jwt_identity()
    print(current_user)
    
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login!')
        access_token = create_access_token(identity=form.username.data)
        g.auth = access_token
        form = QueryForm()      
        return render_template('query.html', title='Query',figmsg="Hello World", form=form )
    return render_template('login.html', title='Login',form=form)
#
#@app.before_request
#def apply_b4_caching(response):
#    print('before ' + response.headers)


# index page
@app.route('/query', methods=['GET', 'POST'])
@jwt_required
def query():
    current_user = get_jwt_identity()
    print(current_user)
    
    form = QueryForm()
    if form.validate_on_submit():
        flash('Query!')
        return render_template('query.html', title='Query',figmsg="Hello World", form=form )
    return render_template('query.html', title='Query',form=form)
    
# index page
@app.route('/', methods=['GET', 'POST'])
@jwt_optional
def index():
    # If no JWT is sent in with the request, get_jwt_identity()
    # will return None
    current_user = get_jwt_identity()
    print(current_user)    
    form = LoginForm()
    print(blacklist)
    if current_user:
        print("in query")
        form = QueryForm()
        uefa = ['Barca-MU','Arseanl-Chelase']
        uefa_ch = []
        for idx,val in enumerate(uefa):
            uefa_ch.append((idx,val))
        form.match.choices = uefa_ch         
        if form.validate_on_submit():
            print('query submitted')
            flash('Your query is now live!')
            return render_template('query.html', title='Query',figmsg="Hello World", form=form )
        return render_template('query.html', title='Query', form=form)
    else:
        g.auth = ''
        
        if form.validate_on_submit():
            print('login')
            flash('You login')
            access_token = create_access_token(identity=form.username.data)
            form = QueryForm()
            wc = [u'Liverpool-NYC',u'NYC-SJS']
            wc_ch = []
            for idx,val in enumerate(wc):
                wc_ch.append(( str(idx),val))
            form.match.choices = wc_ch            
            g.auth = access_token
            return render_template('query.html', title='Query', form=form)
        print('index')
        return render_template('login.html', title='Sign In', form=form,current_user=current_user)

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,threaded=True)
