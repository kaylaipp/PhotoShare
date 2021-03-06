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
import Tkinter
import tkMessageBox

# for image uploading
# from werkzeug import secure_filename
import os, base64

#for string formatting
import re

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
    #user.is_authenticated = (request.form['password'] == pwd) ################### this line is giving me issues
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
        return render_template('login.html', suppress = True)
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
    return  render_template('login.html', suppress = False)


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

        uid = getUserIdFromEmail(flask_login.current_user.id)
        date = time.strftime("%Y-%m-%d")
        # creates album Unsorted for all unsorted pictures
        createUnsorted(uid, date)


        return render_template('profile.html', firstname=firstname, message='Account Created!')
        #return flask.redirect(flask.url_for('profile.html', firstname=firstname, message='Account Created!'))

    else:
        print("couldn't find all tokens")
        return render_template('register.html', supress=False)


def createUnsorted(uid, date):
    cursor = conn.cursor()
    unsorted = "INSERT INTO Albums(albumID, albumOwner, name, datecreated) VALUES(1, '{0}', 'Unsorted', '{1}')".format(uid, date)
    cursor.execute(unsorted)
    conn.commit()


# to list names of albums on user profile page
def listalbums(uid):

    cursor = conn.cursor()
    #unsorted_count = "SELECT COUNT(photoid) FROM Photos S WHERE S.album_id = 1 AND S.user_id ='{0}'".format(uid)
    unsorted_count = "SELECT photoid FROM Photos S WHERE S.album_id = 1 AND S.user_id ='{0}'".format(uid)
    unsorted_count = cursor.execute(unsorted_count)

    # This hides the album "unsorted" if there are no photos in it
    if (unsorted_count < 1):
        albumnames = "SELECT name " \
                 "FROM Albums " \
                 "WHERE  name != 'Unsorted' AND "\
                 "albumOwner = '{0}'".format(uid)
    else:
        albumnames = "SELECT name " \
                     "FROM Albums " \
                     "WHERE  "\
                     "albumOwner = '{0}'".format(uid) #
    # albumnames = "SELECT name FROM Albums WHERE albumOwner = '{0}'".format(uid)
    # cursor = conn.cursor()

    albumnames = cursor.execute(albumnames)
    albumnames = cursor.fetchall()
    #cursor.fetchall()
    converted = []
    for name in albumnames:
        name = str(name)
        converted.append(name[3:-3])
    #print(albumnames)

    return converted



# @app.route('/view_album')
# def albumpageview():
# 	return render_template('view_album.html')

@app.route("/view_album/<album>")
def view_album(album):
    message = ''

    try:
        uid = getUserIdFromEmail(flask_login.current_user.id)
        albumid = getAlbumID(uid,album)
        photos = getPhotosFromAlbum(uid,albumid) #path, id, caption
        albumnames = getUsersAlbums(uid)

    except:
        print("couldn't find all tokens")
        return render_template('view_album.html', album=album)


    try:
        comments = []
        for each in photos:
            comments = [getCommentForPicture(each[1])] + comments
    except:
        print("couldn't find all comments")

    try:
        numlikes = []
        print("numlikes",getnumlikes(11))
        for each in photos:
            numlikes.append(getnumlikes(each[1]))
        print(numlikes)
    except:
        print("couldnt get all likes")
        return render_template('view_album.html', album=album, albumid=albumid, photopath = photos, albumnames = albumnames)
    return render_template('view_album.html', album = album, photopath = photos, albumid = albumid, comments = comments, message = message, albumnames = albumnames, numlikes = numlikes)


@app.route("/move", methods = ['GET','POST'])
@flask_login.login_required
def move():
    psd = request.form.get("Move")
    psd = psd.split(',')
 #   print(psd)
    # pic, src, dest
    uid = getUserIdFromEmail(flask_login.current_user.id)
    albumid = getAlbumID(uid,psd[1])

    cursor= conn.cursor()
    albumname = ("SELECT S.name FROM Albums S WHERE S.albumID = '{0}' AND S.albumOwner = '{1}'".format(psd[2],uid))
    cursor.execute(albumname)
    albumname = cursor.fetchone()
#    print(albumname)
    conn.commit()

    cursor = conn.cursor()
    query = ("UPDATE Photos SET album_id = '{2}' WHERE album_id = '{1}' AND photoid = '{0}'".format(psd[0],albumid,psd[2]))
    cursor.execute(query)
    conn.commit()

    return flask.redirect(flask.url_for('view_album',album=psd[1]))


@app.route("/add_comment/<album>/<photo>", methods=['GET', 'POST'])
def add_comment(album,photo):
    if flask.request.method == 'POST':
        try:
            uid = getUserIdFromEmail(flask_login.current_user.id)
        except:
            uid = 1
        photoOwner = getPhotoOwnerID(photo)

        if uid == photoOwner:
            return flask.redirect(flask.url_for('browse'))

        date = time.strftime("%Y-%m-%d")
        comment = request.form.get('comment')
        test = isCommentUnique(comment)
        if test:
            insertComment(comment,uid, date)
            cursor=conn.cursor()
            cursor.execute("SELECT MAX(commentID) FROM Comments")
            cid = cursor.fetchall()
            cid = cid[0][0]
        else:
            cid = getCommentIDFromText(comment)
            cid = cid[0][0]
        insertHasComment(cid,photo,uid)
        if uid != 1: contributionscoreINC(uid) #anonymous doesn't count
        return flask.redirect(flask.url_for('browse', album=album))
    return flask.redirect(flask.url_for('browse'))





def getnumlikes(photo):
	cursor=conn.cursor()
	cursor.execute("SELECT COUNT(userID) FROM Likes WHERE photoid='{0}'".format(photo))
	return cursor.fetchone()[0]


def getUsersPhotos(uid):
    cursor = conn.cursor()
    #cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
    cursor.execute("SELECT imgdata, photoid, caption FROM Photos WHERE user_id = '{0}'".format(uid))
    photos = cursor.fetchall()
    #print('getUsersPhotos: ', photos)
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

def getPhotosFromAlbum(uid,albumid):
    cursor = conn.cursor()
    cursor.execute("SELECT S.photopath, S.photoid, S.caption FROM Photos S \
                    WHERE S.user_id = '{0}' AND S.album_id = '{1}'".format(uid,albumid))
    photoinfo = cursor.fetchall()
    print('getPhotosFromAlbum: ', photoinfo)
    #return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]
    return photoinfo


def getCommentForPicture(photoid):

    cursor = conn.cursor()
    cursor.execute("SELECT S.text,R.date,Q.firstname,Q.lastname,R.commenterID,R.photoid \
                    FROM (Comments S LEFT JOIN Has_Comment R ON S.commentID = R.commentID \
                    LEFT JOIN Users Q ON Q.user_id = R.commenterID) \
                    WHERE Q.user_id = S.userID AND R.photoid = '{0}'\
                    ORDER BY R.date DESC".format(photoid))
    return cursor.fetchall()

def getUsersAlbums(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT name, albumID FROM Albums WHERE albumOwner = '{0}'".format(uid))
    return cursor.fetchall()


def getAlbumID(uid,albumname):
    cursor = conn.cursor()
    cursor.execute("SELECT albumID FROM Albums WHERE albumOwner = '{0}' AND name = '{1}' ".format(uid,albumname))
    ret = cursor.fetchall()
    ret = str(ret)[2:-4]
    return ret


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

def hasTag(tagID,photoid):
    cursor=conn.cursor() # why does this keep coming out true
    cursor.execute("SELECT tagID, photoid FROM Has_Tag WHERE tagID = '{0}' AND photoid = '{1}'".format(tagID, photoid))
    test = cursor.fetchall()

    return test!=()

def isCommentUnique(comment):
    cursor=conn.cursor()
    if cursor.execute("SELECT text FROM Comments WHERE text = '{0}'".format(comment)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True

def isAlbumNameUnique(name,uid):

    cursor = conn.cursor()
    if cursor.execute("SELECT name FROM Albums WHERE name = '{0}' AND albumOwner = '{1}'".format(name,uid)):
        # this means there are greater than zero entries with that album_title
        return False
    else:
        return True

def getUsersFriends(uid):
    cursor = conn.cursor()
    #cursor.execute("SELECT user_id2 FROM Friends_with WHERE user_id1 = '{0}'".format(uid))
    #cursor.execute("SELECT userID1 FROM Friends WHERE userID1 = '{0}' OR userID2 = '{0}'".format(uid))
    cursor.execute("SELECT userID1 FROM Friends WHERE userID2 = '{0}' "
                   "UNION SELECT userID2 FROM Friends WHERE userID1 = '{0}'".format(uid))
    #cursor.execute(query)
    uidtuple = cursor.fetchall()
    #return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]
    return uidtuple

def getTopTags():
    cursor = conn.cursor()
    query = "SELECT tag FROM Tags GROUP BY tag ORDER BY COUNT(*) DESC LIMIT 5"
    taglist = cursor.execute(query)
    taglist = cursor.fetchall()
    converted = []
    for tag in taglist:
        tag = str(tag)
        converted.append(tag[3:-3])
    return converted


def getUsersTopTags(uid):
    cursor = conn.cursor()
    query = "SELECT tag FROM Tags, Users GROUP BY tag ORDER BY COUNT(*) DESC LIMIT 5 WHERE user_id = '{0}'".format(uid)
    taglist = cursor.execute(query)
    taglist = cursor.fetchall()
    converted = []
    for tag in taglist:
        tag = str(tag)
        converted.append(tag[3:-3])
    return converted

#should return photoid, as imgdata is blank
def getTaggedPhotos(tag_word):
    cursor = conn.cursor()
    cursor.execute("SELECT p.imgdata, p.photoid FROM Photos p, Has_Tag h, Tags t WHERE h.photoid=p.photoid \
                    AND h.tagID = t.tagID AND t.tag ='{0}'".format(tag_word))
    photos = cursor.fetchall()
    print(photos)
    return photos


def getCommentIDFromText(comment_text):
    cursor = conn.cursor()
    cursor.execute("SELECT S.commentID FROM Comments S WHERE S.text = '{0}'".format(comment_text))
    return cursor.fetchall()

def insertComment(comment_text,uid,date):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Comments(text, userID, date) VALUES('{0}','{1}','{2}')".format(comment_text, uid, date))
    conn.commit()

#get photopath of photo based on photoid
def getPhotoPath(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT photopath FROM Photos WHERE photoid = '{0}'".format(pid))
    return cursor.fetchall()

def insertHasComment(commentID, photoid,uid):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Has_Comment(commentID, photoid,commenterID) VALUES('{0}','{1}','{2}')".format(commentID, photoid,uid))
    conn.commit()


#return first,last name of likes on photo
def getPhotoLikes(photo_id):
    cursor = conn.cursor()
    cursor.execute("SELECT u.firstname, u.lastname FROM Likes l, Users u WHERE l.userID = u.user_id AND l.photo_id = '{0}'".format(photo_id))
    return cursor.fetchall() # (firstname, lastname)

#input photoid and return tags for that photo
def getTags(photo):
	cursor = conn.cursor()
	cursor.execute("SELECT tag FROM Tags T JOIN Has_Tag H on H.tagID = T.tagID WHERE H.photoid = '{0}'".format(photo))
	return cursor.fetchall()

#input photoid and return USERNAMES that have liked photo
def like_users(photo):
	cursor=conn.cursor()
	cursor.execute("SELECT U.username FROM Likes L LEFT JOIN Users U ON L.userID = U.user_id WHERE photoID ='{0}' AND U.user_id = L.userID".format(photo))
	return cursor.fetchall()

#input photoid and get username for owner
def getPhotoOwner(photo_id):
        print('getPhotoOwner photoid: ', photo_id)
        cursor=conn.cursor()
        cursor.execute("SELECT username FROM Users U, Photos P WHERE photoid= '{0}' AND P.user_id=U.user_id".format(photo_id))
        username = cursor.fetchone()
        print('getPhotoOwner: ', username)
        #return cursor.fetchone()
        return username

#input userID and return username:
def getUsername(uid):
    print('getUsername id: ', uid)
    cursor = conn.cursor()
    username = "SELECT username FROM Users WHERE user_id = '{0}'".format(uid)
    cursor.execute(username)
    username = cursor.fetchone()
    return username

def getMyTags(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT S.tag from Tags S join has_tag P ON S.tagID=P.tagID left join Photos Q on P.photoid=Q.photoid WHERE Q.user_id = '{0}'".format(uid))
    return cursor.fetchall()

def getAllTags():
    cursor = conn.cursor()
    cursor.execute("SELECT S.tag from (Tags S join has_tag P ON S.tagID=P.tagID left join Photos Q on P.photoid=Q.photoid)")
    return cursor.fetchall()

def getPhotoOwnerID(photo_id):
	cursor=conn.cursor()
	cursor.execute("SELECT P.user_id FROM Photos P WHERE photoid= '{0}'".format(photo_id))
	return cursor.fetchone()[0]

#input photoid and get comment texts, username and date from each user
# def getPhotoComments(photo_id):
#     cursor = conn.cursor()
#     cursor.execute("SELECT C.text, U.username FROM Comments C JOIN Has_Comment on H.commentID = C.commentID "\
#                    "JOIN Photos P on P.photoid = H.photoid " \
#                    "JOIN Users U on U.user_id = '{0}'".format(photo)

#input photoid and get comment texts, username and date from each user
def getPhotoComments(photo_id):
    cursor = conn.cursor()
    cursor.execute("SELECT C.text, U.username FROM Users U, Comments C, Has_Comment H, Photos P " \
                   "WHERE H.commenterID = U.user_id AND C.commentID = H.commentID " \
                   "AND P.photoid = '{0}'".format(photo_id))
    comments = cursor.fetchall()
    print('getPhotoComments: ', comments)
    #return cursor.fetchall() # (comment_text, firstname, lastname))
    return comments

def contributionscoreINC(user_id):
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET contributions = contributions + 1 WHERE user_id = '{0}' ".format(user_id))
    conn.commit()

def contributionscoreDEC(user_id):
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET contributions = contributions - 1 WHERE contributions > 0 AND user_id = '{0}' ".format(user_id))
    conn.commit()



#delete albums
@app.route("/deletealbum/<album>", methods=['GET'])
@flask_login.login_required
def delete_album(album):
        uid=getUserIdFromEmail(flask_login.current_user.id)
        cursor=conn.cursor()
        albumid = getAlbumID(uid, album)
        for x in getPhotosFromAlbum(uid,albumid):
            contributionscoreDEC(uid)
            print("DEC_A")
        cursor.execute("DELETE FROM Albums WHERE albumOwner='{0}' AND albumID='{1}'".format(uid,albumid))
        conn.commit()

        return render_template('view_album.html', album=album, message='Album deleted!')


#delete pictures
@app.route("/deletepicture/<album>/<photoID>", methods=['GET'])
@flask_login.login_required

def deletePhoto(photoID,album):
    cursor = conn.cursor()

    cursor.execute("SELECT photoid, commenterID FROM Has_Comment where photoid = '{0}'".format(photoID))
    loop = cursor.fetchone()
    for x in loop: contributionscoreDEC(loop[1])
    conn.commit()
    cursor.execute("DELETE FROM Has_Comment where photoid = '{0}'".format(photoID))
    conn.commit()
    cursor.execute("DELETE FROM Likes where photoID = '{0}'".format(photoID))
    conn.commit()
    cursor.execute("DELETE FROM Has_Tag WHERE photoid='{0}'".format(photoID))
    conn.commit()
    cursor.execute("DELETE FROM Belongs_To WHERE photoID='{0}'".format(photoID))
    conn.commit()
    cursor.execute("DELETE FROM Photos WHERE photoid='{0}'".format(photoID))
    conn.commit()
    email = flask_login.current_user.id
    uid = getUserIdFromEmail(email)
    message = "Picture deleted!"
    if uid != 1:
        contributionscoreDEC(uid)  # anonymous doesn't count
        print("DEC_p")
    return flask.redirect(flask.url_for('view_album',album=album))

#delete comments
@app.route("/deletecomment/<album>/<attrs>/", methods=['GET'])
@flask_login.login_required
def deleteComment(album,attrs):
    print(attrs)
    attrs = attrs.split('&')
    photoid = int(attrs[0])
    ctext = attrs[1]
    cdate = attrs[2]
    commenterid = int(attrs[3])
    cid = int(getCommentIDFromText(ctext)[0][0])

    if commenterid != 1: contributionscoreDEC(commenterid)  # anonymous doesn't count

    cursor = conn.cursor()
    query = "DELETE FROM Has_Comment WHERE (photoid = %s AND commenterID = %s AND date = %s AND commentID = %s)"
    args = photoid,commenterid,cdate,cid
    cursor.execute(query,args)
    conn.commit()

    return flask.redirect(flask.url_for('view_album', album=album))


#display your friends on your profile page
@app.route('/friends', methods=['GET'])
def displayFriends():
    cursor = conn.cursor()
    uid = getUserIdFromEmail(flask_login.current_user.id)
    query = "SELECT U.firstname,U.lastname from Users U, Friends F where F.userID1='{0}' AND F.userID2=U.user_id OR F.userID2='{0}' AND F.userID1=U.user_id".format(
            uid)
    cursor.execute(query)
    friends = cursor.fetchall()
    #print('friend count: ', len(friends))
    #print('friends: ', friends)
    return render_template('friends.html', friends = friends, message = "Your Friends")

def getMostContributors():
    cursor = conn.cursor()
    cursor.execute("SELECT S.firstname, S.lastname FROM Users S Where(S.firstname != 'anonymous' )ORDER BY S.contributions DESC LIMIT 10")
    ret = cursor.fetchall()
    ret = list(ret)

    for x in range(len(ret)):
        ret[x] = ret[x][0] +" "+ ret[x][1]

    return ret

def friendcount(uid):
    cursor = conn.cursor()
    #print(uid)
    #count = "SELECT count(distinct(userID1 + userID2))" \
    #       "FROM Friends " \
    #       "WHERE userID1 OR userID2 = '{0}'".format(uid)
    query = "SELECT U.firstname,U.lastname from Users U, Friends F where F.userID1='{0}' AND F.userID2=U.user_id OR F.userID2='{0}' AND F.userID1=U.user_id".format(
        uid)
    # count = "SELECT count(distinct(userID2))" \
    #         "FROM Friends " \
    #         "WHERE userID1 = '{0}'".format(uid)
    cursor.execute(query)
    friends = cursor.fetchall()

    count = len(friends)

    #return str(count)[2:-4] #this was giving me count:  ((1,),) so i converted to string and sliced it
    return count

#@app.route('/search',methods=['GET','POST'])
#@flask_login.login_required
def getUserId(first_name, last_name):
    cursor = conn.cursor()
    print 'getuserid: ', first_name
    print 'getuserid: ', last_name
    query = "SELECT user_id " \
            "FROM Users WHERE firstname='{0}' AND lastname='{1}'".format(first_name, last_name)

    cursor.execute(query)
    user_id = cursor.fetchone()[0]
    return user_id
def getUserNameUid(uid):
    cursor = conn.cursor()
    query = "SELECT firstname, lastname FROM Users WHERE user_id = '{0}'".format(uid)
    cursor.execute(query)
    name = cursor.fetchone()
    #name = name[-10:68]
    return name


def getTagIDFromTag(tag):
    cursor = conn.cursor()
    query = "SELECT tagID FROM Tags WHERE Tags.tag = '{0}'".format(tag)
    cursor.execute(query)
    name = cursor.fetchone()
    print("tagid is ",name)
    return name


# end login code

#display current user profile
@app.route('/profile')
@flask_login.login_required
def protected():
    email = flask_login.current_user.id
    name = getNameFromEmail(email)
    user = getUserIdFromEmail(email)
    #uid = getNameFromEmail(email)
    #photos = getUsersPhotos(user)
    photopath = showPhotos()

    albumnames = listalbums(user)
    numberfriends = friendcount(user)
    taglist = getTopTags()


    mostCont = getMostContributors()
    print(mostCont)

    return render_template('profile.html', name=flask_login.current_user.id,
                           firstname=name, albumname = albumnames,
                           photopath = photopath, numberfriends = numberfriends, tags = taglist, mostCont = mostCont)

# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

#direct to search page w/search bar
@app.route('/search')
@flask_login.login_required
def searchpage():
    friendrecs = friend_recommendations()
    #friendrecs = str(friendrecs)
    return render_template('search.html', friendrecs = friendrecs)
    #return render_template('search.html')

#when search button is pressed
@app.route('/search',methods=['GET','POST'])
#@app.route('/search')
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
        # print(users)
        #info = getProfileInfo(uid)
        return render_template('search.html', users=users, message="User search results")
    except IndexError:
        return render_template('search.html', message="No results found, "
                                                                   "please enter first and last"
                                                                   "name")
    #if the case person searched doesn't exist
    except TypeError:
        return render_template('search.html', message="No users found, please try again")

@app.route('/browse', methods = ['GET','POST'])
def browse():

    taglist = getTopTags()
    try:
        cursor = conn.cursor()
        query = ("SELECT *, S.firstname, S.lastname, Q.name FROM Photos P LEFT JOIN Users S ON P.user_id = S.user_id LEFT JOIN Albums Q ON P.user_id = Q.albumOwner AND P.album_id = Q.albumID")
        cursor.execute(query)
        query = cursor.fetchall()
        print(query)

    except:
        print("couldn't find all tokens")
        return render_template('browse.html', )
    try:
        comments = []
        for each in query:

            comments = [getCommentForPicture(each[0])] + comments
            print("comments :",comments)

    except:
        print("couldn't find all comments")
        return render_template('browse.html',   photopath = query)
    return render_template('browse.html', tags = taglist, photopath = query, comments = comments)



#friend profile not necessary anymore..will delete later
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

#Semi-Works!
# need to fix formatting for outputing names
# and actually adding them
#After searching for users, clicking on a user will add you as a friend
# @app.route('/addfriend/<user>', methods=['GET'])
# #@flask_login.login_required
# def addfriends(user):
#     try:
#         uid = getUserIdFromEmail(flask_login.current_user.id)
#         print('user uid: ', uid)
#         print('friend uid: ', user )
#         user = int(user)
#         cursor = conn.cursor()
#         query = "INSERT INTO Friends (userID1, userID2)" \
#                 "VALUES ('{0}', '{1}')".format(uid, user)
#         cursor.execute(query)
#         conn.commit()
#         return render_template('/search.html', message = "added friend!")
#     except:
#         return render_template('/search.html', message="you're already friends with this user!")

# #After searching for users, clicking on a user will add you as a friend
@app.route('/addfriend/<user>', methods=['GET'])
@flask_login.login_required
def addfriends(user):
    #try:
        uid = getUserIdFromEmail(flask_login.current_user.id)
        #print('user uid: ', uid)
        print('friend: ', user )
        #firstname = user[-1]
        fullname = user.replace('(', ' ').replace('u','').replace(')', '').split(',')
        firstname = fullname[0].encode()
        lastname = fullname[1].encode()
        print('friend: ', firstname)
        print('friend: ', lastname)
        friendid = getUserId(firstname[2:-1], lastname[2:-1])
        print('friendid: ', friendid)
        cursor = conn.cursor()
        query = "INSERT INTO Friends (userID1, userID2)" \
                "VALUES ('{0}', '{1}')".format(uid, friendid)
        cursor.execute(query)
        conn.commit()
        return render_template('/search.html', message = "added friend!")
    #except:
        #return render_template('/search.html', message="you're already friends with this user!")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/new_album', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
    if request.method == 'POST':
        albumName = request.form.get('album_title')
        uid = getUserIdFromEmail(flask_login.current_user.id)
        if isAlbumNameUnique(albumName,uid) and albumName != '':
            cursor = conn.cursor()
            uid = getUserIdFromEmail(flask_login.current_user.id)
            #albumName = request.form.get('album_title')
            date = time.strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO Albums(name, albumOwner, datecreated) VALUES('{0}', '{1}', '{2}')".format(albumName,uid,date))
            conn.commit()
            return render_template('new_album.html', message='Album Created!', supress = False)#albums=getUsersAlbums(uid))
        else:
            return render_template('new_album.html', message="Choose an album title", supress = True)
    else:
        return render_template('new_album.html', supress = True)

# Problems: doesn't store imgdata for some reason under python 2.7

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    #Uploads = '/Users/kaylaippongi/Desktop/PhotoShare/static/uploads'
    Uploads = '/Volumes/Old_HDD/Users/Yuta/Spock_Stuff/BU/CS460/PA1/PhotoShare1/static/uploads/'
    app.config['Uploads'] = Uploads

    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        uploadfile = request.files['photo']
        #ext = uploadfile.filename.rsplit('.', 1)[1]
        caption = request.form.get('caption')
        album_id = getAlbumID(uid,request.form.get('album'))
        tags = request.form.get('tags').rstrip(',').split(',')
        filename_NoPath = uploadfile.filename
        filename = Uploads + uploadfile.filename
        cursor = conn.cursor()

        print('upload photo full filename: ',filename)

        #to save photos to upload folder
        uploadfile.save(os.path.join(app.config['Uploads'], filename))
        photo_data = base64.standard_b64encode(uploadfile.read())


        #add photo info to database
        cursor = conn.cursor()
        query = "INSERT INTO Photos(imgdata, user_id, caption, photopath, album_id) " \
                "VALUES('{0}', '{1}', '{2}', '{3}','{4}')".format(photo_data, uid, caption, filename_NoPath,album_id)
        cursor.execute(query)
        contributionscoreINC(uid) #for uploading

        # get the photo id
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(photoid) FROM Photos")
        photoid = cursor.fetchall()[0][0]

        #format tags
        lst = []
        for i in tags:
            if ' ' in i:
                e = i.rstrip(' ').split(' ')
                for j in e:
                    if j != '':
                        lst.append(j)
            elif i != '':
                lst.append(i)


        #add tags to Tags table
        for word in lst:
            word = str(word)
            tagID = getTagIDFromTag(word)
            if tagID == None: #then tag doesn't already exist
                cursor=conn.cursor()
                cursor.execute("INSERT INTO Tags(tag) VALUES('{0}')".format(word))
                conn.commit()

            # add to has tags
            tagID = getTagIDFromTag(word)

            tagStatus = hasTag(tagID[0], photoid)

            if not tagStatus:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Has_Tag(tagID, photoid) VALUES ('{0}', '{1}')".format(tagID[0], photoid))
                conn.commit()


        conn.commit()
        return render_template('new_album.html', name=flask_login.current_user.id, message='Photo uploaded!',photos=getUsersPhotos(uid))
    # The method is GET so we return a  HTML form to upload the a photo.
    else:

        albumnames = listalbums(getUserIdFromEmail(flask_login.current_user.id))

        return render_template('upload.html', albumname=albumnames)


@app.route('/profile', methods=['GET'])
def showPhotos():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    query = "SELECT photopath " \
            "FROM Photos WHERE user_id = '{0}'".format(uid)
    cursor.execute(query)
    photopath = cursor.fetchall()
    converted = []
    for path in photopath:
        path = str(path)
        #print("[line 462 in showPhotos()] photopath is ",path[3:-3]) ####################################
        converted.append(path[3:-3])                                  #### tried changing slice to include ext
    #take brackets off of final list

    return converted

#return a string of recommended friends
#based on your friend's friend's
def friend_recommendations():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()

    myfriends = getUsersFriends(uid)
    myfriends = [i[0] for i in myfriends]

    #go through each of current user's friends and get their friends
    recommend = []
    theirfriends = []
    for friend in myfriends:
        print('myfriend: ', friend)
        theirfriends = getUsersFriends(friend)
        print('their friend tuple list: ', theirfriends)     #a tuple
        #convert tuple to list of uid ints
        theirfriends = [i[0] for i in theirfriends]
        print('thier friend int list: ', theirfriends)

    #go through their friends and append to recommend list
    #as long as 1) uid is not current user's uid, and 2) uid is not already in myfriends
    for user in theirfriends:
        if user not in myfriends and user != uid:
            print('adding ', user, ' to recommended list')
            recommend.append(user)
    print('recommended list: ', recommend)

    #go through recommened list, change those uids to actual string names
    recommendfriends = []
    for i in recommend:
        name = getUserNameUid(i)
        recommendfriends.append(name)

    #Formatting D: need to change from unicode to strings for nicer output
    first = []
    last = []
    for x in recommendfriends:
        #firstname = x[0].encode()
        #print('firstname: ', firstname[-3:3])
        #lastname = x[1].encode()
        # first.append(firstname)
        # last.append(lastname)
        first.append(x[0])
        last.append(x[1])
    final = zip(first,last)
    print('final: ', final)
    return final




@app.route('/searchcomments')
@flask_login.login_required
def searchcommentload():
    return render_template('searchcomments.html')


#Should return USERS that created comments that match search
#return users ordered by number of comments
#that match the query for each user in descending order
@app.route('/searchcomments',methods=['GET','POST'])
@flask_login.login_required
def search_comments():
    try:
        comments = request.form.get('comments')
        print('searchcomments: ', comments)
        # comments = comments.split(' ')
        # cursor = conn.cursor()
        #search = " "
        # user = "SELECT U.username " \
        #         "FROM Comments C JOIN Users U on U.user_id = C.userID " \
        #         "WHERE text = '{0}'".format(comments)

        user = "SELECT U.username, C.text, C.date " \
                "FROM Comments C JOIN Users U on U.user_id = C.userID " \
                "WHERE text = '{0}'".format(comments)

        # user = "SELECT U.username, C.text, H.date " \
        #         "FROM Has_Comments H JOIN Users U on U.user_id = H.commenterID " \
        #         "WHERE C.text = '{0}'".format(comments)

        #search += user
        #print(search)
        result = cursor.execute(user)
        result = cursor.fetchall()
        print('searchcomments user: ', result)
        return render_template('searchcomments.html', users = result, comment = comments)
    except:
        return render_template('searchcomments.html', message = "No user's have commented something like that, try again :) ")



@app.route('/searchtags')
#@flask_login.login_required
def searchtagload():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    mytags = list(getMyTags(uid))
    for eachtag in range(len(mytags)):
        mytags[eachtag] = str(mytags[eachtag])[3:-3]
    alltags = getAllTags()
    print(mytags)#############################################

    alltags = list(getAllTags())
    for eachtag in range(len(alltags)):
        alltags[eachtag] = str(alltags[eachtag])[3:-3]
    print(alltags)  #############################################
    return render_template('searchtags.html', mytags = mytags, alltags = alltags)

@app.route('/searchtags', methods = ['GET', 'POST'])
#@flask_login.login_required
def searchtags():
    #split tags by space, in the case where there is > 1 tag searched
    name = request.form.get('tags')

    name = name.split(' ')
    cursor = conn.cursor()

    photopaths = []
    for tag in name:
        photopath = "SELECT photopath FROM Photos P " \
                    "JOIN Has_Tag H on H.photoId = P.photoID JOIN Tags T on T.tagID = H.tagID " \
                    "WHERE T.tag = '{0}'".format(tag)

        cursor.execute(photopath)
        photopath = cursor.fetchall()
        # photopath = str(photopath)
        # print('photopath: ', photopath[4:-5])
        # # photopath = photopath[3:-3]
        # #This is causing photo not to show
        # photopath = photopath[4:-5]
        #photopaths.append(photopath)
        if photopath == '':
            return render_template('searchtags.html',
                                   message="There are no photos tagged with: " + str(name)[2:-1])
    print('searchTags photopath: ', photopath)
    return render_template('searchtags.html', photopaths= photopath,
                           message="Here are all photos tagged with: " + str(name)[2:-1])


#when one of the top 5 tags is clicked
#return list of photopaths for all photos
@app.route('/searchtags/<tag>', methods = ['GET', 'POST'])
#@flask_login.login_required
def searchtags2(tag):
    photopaths = []
    #returns tuple of all photopaths
    photopath = "SELECT photopath FROM Photos P " \
                "JOIN Has_Tag H on H.photoId = P.photoID JOIN Tags T on T.tagID = H.tagID " \
                "WHERE T.tag = '{0}'".format(tag)
    cursor.execute(photopath)
    photopath = cursor.fetchall()

    # photopath = str(photopath)
    # length = len(photopath)
    # print('lenghth: ', length)
    #
    # for path in range(length):

    print('photopath: ', photopath)
    print('photopath: ', photopath[4:-5])
        # photopath = photopath[3:-3]
        #This is causing photo not to show
    #photopath = photopath[4:-5]
    #photopaths.append(photopath)
    if photopath == '':
        return render_template('searchtags.html',
                                   message="There are no photos tagged with: " + str(tag))
    return render_template('searchtags.html', photopaths= photopath,
                           message="Here are all photos tagged with: " + str(tag))
# def getTaggedPhotos2(tag_word):
#     cursor = conn.cursor()
#     cursor.execute("SELECT p.imgdata, p.photoid FROM Photos p, Has_Tag h, Tags t WHERE h.photoid=p.photoid \
#                     AND h.tagID=t.tagID AND t.tag='{0}'".format(tag_word))
#     return cursor.fetchall()
#
#
# @app.route('/searchtags', methods=['GET', 'POST'])
# def search_tags():
#     tag_word = request.form.get('tags')
#     #return render_template('view_album.html', message="Here are the pictures with the tag", tag=tag_word, tagged=getTaggedPhotos2(tag_word))
#     print('tag:', tag_word)
#     for tag in tag_word:
#         tagged = getTaggedPhotos2(tag)
#         print('tagged: ', tagged)
#         photopath = getPhotoPath(tagged)
#         print('photopath: ', photopath)
#     return render_template('searchtags.html', message="Here are the pictures with the tag", tag=tag_word, tagged=getTaggedPhotos2(tag_word))

@app.route('/like/<photo>', methods=['GET','POST'])
#@flask_login.login_required
def like_photo(photo):
    print('photo: ', photo)
    #get photopath and remove excess characters
    photopath = getPhotoPath(photo)
    print('photopath: ', photopath)
    photopath = str(photopath)
    print('photopath: ', photopath)
    photopath = photopath[4:-5]
    print('photopath: ', photopath)
<<<<<<< HEAD
    users = like_users(photo)       #returns USERNAME ###########################################
=======
    users = like_users(photo)  # returns USERNAME
>>>>>>> 9638fa052cd741f4d550426ae7687871e2420e5e
    print('users who liked: ', users)
    # listusernames =[]
    # for id in users:
    #     print('id: ', str(id)[1:-1])
    #     username = getUsername(str(id)[1:-1])
    #     listusernames.append(username)
    # print('listusernames: ', listusernames)
    # print('like_photo: ', users )
    try:
        try:
            uid = getUserIdFromEmail(flask_login.current_user.id)
        except:
            uid = 1 #anonymous!!!
        cursor=conn.cursor()
        cursor.execute("INSERT INTO Likes (userID, photoID) VALUES ('{0}', '{1}')".format(uid,photo))
        conn.commit()
        users = like_users(photo)  # returns USERNAME
        print('users after insert: ', users)
        return render_template('photo.html',picture=photopath, tags=getTags(photo), likes=getnumlikes(photo), users=users, owner=getPhotoOwner(photo), comments=getPhotoComments(photo), message="Liked!")
    except:
        return render_template('photo.html',picture=photopath, tags=getTags(photo), likes=getnumlikes(photo), users=users, owner = getPhotoOwner(photo), comments=getPhotoComments(photo),message="You've already liked this photo!")

@app.route('/explore')
@flask_login.login_required
def explorepageload():
    return render_template('explore.html')


#like browse page, but photos shouldn't be users...
@app.route('/explore', methods = ['GET','POST'])
@flask_login.login_required
def explore():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    taglist = getUsersTopTags(uid)
    print('taglist: ', taglist)
    try:
        print('test')
        cursor = conn.cursor()
        query = ("SELECT *, S.firstname, S.lastname, Q.name FROM Photos P LEFT JOIN Users S ON P.user_id = S.user_id LEFT JOIN Albums Q ON P.user_id = Q.albumOwner AND P.album_id = Q.albumID")
        cursor.execute(query)
        query = cursor.fetchall()
        print('explore query: ', query)

    except:
        print("couldn't find all tokens")
        return render_template('explore.html', )
    try:
        comments = []
        for each in query:

            comments = [getCommentForPicture(each[0])] + comments
            print("comments :",comments)

    except:
        print("couldn't find all comments")
        print("error")
        return render_template('explore.html',   photopath = query)
    return render_template('explore.html', tags = taglist, photopath = query, comments = comments)


# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welcome to Photoshare')

if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
