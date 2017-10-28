######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Baichuan Zhou (baichuan@bu.edu) and Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further und0000erstanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
#import flask.ext.login as flask_login
#import flask.ext.login as flask_login
#from flask.ext.login import LoginManager
import flask_login
import time


# for image uploading
# from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your credentials
app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'BOston2019!'
app.config['MYSQL_DATABASE_PASSWORD'] = '940804'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM Users")
users = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html')
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('hello.html', message = 'Please log in or create an account')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')

#registering new user
@app.route("/register", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        DOB = request.form.get('DOB')

    except:
        print("couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO Users (email, password,firstname, lastname, username, DOB)"
                             "VALUES ('{0}', '{1}','{2}', '{3}','{4}', '{5}')".format(email, password,
                              firstname, lastname,username,DOB)))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('profile.html', name=firstname, message='Account Created!')
    else:
        print("couldn't find all tokens")
        return render_template('register.html', supress=False)

#to list names of albums on user profile page
def listalbums():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    albumnames = "SELECT name " \
                 "FROM Albums WHERE albumOwner = '{0}'".format(uid)
    albumnames = cursor.execute(albumnames)
    #albumnames = cursor.fetchall()
    cursor.fetchall()
    #for name in albumnames:
        #name.encode('ascii', 'ignore')
    return albumnames

@app.route('/view_album')
def albumpageview():
	return render_template('view_album.html')

@app.route("/view_album", methods=['GET','POST'])
def view_album():
    album = request.form.get('view_album')
    albumname = album[2:-2]
    try:
        print(album[1])
        #not sure if what i put actually works yet
        uid = getUserIdFromEmail(flask_login.current_user.id)
        albumid = getAlbumID(uid)
        #photos = getPhotosFromAlbum(getUserIdFromEmail(),album[1]) #how can I get the album id ???????????
        photos = getPhotosFromAlbum(uid, albumid)
    except:
        print("couldn't find all tokens")
        #return render_template('view_album.html', album=albumname, albumid = album[1])
        return render_template('view_album.html', album=albumname, albumid=albumid)
    return render_template('view_album.html', album = albumname, photos = photos, albumid = album)
## need to figure out how to get the album id so I can pass it into view_album which can then be passed
## from there into upload -- bc I want only to be able to upload from within an album
## UNLESS it's easier to do a general upload and have the user select which album to upload into?


def getUsersPhotos(uid):
    cursor = conn.cursor()
    #cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
    cursor.execute("SELECT imgdata, photoid, caption FROM Photos WHERE user_id = '{0}'".format(uid))
    photos = cursor.fetchall()
    print(photos)
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

def getPhotosFromAlbum(uid,albumid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, photo_id, caption FROM Photos \
                    WHERE Photos.user_id = '{0}' AND Photos.album_id = '{1}'".format(uid,albumid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

def getUsersAlbums(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT name, albumID FROM Albums WHERE albumOwner = '{0}'".format(uid))
    return cursor.fetchall()


def getAlbumID(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT albumID FROM Albums WHERE albumOwner = '{0}'".format(uid))
    return cursor.fetchall()


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def getNameFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT firstname  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True

#display your friends on your profile page ~not working yet~
@app.route('/friendlist', methods=['GET'])
def displayFriends(uid):
    cursor = conn.cursor()
    friends = "SELECT u.firstname, u.lastname " \
              "FROM Users u, Friends f,  " \
              "WHERE f.userID1 = '{0}' "\
              "AND f.userID2 = u.user_id OR f.userID2 = '{0}'" \
              "AND f.userID1 = u.user_id".format(uid)
    cursor.execute(friends)
    friends = cursor.fetchall()
    return render_template('profile.html', friends = friends, message = "Your Friends")

def friendcount(uid):
    cursor = conn.cursor()
    print(uid)
    #count = "SELECT count(distinct(userID1 + userID2))" \
    #       "FROM Friends " \
    #       "WHERE userID1 OR userID2 = '{0}'".format(uid)

    count = "SELECT count(distinct(userID2))" \
            "FROM Friends " \
            "WHERE userID1 = '{0}'".format(uid)
    cursor.execute(count)
    count = cursor.fetchall()
    print('count: ', str(count))
    return str(count)[2:-4] #this was giving me count:  ((1,),) so i converted to string and sliced it

#@app.route('/search',methods=['GET','POST'])
#@flask_login.login_required
def getUserId(first_name, last_name):
    cursor = conn.cursor()
    query = "SELECT user_id " \
            "FROM Users WHERE firstname='{0}' AND lastname='{1}'".format(first_name, last_name)

    cursor.execute(query)
    user_id = cursor.fetchone()[0]
    return user_id

# end login code
#display current user profile
@app.route('/profile')
@flask_login.login_required
def protected():
    name = getNameFromEmail(flask_login.current_user.id)
    user = getUserIdFromEmail(flask_login.current_user.id)
    album = getUsersAlbums(user)[2:-2]
    uid = getNameFromEmail(flask_login.current_user.id)
    #photos = getUsersPhotos(user)
    #photopath = showPhotos(user)
    photopath = showPhotos()
    albumnames = listalbums()
    numberfriends = friendcount(user)
    return render_template('profile.html', name=flask_login.current_user.id,
                           firstname=name, albumname = albumnames, albums=album,
                           photopath = photopath, numberfriends = numberfriends)

# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

#direct to search page w/search bar
@app.route('/search')
def searchpage():
	return render_template('search.html')

#when search button is pressed
@app.route('/search',methods=['GET','POST'])
@flask_login.login_required
def search_friends():
    try:
        name = request.form.get('name')
        name = name.split(' ')
        first_name = name[0]
        last_name = name[1]
        uid = getUserId(first_name, last_name)
        #print(uid)
        cursor = conn.cursor()
        query  = "SELECT user_id, firstname, lastname " \
                "FROM Users WHERE firstname='{0}' AND lastname='{1}'".format(first_name, last_name)
        cursor.execute(query)
        users = cursor.fetchall()
        #info = getProfileInfo(uid)
        return render_template('search.html', users=users, message="User search results")
    except IndexError:
        return render_template('search.html', message="No results found, "
                                                                   "please enter first and last"
                                                                   "name")
#Should return USERS that created comments that match search
#return users ordered by number of comments
#that match the query for each user in descending order
# @app.route('/search',methods=['GET','POST'])
# @flask_login.login_required
# def search_comments():
#     comments = request.form.get('comments')
#     comments = comments.split(' ')
#     cursor = conn.cursor()
#     search = " "
#     for word in comments:
#         user = "SELECT userID" \
#                "FROM Comments " \
#                "WHERE text = '{0}'".format(word)
#         search += user
#         print(search)
#     result = cursor.execute(search)
#     result = cursor.fetchall()
#     return render_template('search.html', users = result, message="Comment search results:")

#when you click each user, get their info to display their profile
#display info such as: their name, photos, if you are friends or not
# @app.route('/friendprofile')
# def friendprofilepage():
# 	return render_template('friendprofile.html')

# @app.route('/friendprofile', methods=['GET','POST'])
# def getProfileInfo(uid):
#     cursor = conn.cursor()
#     #get first name
#     firstname = "SELECT firstname "\
#             "FROM USERS " \
#             "WHERE user_id ='{0}'".format(uid)
#     cursor.execute(firstname)
#     firstname = cursor.fetchone()[0]
#     print(firstname)
#     #get lastname
#     lastname = "SELECT lastname " \
#                 "FROM USERS " \
#                 "WHERE user_id ='{0}'".format(uid)
#     cursor.execute(lastname)
#     lastname = cursor.fetchone()[0]
#     print(lastname)
#     #get user photos
#     photos = getUsersPhotos(uid)
#     return render_template('friendprofile.html', firstname='firstname', lastname='lastname', photo=photos)

#Works!
#After searching for users, clicking on a user will add you as a friend
@app.route('/addfriend/<user>', methods=['GET'])
#@flask_login.login_required
def addfriends(user):
    try:
        uid = getUserIdFromEmail(flask_login.current_user.id)
        print('user uid: ', uid)
        print('friend uid: ', user )
        user = int(user)
        cursor = conn.cursor()
        query = "INSERT INTO Friends (userID1, userID2)" \
                "VALUES ('{0}', '{1}')".format(uid, user)
        cursor.execute(query)
        conn.commit()
        return render_template('/search.html', message = "added friend!")
    except:
        return render_template('/search.html', message="you're already friends with this user!")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/new_album', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
    if request.method == 'POST':
        if (True):
            cursor = conn.cursor()
            uid = getUserIdFromEmail(flask_login.current_user.id)
            albumName = request.form.get('album_title')
            date = time.strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO Albums(name, albumOwner, datecreated) VALUES('{0}', '{1}', '{2}')".format(albumName,uid,date))
            conn.commit()
            return render_template('new_album.html', message='Album Created!', supress = False)#albums=getUsersAlbums(uid))
        else:
            return render_template('new_album.html', message="Choose an album title", supress = True)
    else:
        return render_template('new_album.html', supress = True)

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    Uploads = '/Users/kaylaippongi/Desktop/PhotoShare/uploads'
    Uploads = '/Volumes/Old_HDD/Users/Yuta/Spock_Stuff/BU/CS460/PA1/PhotoShare1/static/uploads'
    app.config['Uploads'] = Uploads
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        uploadfile = request.files['photo']
        caption = request.form.get('caption')
        album_id = request.form.get('album_id')
        filename = "../uploads/" + uploadfile.filename            #img1.png, img2.png
        cursor = conn.cursor()

        #to save photos to upload folder
        uploadfile.save(os.path.join(app.config['Uploads'], filename))
        photo_data = base64.standard_b64encode(uploadfile.read())
        print(photo_data)                       #blank for some reason
        cursor = conn.cursor()
        query = "INSERT INTO Photos(imgdata, user_id, caption, photopath) VALUES('{0}', '{1}', '{2}', '{3}')".format(photo_data, uid, caption, filename)
        cursor.execute(query)
        #cursor.execute(
            #"INSERT INTO Pictures(imgdata, user_id, caption) \
             #VALUES ('{0}', '{1}', '{2}' )".format(photo_data, uid, caption))
            # getting a mysql syntax error when trying to upload but IDK WHY

            #I think it should work now! or at least error out of the way lol
            # used 'Photos' instead of 'Pictures' same thing in getUsersPhotos()
            #also had to do with the variable photo_data, python 3 doesn't support it, so change interpreter to 2.7

        conn.commit()
        return render_template('new_album.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUsersPhotos(uid))
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')

#Trying to display photos on profile
#not completely working yet, getting blue boxes
@app.route('/profile', methods=['GET'])
def showPhotos():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    query = "SELECT photopath " \
            "FROM Photos WHERE user_id = '{0}'".format(uid)
    cursor.execute(query)
    #photopath = cursor.fetchall()
    #print('photopath: ',photopath)
    return render_template('profile.html', photopath = "../uploads/img1.png")

# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welcome to Photoshare')

if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
