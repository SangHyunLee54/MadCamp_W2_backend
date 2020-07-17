import os
import functools
from flask import Flask, render_template, redirect, request, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from bson.objectid import ObjectId
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)

db = client.test_users

#user_info = client.test_users.user_info
col = db.user_info
contacts_col = db.contacts

for i in col.find():
    print(i)

@app.route('/')
def inputTest(num=None):
    return render_template('index.html')

@app.route('/sign_up')
def sign_up():
    return render_template('SignUp.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    ID = request.form['id']
    password = request.form['password']
    is_already = col.find({"id":ID})

    for us in is_already:
        print(us)

    if is_already.count():
        return 'Sign up Failed'
    col.insert({'id':ID, 'password':password})
    return 'Sign up Success'
    
@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/check_user', methods=['POST'])
def check_user():
    ID = request.form['id']
    password = request.form['password']
    is_already = col.find({'id':ID,'password':password})

    for us in is_already:
        print(us)

    if is_already.count():
        return 'Login Success'
    return 'Login Failed'

@app.route('/add_c')
def add_c():
    return render_template('AddContact.html')

@app.route('/add_contact', methods=['POST'])
def add_contact():
    ID = request.form['id']
    password = request.form['password']
    name = request.form['name']
    phone_no = request.form['phone_no']

    is_user = col.find({'id':ID,'password':password})
    if not is_user.count():
        return 'Can not find in user list'

    if len(name) == 0 or len(phone_no) == 0:
        return 'Please complete name and number'

    contacts_col.insert({'id':ID, 'password':password, 'name':name, 'phone_no':phone_no})
    return 'Add Complete'

@app.route('/get_c')
def get_c():
    return render_template('getContact.html')

@app.route('/get_contact', methods=['POST'])
def get_contact():
    ID = request.form['id']
    password = request.form['password']

    is_user = col.find({'id':ID,'password':password})
    if not is_user.count():
        return 'Can not find in user list'

    contact_list = contacts_col.find({'id':ID,'password':password})

    result = ""

    for cont in contact_list:
        result += cont['name'] + ": " +cont['phone_no'] + " | ObjectId: " + str(cont['_id']) + "<br>"
        
        
    return result

@app.route('/del_c')
def del_c():
    return render_template('DeleteContact.html')


@app.route('/del_contact', methods=['POST'])
def delete_contact():
    ID = request.form['id']
    password = request.form['password']
    Oid = request.form['Oid']

    is_user = col.find({'id':ID,'password':password})
    if not is_user.count():
        return 'Can not find in user list'

    if not contacts_col.find({'id':ID, 'password':password, '_id':ObjectId(Oid)}).count():
        return 'Can not find Object'

    contacts_col.delete_one({'_id':ObjectId(Oid)})
    
    return 'Delete Complete'

@app.route('/edit_c')
def edit_c():
    return render_template('EditContact.html')

@app.route('/edit_contact', methods=['POST'])
def edit_contact():
    ID = request.form['id']
    password = request.form['password']
    Oid = request.form['Oid']
    name = request.form['name']
    phone_no = request.form['phone_no']

    is_user = col.find({'id':ID,'password':password})
    if not is_user.count():
        return 'Can not find in user list'

    if not contacts_col.find({'id':ID, 'password':password, '_id':ObjectId(Oid)}).count():
        return 'Can not find Object'

    if len(name) > 0:
        contacts_col.find_one_and_update({'_id':ObjectId(Oid)},{'$set': {'name': name}})

    if len(phone_no) > 0:
        contacts_col.find_one_and_update({'_id':ObjectId(Oid)},{'$set': {'phone_no': phone_no}})

    return 'Edit Complete'

@app.route('/add_I')
def add_i():
    return render_template('AddFile.html')

@app.route('/add_Image', methods=['POST'])
def add_image():
    ID = request.form['id']
    password = request.form['password']
    Image_file = request.files['File']
    print(Image_file.filename)
    #Image_file.save(secure_filename(Image_file.filename))
    Image_file.save(os.path.join('files', secure_filename(Image_file.filename)))
    return "Hello"

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80)
