from flask import Flask, render_template, Response, redirect, request, url_for, flash, session
from Face import VideoCamera, VideoCamera1

import time
from flask_mysqldb import MySQL
import cv2
import csv
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
import hashlib
import re
#from registered import registered
#from new import new

app = Flask(__name__)
app.secret_key = "dbdj34jsnf"
#app.register_blueprint(registered, url_prefix="/registered")
#app.register_blueprint(new, url_prefix="/register")


index1 = open("index.txt","r") # file to access next user id
index_id = index1.read()
index1.close()

res = open("result.txt","r") # file to check the FR match
result = res.read()
res.close()

KNOWN_FACES_DIR = 'known_faces'
class data():
    myres=[]
d=data()

app.config['MYSQL_HOST'] = '134.122.46.178' #ip address
app.config['MYSQL_USER'] = 'greetingrpi' # greetingrpi
app.config['MYSQL_PASSWORD'] = 'greetingrpi' #greetingrpi
app.config['MYSQL_DB'] = 'registration' #registration
mysql = MySQL(app)


@app.route('/') # Welcome to Fleming Page
def index():
    return render_template('index.html')


                                  #########       REGISTERED USER        #########

@app.route('/regdisclamer', methods=['GET','POST']) # Are you reg with FR?
def regdisclamer():
    if request.method == "POST":
        return render_template('regdisclamer.html')
    return render_template('regdisclamer.html')



@app.route('/login', methods=['GET','POST']) # No - login
def login():
    if request.method == "POST":
        email = request.form['email']
        cur = mysql.connection.cursor() 
        cur.execute("SELECT question FROM users WHERE email = %s", (email,))
        uname = cur.fetchone()
        if uname == None:
            flash("Could not find result! Please check the Email or Register as new user.")
            return redirect(url_for("index"))
        print (uname)
        #question = cur.fetchone()
        #session["name"] = name
        return render_template('confirmlogin.html', uname = uname)
    else:
        #if "name" in session:
        #    return redirect(url_for("welcome"))
        return render_template('login.html')



@app.route('/confirmlogin', methods=['GET','POST']) # Confirm login
def confirmlogin():
    if request.method == "POST" and 'answer' in request.form:
        name = request.form['name']
        ans = request.form['answer']
        ans_ = hashlib.md5(ans.encode())
        answer = ans_.hexdigest()
        cur = mysql.connection.cursor() 
        cur.execute("SELECT * FROM users WHERE name = %s AND answer =%s", (name, answer,)) ## compare email & link FR if error
        account = cur.fetchone()
        if account: 
            session['loggedin'] = True
            #session['faceid'] = account[0] 
            session['name'] = account[1] 
            flash('Logged in successfully !')
            return render_template('welcome.html',name=name) 
        else: 
            flash('Incorrect name / answer !')
            return render_template('index.html') 
    else:
        return render_template('login.html')


@app.route('/face_reco') # Yes - Recognition/ Login for FR
def face_reco():
    return render_template('face_reco.html')

@app.route('/login_face') #get data from DB send to Welcome page
def login_face():
    res = open("result.txt","r") # file to check the FR match
    result = res.read()
    res.close()
    faceid = result
    if faceid == str(0):
        flash("Face could not be recognised! Please Login using Email.")
        return redirect(url_for("login"))
    cur = mysql.connection.cursor() 
    cur.execute("SELECT * FROM users WHERE faceid = %s", (faceid,))
    account = cur.fetchone()
    
    if account:
        session['loggedin'] = True
        session['faceid'] = account[0] 
        session['name'] = account[1] 
        flash('Logged in successfully !')
        return render_template('welcome.html',name=account[1]) 
    else: 
         flash("Face could not be recognised! Please Login using Email.")
         return redirect(url_for("login"))
   
    return render_template('welcome.html', name = name)


                                    #########       NEW USER        #########

@app.route('/facialregdisclamer', methods=['GET','POST']) # Do you want to reg using FR
def facialregdisclamer():
    if request.method == "POST":
        return render_template('facialregdisclamer.html')
    return render_template('facialregdisclamer.html')


@app.route('/face_reg') # Yes - Registration for FR
def face_reg():
    return render_template('face_reg.html')
@app.route('/registerface', methods=['GET','POST']) ## entering details after registration using Facial Reco
def registerface():
    import os.path
    next_id = index_id + '-A'
    isdir = os.path.isdir(f"{KNOWN_FACES_DIR}/{next_id}")
    if isdir == False:
        flash("Could not register Face! Please register without Facial Recognition")
        return redirect(url_for("reg"))
    if request.method == "POST" and "name" in request.form and "answer_1" in request.form and "email" in request.form:
        details = request.form
        fname = details['name']
        email = details['email']
        faceid = details['faceid']
        ans = details['answer_1']
        ans_ = hashlib.md5(ans.encode())
        answer = ans_.hexdigest()
        #answer_2 = details['']
        question = details['question']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE email = % s', (email, )) 
        account = cur.fetchone() 
        if account: 
            flash( 'Account already exists !')
            return render_template('registerface.html',id=next_id)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
            flash( 'Invalid email address !')
            return render_template('registerface.html',id=next_id)
        elif not re.match(r'[A-Za-z0-9]+', fname): 
            flash('Name must contain only characters and numbers !')
            return render_template('registerface.html',id=next_id)
        elif not fname or not ans or not email: 
            flash( 'Please fill out the form !')
            return render_template('registerface.html',id=next_id)
        else: 
            cur.execute('INSERT INTO users(faceid, name, email, question, answer) VALUES (% s, % s, % s, % s, % s)', (faceid, fname, email, question, answer )) 
            mysql.connection.commit() 
            flash('You have successfully registered !')
            return render_template('welcome.html',name=fname)
    elif request.method == 'POST': 
        flash( 'Please fill out the form !')
        return render_template('welcome.html',name=fname)
        #cur.execute("INSERT INTO users(faceid, name, email, question, answer) VALUES (%s, %s, %s, %s, %s)", (faceid, fname, email, question, answer))
        #mysql.connection.commit()
        #cur.close()
        ##session["name"] = fname
    else:
        #if "name" in session:
        #    return redirect(url_for("welcome"))
        return render_template('registerface.html',id=next_id)


@app.route('/reg', methods=['GET','POST']) # No - Registration 
def reg():
    if request.method == "POST" and "name" in request.form and "answer_1" in request.form and "email" in request.form:
        details = request.form
        fname = details['name']
        email = details['email']
        ans = details['answer_1']
        ans_ = hashlib.md5(ans.encode())
        answer = ans_.hexdigest()
        #answer_2 = details['']
        question = details['question']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE email = % s', (email, )) 
        account = cur.fetchone() 
        if account: 
            flash( 'Account already exists !')
            return render_template('reg.html')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
            flash( 'Invalid email address !')
            return render_template('reg.html')
        elif not re.match(r'[A-Za-z0-9]+', fname): 
            flash('Name must contain only characters and numbers !')
            return render_template('reg.html')
        elif not fname or not ans or not email: 
            flash( 'Please fill out the form !')
            return render_template('reg.html')
        else: 
            cur.execute("INSERT INTO users(name, email, question, answer) VALUES (%s, %s, %s, %s)", (fname, email, question, answer))
            mysql.connection.commit()
            cur.close()
        #session["name"] = fname
            return render_template('welcome.html',name=fname) # Welcome Name
    else:
        #if "name" in session:
        #    return redirect(url_for("welcome"))
        return render_template('reg.html')

                                  #########       GUEST        #########

@app.route('/guest', methods=['GET','POST']) # Guest
def guest():
    if request.method == "POST":
        details = request.form
        name = details['name']
        #session["name"] = name
        return render_template('welcome.html', name = name)
    
        #if "name" in session:
        #    return redirect(url_for("welcome"))
    return render_template('guest.html')

@app.route('/welcome', methods=['GET','POST']) # After reg/login/guest login
def welcome():
    #if "name" in session:
    #    name = session['name']
        return render_template('welcome.html')
    #else:
    #    return redirect (url_for("index"))
    #return render_template('guest.html')

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        location_keywords = open("location_keywords.txt", "r") 
        location_reader = csv.reader(location_keywords)

        user_search = request.form['user']
        stop_words = set(stopwords.words('english'))  
  
        word_tokens = word_tokenize(user_search.lower())  
        filtered_sentence = []   
        filtered_sentence = [w for w in word_tokens if not w in stop_words]  
        

        for row in location_reader:
            for field in row:
                result = [w for w in filtered_sentence if w in field]
                if result != []:
                    d.myres.append(row[0])

        myres = list(dict.fromkeys(d.myres))
        return render_template('search.html',res=myres)
        location_keywords.close()
    else:
        return render_template('search.html',res=myres)
@app.route('/searchvoice', methods=['GET','POST'])
def searchvoice():
    import speech_recognition as sr

    recognizer = sr.Recognizer()


    try:

        with sr.Microphone() as source:
            print('Speak Now')
            recognizer.adjust_for_ambient_noise(source)#(Problem Solved)
            voice= recognizer.listen(source)
            text= recognizer.recognize_google(voice)
            print(text)
            return render_template('welcome.html', search=text)
            
        
    except:
        flash('Sorry could not recognize your voice')
        return render_template('welcome.html')
        

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame == None:
            frame = camera.get_frame()
        else:
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
 

@app.route('/video_feed') #video for registration FR
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed1') #video for recognition FR
def video_feed1():
    return Response(gen(VideoCamera1()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/logout') #end session 
def logout():
    session.pop('loggedin', None) 
    session.pop('faceid', None) 
    session.pop('name', None) 
    flash("Logged out successfully")
    return redirect(url_for('index')) 

if __name__ == '__main__':
    app.run(debug=True)
