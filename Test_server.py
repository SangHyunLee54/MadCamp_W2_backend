import os
import functools
import codecs
import base64
import json
import logging
from flask import Flask, render_template, redirect, request, url_for, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from bson.objectid import ObjectId
from pymongo import MongoClient
from gridfs import GridFS


app = Flask(__name__)

client = MongoClient('localhost', 27017)

db = client.test_users

#user_info = client.test_users.user_info
col = db.user_info
contacts_col = db.contacts

gallery_col = db.gallery

fs = GridFS(db)

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

    current_app.logger.info("Called /add_user")
    current_app.logger.info(request.form)
    
    myResponse = {"result": 0}

    ID = request.form['id']
    password = request.form['password']
    username = request.form['username']

    is_already = col.find({"id":ID})

    for us in is_already:
        print(us)

    if is_already.count():
        myResponse["result"] = 2
        response = jsonify(myResponse)
        return response #'Sign up Failed'


    col.insert({'id':ID, 'password':password, 'username': username})
    myResponse["result"] = 1
    myResponse["id"] = ID
    myResponse["password"] = password
    myResponse["username"] = username
    response = jsonify(myResponse)
    return response #'Sign up Success'
    
@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/check_user', methods=['POST'])
def check_user():

    myResponse = {"result": 0}

    ID = request.form['id']
    password = request.form['password']
    is_already = col.find({'id':ID,'password':password})

    if is_already.count():
        myResponse["result"] = 1
        myResponse["id"] = ID
        myResponse["password"] = password
        myResponse["username"] = is_already[0]['username']
        response = jsonify(myResponse)
        return response #'Login Success'

    myResponse["result"] = 2
    response = jsonify(myResponse)
    return response #'Login Failed'

@app.route('/add_c')
def add_c():
    return render_template('AddContact.html')

@app.route('/add_contact', methods=['POST'])
def add_contact():

    myResponse = {"result": 0}

    ID = request.form['id']
    password = request.form['password']
    name = request.form['name']
    phone_no = request.form['phone_no']

    is_user = col.find({'id':ID,'password':password})
    if not is_user.count():
        myResponse["result"] = 2
        response = jsonify(myResponse)
        return response #'Can not find in user list'

    if len(name) == 0 or len(phone_no) == 0:
        myResponse["result"] = 2
        response = jsonify(myResponse)
        return response #'Please complete name and number'

    contact_Oid = contacts_col.insert({'id':ID, 'password':password, 'name':name, 'phone_no':phone_no})
    myResponse["id"] = ID
    myResponse["password"] = password
    myResponse["name"] = name
    myResponse["phone_no"] = phone_no
    myResponse["Oid"] = str(contact_Oid)
    myResponse["result"] = 1
    response = jsonify(myResponse)
    return response #'Add Complete'

@app.route('/get_c')
def get_c():
    return render_template('getContact.html')

@app.route('/get_contact', methods=['POST'])
def get_contact():

    myResponse = {"result": 0}

    ID = request.form['id']
    password = request.form['password']

    is_user = col.find({'id':ID,'password':password})
    if not is_user.count():
        myResponse["result"] = 2
        response = jsonify(myResponse)
        return response #'Can not find in user list'

    contact_list = contacts_col.find({'id':ID,'password':password})

    result = []
    #
    for cont in contact_list:
        #result += cont['name'] + ": " +cont['phone_no'] + " | ObjectId: " + str(cont['_id']) + "<br>"
        contact_t = {'name':cont['name'], 'phone_no':cont['phone_no'], 'Oid': str(cont['_id'])}
        result.append(contact_t)

    myResponse["contact_list"] = result
    myResponse["result"] = 1
    response = jsonify(myResponse)
    return response

@app.route('/del_c')
def del_c():
    return render_template('DeleteContact.html')


@app.route('/del_contact', methods=['POST'])
def delete_contact():

    myResponse = {"result": 0}

    ID = request.form['id']
    password = request.form['password']
    Oid = request.form['Oid']

    is_user = col.find({'id':ID,'password':password})
    if not is_user.count():
        myResponse["result"] = 2
        response = jsonify(myResponse)
        return response #'Can not find in user list'

    if not contacts_col.find({'id':ID, 'password':password, '_id':ObjectId(Oid)}).count():
        myResponse["result"] = 2
        response = jsonify(myResponse)
        return response #'Can not find Object'

    contacts_col.delete_one({'_id':ObjectId(Oid)})
    
    myResponse["result"] = 1
    response = jsonify(myResponse)
    return response #'Delete Complete'

@app.route('/edit_c')
def edit_c():
    return render_template('EditContact.html')

@app.route('/edit_contact', methods=['POST'])
def edit_contact():

    myResponse = {"result": 0}

    ID = request.form['id']
    password = request.form['password']
    Oid = request.form['Oid']
    name = request.form['name']
    phone_no = request.form['phone_no']

    is_user = col.find({'id':ID,'password':password})
    if not is_user.count():
        myResponse["result"] = 2
        response = jsonify(myResponse)
        return response #'Can not find in user list'

    if not contacts_col.find({'id':ID, 'password':password, '_id':ObjectId(Oid)}).count():
        myResponse["result"] = 2
        response = jsonify(myResponse)
        return response #'Can not find Object'

    if len(name) > 0:
        contacts_col.find_one_and_update({'_id':ObjectId(Oid)},{'$set': {'name': name}})

    if len(phone_no) > 0:
        contacts_col.find_one_and_update({'_id':ObjectId(Oid)},{'$set': {'phone_no': phone_no}})

    myResponse["result"] = 1
    response = jsonify(myResponse)
    return response #'Edit Complete'

@app.route('/add_I')
def add_i():
    return render_template('AddFile.html')

@app.route('/add_Image', methods=['POST'])
def add_image():
    ID = request.form['id']
    password = request.form['password']

    is_user = col.find({'id':ID,'password':password})
    if not is_user.count():
        return 'Can not find in user list'

    Image_file = request.files['File']
    Image_binary = base64.b64encode(Image_file.read())

    if not len(Image_binary):
        return 'Please upload with file'

    #save file in server directory
    #Image_file.save(os.path.join('files', secure_filename(Image_file.filename)))

    #image file save in MongoDB with GridFS
    fs = GridFS(db, "image")
    file_id = fs.put(Image_binary, filename = Image_file.filename)
    #save Object Id with the user info.
    gallery_col.insert({'id':ID, 'password':password, 'fileID':file_id})

    return str(file_id)

@app.route('/get_i')
def get_i():
    return render_template('getFile.html')

@app.route('/get_image', methods = ['POST'])
def get_image():

    ID = request.form['id']
    password = request.form['password']

    is_user = col.find({'id':ID,'password':password})
    if not is_user.count():
        return 'Can not find in user list'

    image_field_list = gallery_col.find({'id':ID,'password':password})

    fs = GridFS(db, "image")

    result = []

    for Img_field in image_field_list:
        file_id = Img_field['fileID']
        file_i = fs.get(file_id)
        result.append({"file_id": str(file_id), "content":file_i.read()})

        imgdata = base64.b64decode(file_i.read())
        filename = 'some_image.jpg'  # I assume you have a way of picking unique filenames
        with open(filename, 'wb') as f:
            f.write(imgdata)

    myResponse = {"files":result}
    print (myResponse)
    response = jsonify(myResponse)
    return response

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80)
