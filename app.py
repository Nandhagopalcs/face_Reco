import numpy as np
from flask import Flask, request, jsonify, render_template,session
import pickle
import face_recognition
import cv2
import os
from werkzeug.utils import secure_filename
import pymongo
from datetime import date


client = pymongo.MongoClient("mongodb+srv://nandhu:hinandhu100@cluster0.q49fb.mongodb.net/attendance?retryWrites=true&w=majority")
db = client['attendance']
col = db['encoding']
coll=db['present']
log=db['login']


app = Flask(__name__)
app.secret_key="hi"

@app.route('/')
def home():
    return render_template('landing.html')

@app.route("/firstlog")
def firstlog():
    return render_template('login.html')

@app.route("/logging", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        credentials = request.form.to_dict()
        existing_user = log.find_one(({"_id": credentials['check_id']}))
    
        if existing_user is None:
            return render_template("login.html")
        else:
            if credentials['check_id'] == existing_user["_id"] and credentials['check_name'] == existing_user['password']:
                session['college_id']=existing_user["c_id"]
                session['college_name']=existing_user['c_name']
                session['personal_id']=existing_user['_id']
                session['personal_name']=existing_user['name']
                session['role']=existing_user['role']

                if existing_user['role']=="admin":
                    cla=db[session['college_id']+"_classes"]
                    tr=db[session['college_id']+"_teachers"]
                    y=cla.find({})
                    z=tr.find({})
                    return render_template('adminview.html',data=existing_user,cl=y,t=z)
                elif existing_user['role']=="teacher":
                    cla=db[session['college_id']+"_classes"]
                    y=cla.find({})                    
                    return render_template('teacherview.html',data=existing_user,cl=y)
                elif existing_user['role']=="student":
                    att=db[session['college_id']+"_"+existing_user['class_id']+"_attendance"]
                    x=att.find({})
                    teachernames=set()
                    print(type(x))
                    
                    for i in x:
                        teachernames.add(i['teacher'])
                    teachernames = list(teachernames)
                    countatt=[]
                    for i in teachernames:
                        countatt.append(0)
                    print(teachernames, countatt, session['personal_name'])
                    dupli = att.find({})
                    for i in dupli:
                        if session['personal_name'] in i['present']:
                            a = teachernames.index(i['teacher'])
                            countatt[a]+=1
                        
                    print(countatt)
                    
                    dupli = att.find({})


                    return render_template('studentview.html',data=existing_user,teachernames=teachernames, countatt= countatt,at=dupli)
            else:
                return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/redirect')
def redirect():
    existing_user = log.find_one(({"_id": session['personal_id']}))
    if existing_user['role']=="admin":
        cla=db[session['college_id']+"_classes"]
        tr=db[session['college_id']+"_teachers"]
        y=cla.find({})
        z=tr.find({})
        return render_template('adminview.html',data=existing_user,cl=y,t=z)
    elif existing_user['role']=="teacher":
            cla=db[session['college_id']+"_classes"]
            y=cla.find({})                    
            return render_template('teacherview.html',data=existing_user,cl=y)
    elif existing_user['role']=="student":
            att=db[session['college_id']+"_"+existing_user['class_id']+"_attendance"]
            x=att.find({})
            teachernames=set()
            print(type(x))
            
            for i in x:
                teachernames.add(i['teacher'])
            teachernames = list(teachernames)
            countatt=[]
            for i in teachernames:
                countatt.append(0)
                   
            dupli = att.find({})
            for i in dupli:
                if session['personal_name'] in i['present']:
                        a = teachernames.index(i['teacher'])
                        countatt[a]+=1
                        
            print(countatt)
                    
            return render_template('studentview.html',data=existing_user,teachernames=teachernames, countatt= countatt)
            


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/sigup',methods=['GET','POST'])
def sigup():
    if request.method == 'POST':
        req = request.form
        a_name = req.get("a_name")
        a_id = req.get("a_id")
        c_id = req.get("c_id")
        c_name = req.get("c_name")
        passw = req.get("pwd")
        role=str("admin")
        log=db['login']
        existing_user = log.find_one(({"_id":a_id}))
        try_user = log.find_one(({"c_id":c_id}))
        
        if existing_user is not  None:
            if try_user is not None:
                return render_template('signup.html',kk=1,kkk=1)
                
        if existing_user is not  None:
            return render_template('signup.html',kk=0,kkk=1)
        
        if try_user is not None:
            return render_template('signup.html',kk=1,kkk=0)

        image = request.files['imagefile']
        basepath = os.path.dirname(__file__)
        image.filename=a_id+".jpg"
        file_path = os.path.join(basepath, 'static', secure_filename(image.filename))
        image.save(file_path)

        past = {"_id": a_id,"name":a_name,"c_id":c_id,"c_name":c_name,"password":passw,"role":role,"image":image.filename}

        log.insert_one(past)
        return render_template('login.html')
    else:
        return render_template('signup.html')


@app.route('/createclass')
def createclass():
    return render_template('class.html')


@app.route('/creatingclass',methods=['GET','POST'])
def creatingclass():
    if request.method =='POST':
        req = request.form
        class_id = req.get("class_id")
        class_name = req.get("class_name")
        infoc=db[session['college_id']+"_classes"]
        existing_user = infoc.find_one(({"_id":class_id}))
        try_user=infoc.find_one(({"class_name":class_name}))
        
        if existing_user is not  None:
            if try_user is not None:
                return render_template('class.html',kk=1,kkk=1)
                
        if existing_user is not  None:
            return render_template('class.html',kk=0,kkk=1)
        
        if try_user is not None:
            return render_template('class.html',kk=1,kkk=0)

        post={"_id": class_id,"class_name":class_name}
        
        infoc.insert_one(post)
        return render_template('class.html')
    else:
        return render_template('class.html')


@app.route('/createteacher')
def createteacher():
    data=db[session['college_id']+"_classes"]
    x=data.find({})
    cd=[]
    for y in x:
        cd.append(y['class_name'])
    return render_template('teacheradd.html',dt=cd,kkk=0)

@app.route('/creatingteacher',methods=['GET','POST'])
def creatingteacher():
    if request.method == 'POST':
        credent = request.form.to_dict()
        data=db[session['college_id']+"_classes"]
        x=data.find({})
        cd=[]
        for y in x:
            cd.append(y['class_name'])
        k=cd
        ls=[]
        
        for i in cd:
            if i in credent:
                ls.append(credent[i])
        
        try_user = log.find_one(({"_id":credent['p_id']}))
        
        if try_user is not None:
            return render_template('teacheradd.html',dt=k,kkk=1)
        
        image = request.files['imagefile']
        basepath = os.path.dirname(__file__)
        image.filename=credent['p_id']+".jpg"
        file_path = os.path.join(basepath, 'static', secure_filename(image.filename))
        image.save(file_path)
        
        pt={"_id":credent['p_id'],"name":credent['t_name'],"college_id":session['college_id'],"college_name":session['college_name'],"password":credent['pwd'],"classes":ls}
        infot=db[session['college_id']+"_teachers"]
        infot.insert_one(pt)
        lg=db['login']
        p={"_id":credent['p_id'],"name":credent['t_name'],"c_id":session['college_id'],"c_name":session['college_name'],"password":credent['pwd'],"role":str("teacher"),"image":image.filename}
        lg.insert_one(p)

        return render_template('teacheradd.html',dt=k,kkk=0)



@app.route('/createstudent')
def createstudent():
    data=db[session['college_id']+"_classes"]
    x=data.find({})
    cd=[]
    for y in x:
        cd.append(y['class_name'])
    return render_template('add.html',dt=cd)

@app.route('/creatingstudent',methods=['GET','POST'])
def creating():
    if request.method == 'POST':
        credent = request.form.to_dict()
        p_id=credent['p_id']
        name=credent['name']
        clas=credent['class']
        pwd=credent['pwd']
        l=db['login']

        try_user = l.find_one(({"_id":credent['p_id']}))
        
        if try_user is not None:
            data=db[session['college_id']+"_classes"]
            x=data.find({})
            cd=[]
            for y in x:
                cd.append(y['class_name'])
            return render_template('add.html',dt=cd,ex=1)

        
        image = request.files['imagefile']
        basepath = os.path.dirname(__file__)
        image.filename=p_id+".jpg"
        file_path = os.path.join(basepath, 'static', secure_filename(image.filename))
        image.save(file_path)
        print(file_path)
        img = face_recognition.load_image_file(file_path)
        
        encode = face_recognition.face_encodings(img)
        enc=list(encode.pop())
        
        
        check=db[session['college_id']+"_classes"]        
        existing_user = check.find_one(({"class_name":clas}))

        infocs=db[session['college_id']+"_"+existing_user['_id']]
        post = {"_id": p_id,"name":name,"c_id":session['college_id'],"c_name":session['college_name'],"password":pwd,"role":"student","class_id":existing_user['_id'],"image":image.filename}
        pot = {"_id": p_id, "name":name,"encode":enc,"c_id":session['college_id'],"c_name":session['college_name'],"password":pwd,"class_id":existing_user['_id'],"class_name":clas}
        infocs.insert_one(pot)
        l.insert_one(post)

        return render_template('added.html',val_name=name,val_id=p_id,st=1,usi=image.filename)


@app.route('/attendance')
def attendance():
    data=db[session['college_id']+"_classes"]
    x=data.find({})
    cd=[]
    for y in x:
        cd.append(y['class_name'])

    dat=db[session['college_id']+"_teachers"]
    tr=[]
    y=dat.find({})
    for i in y:
        tr.append(i['name'])
    return render_template('attendance.html',dt=cd,dp=tr)


@app.route('/find',methods=['Post'])
def find():
    if request.method == 'POST':
        credent = request.form.to_dict()
        clas=credent['class']
        tr=credent['teach']
        clsno=credent['num_cls']
        image=request.files['imgfile']
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
                basepath, 'static2', secure_filename(image.filename))
        
        image.save(file_path)
        print(file_path)
        img = face_recognition.load_image_file(file_path)
        #img = cv2.cvtColor(trials,cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(img)
        encodesCurFrame = face_recognition.face_encodings(img,facesCurFrame)
        #print(type(encodesCurFrame))
        check=db[session['college_id']+"_classes"]
        existing_user = check.find_one(({"class_name":clas}))

        col=db[session['college_id']+"_"+existing_user['_id']]
        results= col.find({})
        classNames=[]
        encodeListKnown=[]
        for result in results:
            classNames.append(result["name"])
            encodeListKnown.append(result['encode'])
        
        PresentNames=[]
        for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
            if min(faceDis) < 0.55:
                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    name = classNames[matchIndex]
                    #print(name)
                    PresentNames.append(name)
        
        setname = set(PresentNames)
        present=list(setname)
        
        absent=[]
        for a in classNames:
            if a not in present:
                absent.append(a)
        
        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
    
        coll=db[session['college_id']+"_"+existing_user['_id']+"_attendance"]
        
        postp = {"_id":clsno,"date":d1,"teacher":tr,"present":present,"absent":absent}
        coll.insert_one(postp)

        os.remove(file_path)
        return render_template('attended.html',val=present,vall=absent)


@app.route('/logout')
def logout():
    session.pop("college_id",None)
    session.pop("college_name",None)
    session.pop("personal_id",None)
    session.pop("personal_name",None)
    session.pop("role",None)

    return render_template('login.html')


@app.route('/previous')
def previous():
    data=db[session['college_id']+"_classes"]
    x=data.find({})
    cd=[]
    for y in x:
        cd.append(y['class_name'])

    
    return render_template('previous.html',dt=cd)

@app.route('/processing',methods=['GET','POST'])
def processing():
    if request.method == 'POST':
        
        data=db[session['college_id']+"_classes"]
        x=data.find({})
        cd=[]
        for y in x:
            cd.append(y['class_name'])
        credent = request.form.to_dict()
        clas=credent['class']
        check=db[session['college_id']+"_classes"]        
        existing_user = check.find_one(({"class_name":clas}))
        infocs=db[session['college_id']+"_"+existing_user['_id']+"_attendance"]
        x=infocs.find({})
    
    return render_template('previous.html',dt=cd,inf=x)

@app.route('/updateatt')
def updateatt():
    data=db[session['college_id']+"_classes"]
    x=data.find({})
    cd=[]
    for y in x:
        cd.append(y['class_name'])

    return render_template('updateattendance.html',dt=cd)
    
@app.route('/update',methods=['GET','POST'])
def update():
    if request.method == 'POST':
        data=db[session['college_id']+"_classes"]
        x=data.find({})
        cd=[]
        for y in x:
            cd.append(y['class_name'])

        credent = request.form.to_dict()
        clas=credent['class']
        nam=credent['person']
        uniq=credent['num_cls']
        status=credent['status']
        check=db[session['college_id']+"_classes"]        
        existing_user = check.find_one(({"class_name":clas}))
        infocs=db[session['college_id']+"_"+existing_user['_id']+"_attendance"]
        copy = infocs.find_one(({"_id":uniq}))
        oldp=copy['present']
        olda=copy['absent']
        if status=="present":
            olda.remove(nam)
            oldp.append(nam)
        if status=="absent":
            olda.append(nam)
            oldp.remove(nam)

        myquery = { "_id": uniq }
        newvalues = { "$set": { "present":oldp,"absent":olda } }
        infocs.update_one(myquery, newvalues)
        existing = infocs.find_one(({"_id":uniq}))

        return render_template('updateattendance.html',dt=cd,newp=existing['present'],newa=existing['absent'],st=1)

@app.route('/editing',methods=['GET','POST'])
def editing():
    data=db[session['college_id']+"_classes"]
    x=data.find({})
    cd=[]
    for y in x:
        cd.append(y['class_name'])
    return render_template('edit.html',dt=cd)


@app.route('/edit',methods=['GET','POST'])
def edit():
    if request.method == 'POST':
        credent = request.form.to_dict()
        p_id=credent['p_id']
        name=credent['name']
        clas=credent['class']
        pwd=credent['pwd']
        
        image = request.files['imagefile']
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'static', secure_filename(image.filename))
        image.save(file_path)
        print(file_path)
        img = face_recognition.load_image_file(file_path)
        
        encode = face_recognition.face_encodings(img)
        enc=list(encode.pop())
        l=db['login']
        
        check=db[session['college_id']+"_classes"]        
        existing_user = check.find_one(({"class_name":clas}))

        infocs=db[session['college_id']+"_"+existing_user['_id']]

        
        myquery = { "_id":p_id }
        newvalues = { "$set": { "encode":enc} }
        infocs.update_one(myquery, newvalues)
        
        

        return render_template('added.html',val_name=name,val_id=p_id,st=1,usi=image.filename)



@app.route('/file',methods=['GET','POST'])
def file():
    dat=db[session['college_id']+"_teachers"]
    tr=[]
    y=dat.find({})
    for i in y:
        tr.append(i['name'])
    return render_template('complaint.html',dp=tr)

    


@app.route('/complaint',methods=['GET','POST'])
def complaint():
    if request.method =='POST':
        req = request.form
        t_name = req.get("teach")
        complaint = req.get("complaint")
        dat=db[session['college_id']+"_complaint"]
        today = date.today()
        d1 = today.strftime("%d/%m/%Y")

        postp = {"teacher":t_name,"date":d1,"compaint":complaint,"student":session['personal_name']}
        dat.insert_one(postp)
        datt=db[session['college_id']+"_teachers"]
        tr=[]
        y=datt.find({})
        for i in y:
            tr.append(i['name'])    
    return render_template('complaint.html',dp=tr,c=1)

@app.route('/view',methods=['GET','POST'])
def view():
    dat=db[session['college_id']+"_complaint"]
    copy = dat.find(({"teacher":session['personal_name']}))
    return render_template('complaintview.html',information=copy)

   


if __name__ == '__main__':
    app.run(debug=True)