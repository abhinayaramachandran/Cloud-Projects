"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, session
from FlaskWebProject import app
import pymongo
from pymongo import MongoClient
import datetime
import base64
from bson.objectid import ObjectId
import os
from collections import defaultdict, OrderedDict


global u_id
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/authorize' ,methods=['POST'])
def user_login():
    global u_id
    client = MongoClient('path here/')
    db = client['abhinayadb']
    db.authenticate('username', 'password')
    username=request.form['username']
    password=request.form['password']
    collection=db['users']
    theUser=collection.find_one({"name":username})
    if not theUser:
         return "User does not exist"
    elif password==theUser['password']:
        #session['username'] =username
        #session['_id']=str(theUser['_id'])
        u_id=str(theUser['_id'])
        return render_template('Upload.html')
        #return 'Success'


@app.route('/upload' ,methods=['POST'])
def upload():
    global u_id
    client = MongoClient('path here/')
    db = client['abhinayadb']
    db.authenticate('username', 'password')
    collection=db['todo']
    subject=request.form['subject']
    note=request.files['note']
    image=request.files['image']
    count=db.count.find_one({"user_id":u_id})
    flag=''
    if not image:
        image=None
    else:
        stat=os.stat(image.filename)
        if stat.st_size > 10000000:
            return "Image Size too big"
        c=int(count['count_pic'])
        if c > 15:
            return "Sorry image upload limit exceeded"
        with open(image.filename, "rb") as image_file:
            c+=1
            image = base64.b64encode(image_file.read())
            db.count.update({"user_id":u_id},{"$set":{"count_pic":c}})
            flag='i'
    if not note:
        note=None
    else:
        n = int(count['count_notes'])
        if n > 20 :
            return "Sorry note upload limit exceeded"
        else:
            n+=1
            if os.stat(note.filename).st_size > 1000000:
                return 'Sorry file size too big!!'
            with open(note.filename,'rb') as my_file:
                note=my_file.read()
            db.count.update({"user_id":u_id},{"$set":{"count_notes":n}})
            flag=flag+'n'

    priority=request.form['priority']
    print type(priority)
    priority=int(priority)
    print type(priority)
    #user=session['_id']
    user = u_id
    date_now = datetime.datetime.now()
    date_time = str(date_now).split()
    upload_date=date_time[0]
    upload_time=date_time[1]
    collection.insert({"user":user,"subject":subject,"note":note,"image":image,"priority":priority,"date":upload_date,"time":upload_time,"flag":flag})
    return 'Success'



@app.route('/see_posts' ,methods=['POST'])
def view():
    global u_id
    user=u_id
    #user=session['_id']
    print user
    client = MongoClient('path here/')
    db = client['abhinayadb']
    db.authenticate('username', 'password')
    collection = db['todo']
    todos=collection.find({"user":user})
    todo_dict=[]
    i=0
    for t in todos:
        mytodo=[]
        i+=1
        subject=t['subject']
        mytodo.append(subject)
        priority=t['priority']
        mytodo.append(priority)
        date=t['date']
        mytodo.append(date)
        tim=t['time']
        mytodo.append(tim)
        if t['note']:
            note=t['note']
        else:
            note='The image uploaded was'
        mytodo.append(note)
        id=t['_id']
        mytodo.append(id)
        if t['image']:
            image=t['image']
            img=image.decode()
            my_img = "data:image/jpeg;base64," + img
            mytodo.append(my_img)
        todo_dict.append(mytodo)
    return render_template('show.html',res=todo_dict)




@app.route('/sort_by' ,methods=['POST'])
def sort_by():
    global u_id
    submit=request.form['submit']
    if submit=='Sort by date and time':
        var='date'
    elif submit=='Sort by priority':
        var='priority'
    user=u_id
    #user = session['_id']
    client = MongoClient('path here/')
    db = client['abhinayadb']
    db.authenticate('username', 'password')
    collection = db['todo']
    if var=='priority':
        #todos = collection.find({"user": user}).sort([("priority",1)])
        todos = collection.find({"user": user}).sort([("priority", -1)])
    else:
        todos = collection.find({"user": user}).sort([("date", -1),
                                                      ("time",-1)])
    todo_dict = []
    i = 0
    for t in todos:
        mytodo = []
        i += 1
        subject = t['subject']
        mytodo.append(subject)
        priority = t['priority']
        print priority
        mytodo.append(priority)
        date = t['date']
        mytodo.append(date)
        tim = t['time']
        mytodo.append(tim)
        if t['note']:
            note = t['note']
        else:
            note='The image uploaded was '
        mytodo.append(note)
        id = t['_id']
        mytodo.append(id)
        if t['image']:
            image = t['image']
            img = image.decode()
            my_img = "data:image/jpeg;base64," + img
            mytodo.append(my_img)
        todo_dict.append(mytodo)
    return render_template('show.html', res=todo_dict)


@app.route('/search_subject' ,methods=['POST'])
def search_subject():
    global u_id
    search_term=request.form['search_term']
    client = MongoClient('path here/')
    db = client['abhinayadb']
    db.authenticate('username', 'password')
    collection = db['todo']
    todo_dict = []
    i=0
    matching_todos=collection.find({"user":u_id,})
    for t in matching_todos:
        if search_term in t['subject']:
            mytodo = []
            i += 1
            subject = t['subject']
            mytodo.append(subject)
            priority = t['priority']
            print priority
            mytodo.append(priority)
            date = t['date']
            mytodo.append(date)
            tim = t['time']
            mytodo.append(tim)
            if t['note']:
                note = str(t['note'])
            else:
                note = 'The image uploaded was '
            mytodo.append(note)
            id = t['_id']
            mytodo.append(id)
            if t['image']:
                image = t['image']
                img = image.decode()
                my_img = "data:image/jpeg;base64," + img
                mytodo.append(my_img)
            todo_dict.append(mytodo)
    return render_template('show.html', res=todo_dict)

@app.route('/delete',methods=['POST'])
def delete():
    global u_id
    delete_id=request.form['delete_id']
    client = MongoClient('path here/')
    db = client['abhinayadb']
    db.authenticate('username', 'password')
    collection = db['todo']
    coll=db.count.find_one({"user_id":u_id})
    n=int(coll['count_notes'])
    i=int(coll['count_pic'])
    coll2=collection.find_one({'_id':ObjectId(delete_id)})
    if 'i' in str(coll2['flag'] ):
        i-=1
    if 'n' in str(coll2['flag']):
        n-=1
    db.count.update({"user_id":u_id},{"$set":{"count_pic":i,"count_notes":n}})
    collection.delete_one({"_id":ObjectId(delete_id)})
    return "Successfully deleted!!!"


