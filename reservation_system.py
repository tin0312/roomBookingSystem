from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import re
import pymysql
import email.utils
import datetime
import os
from user import setUser, login_required, admin_required
from db import Database

app = Flask(__name__, template_folder='templates', static_folder='resources')
app.secret_key = os.urandom(24)
db = Database()


def getMD5(pwd):
    pwd = pwd.encode('ascii')  # ascii  utf-8
    result = hashlib.md5(pwd).hexdigest()
    return result


def is_valid_email(email_str):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email_str):
        return False
    email_address = email.utils.parseaddr(email_str)[1]
    if not email.utils.formataddr((email_address, email_address)):
        return False
    return True


@app.route('/')
def login():
    return render_template('login.html')


@ app.route('/adminlogin')
def adminlogin():
    return render_template('adminLogin.html')


@ app.route('/adminlogin_validation', methods=['POST'])
def adminlogin_validation():
    username = request.form.get('username')
    password = getMD5(request.form.get('password'))
    param = (username, password)
    sql = "SELECT * FROM adminaccount WHERE username LIKE %s AND password LIKE %s"
    db.cur.execute(sql, param)
    users = db.cur.fetchall()

    if len(users) == 0:
        errorMsg = "Incorrect Username or Password"
        return render_template('adminLogin.html', errorMsg=errorMsg)
    else:
        now = datetime.datetime.now()
        timenowSql = now.strftime('%Y-%m-%d %H:%M:%S')
        user = users[0]
        firstname, lastname, username = user['firstname'], user['lastname'], user['username']
        setUser(user, 'admin')
        return redirect(url_for('adminhome', firstname=firstname, lastname=lastname, username=username, timenowSql=timenowSql))


@ app.route('/userlogin_validation', methods=['POST'])
def userlogin_validation():

    username = request.form.get('username')
    password = getMD5(request.form.get('password'))
    param = (username, password)
    sql = "SELECT * FROM useraccount WHERE username LIKE %s AND password LIKE %s"
    db.cur.execute(sql, param)
    users = db.cur.fetchall()
    if len(users) == 0:
        errorMsg = "Incorrect Username or Password"
        return render_template('login.html', errorMsg=errorMsg)
    else:
        user = users[0]
        setUser(user, 'student')
        return redirect(url_for('userhome'))


@ app.route('/userregistration')
def userregister():
    return render_template('userRegister.html')


@ app.route('/add_user', methods=['POST'])
def adduser():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    username = request.form.get('username')
    password = getMD5(request.form.get('password'))
    email = request.form.get('email')
    status = request.form.get('status')
    emailCheck = is_valid_email(email)
    param = (firstname, lastname, username, password, email, status)
    sql = "INSERT INTO `useraccount` (`firstname`,`lastname`,`username`,`password`,`email`,`status`) VALUES (%s,%s,%s,%s,%s,%s)"
    if emailCheck == True:
        try:
            db.cur.execute(sql, param)
            db.cur.commit()
        except pymysql.connector.Error as error:
            errorMsg = error
            return render_template('userRegister.html', errorMsg=errorMsg)
        else:
            okMsg = "User Registration was Successfull"
            return render_template('userRegister.html', okMsg=okMsg)
    else:
        errorMsg = "Incorrect Email"
        return render_template('userRegister.html', errorMsg=errorMsg)


@ app.route('/adminregistration')
def adminregister():
    return render_template('adminRegister.html')


@ app.route('/add_admin', methods=['POST'])
def addadmin():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    username = request.form.get('username')
    password = getMD5(request.form.get('password'))
    email = request.form.get('email')
    emailCheck = is_valid_email(email)

    param = (firstname, lastname, username, password, email,)
    sql = "INSERT INTO `adminaccount` (`firstname`,`lastname`,`username`,`password`,`email`) VALUES (%s,%s,%s,%s,%s)"
    if emailCheck == True:
        try:
            db.cur.execute(sql, param)
            db.cur.commit()
        except pymysql.connector.Error as error:
            errorMsg = error
            return render_template('adminRegister.html', errorMsg=errorMsg)
        else:
            okMsg = "Admin Registration was Successfull"
            return render_template('adminRegister.html', okMsg=okMsg)
    else:
        errorMsg = "Incorrect Email"
        return render_template('adminRegister.html', errorMsg=errorMsg)
    db.cur.connect()


@ app.route('/userhome')
@login_required
def userhome(user):
    firstname, lastname, username = user['firstname'], user['lastname'], user['username']
    _, reservations = db.get_reservations(username)
    return render_template('userHome.html', firstname=firstname, lastname=lastname, username=username, reservations=reservations)


@ app.route('/adminhome')
@ admin_required
def adminhome(user):
    if 'username' in session:
        firstname, lastname, username = user['firstname'], user['lastname'], user['username']
        _, content = db.get_all_reservations()
        return render_template('adminHome.html', firstname=firstname, lastname=lastname, username=username, content=content)
    else:
        return redirect(url_for('adminlogin'))


@ app.route('/adminlogout')
def adminlogout():
    session.clear()
    return redirect(url_for('adminlogin'))


@ app.route('/userlogout')
def userlogout():
    session.clear()
    return redirect(url_for('login'))


@ app.route('/reservation', methods=['GET', 'POST'])
@login_required
def reservation(user):
    success, rooms = db.get_all_rooms()
    if not success:
        return render_template('reservation.html', errorMsg=rooms)

    reservation_id = request.args.get('id')
    if request.method == 'POST':
        data = request.form
        date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
        roomNo = data['room-number']
        startTime = datetime.datetime.strptime(
            data['start-time'], '%H:%M').time()
        endTime = datetime.datetime.strptime(data['end-time'], '%H:%M').time()
        occupancy = data['occupancy']

        if reservation_id:
            success, data = db.modify_reservation(
                reservation_id, roomNo, startTime, endTime, date, occupancy, user['username'])
        else:
            success, data = db.make_reservation(
                roomNo, startTime, endTime, date, occupancy, user['username'])
        if success:
            return redirect(url_for('userhome'))
        else:
            return render_template('reservation.html', reservation=None, rooms=rooms, errorMsg=data)
    if reservation_id:
        success, data = db.get_reservation(reservation_id)
        if not success:
            return redirect(url_for('userhome'))
        data['start_time'] = str(data['start_time'])[:5]
        data['end_time'] = str(data['end_time'])[:5]
        return render_template('reservation.html', reservation=data, rooms=rooms)
    return render_template('reservation.html', reservation=None, rooms=rooms)


# route for admin add reservation for a selected user & modify reservation
@ app.route('/adreservation', methods=['GET', 'POST'])
@ admin_required
def adreservation(user):
    success, rooms = db.get_all_rooms()
    if not success:
        return render_template('adreservation.html', errorMsg=rooms)

    reservation_id = request.args.get('id')
    if request.method == 'POST':
        data = request.form
        date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
        roomNo = data['room-number']
        startTime = datetime.datetime.strptime(
            data['start-time'], '%H:%M').time()
        endTime = datetime.datetime.strptime(data['end-time'], '%H:%M').time()
        occupancy = data['occupancy']
        username = data['username']

        if reservation_id:
            success, data = db.admin_modify_reservation(
                reservation_id, roomNo, startTime, endTime, date, occupancy, username)
        else:
            success, data = db.make_reservation(
                roomNo, startTime, endTime, date, occupancy, username)
        if success:
            return redirect(url_for('adminhome'))
        else:
            return render_template('adreservation.html', reservation=None, rooms=rooms, errorMsg=data)

    success, users = db.get_all_users()

    if not success:
        return render_template('adreservation.html', errorMsg=users)

    if reservation_id:
        success, data = db.get_reservation(reservation_id)
        if not success:
            return redirect(url_for('adminhome'))
        data['start_time'] = str(data['start_time'])[:5]
        data['end_time'] = str(data['end_time'])[:5]
        return render_template('adreservation.html', reservation=data, rooms=rooms, users=users)

    return render_template('adreservation.html', reservation=None, rooms=rooms, users=users)


@ app.route('/cancel/<int:reservation_id>', methods=['GET'])
@login_required
def cancel(user, reservation_id):
    success, data = db.cancel_reservation(reservation_id, user['username'])
    if success:
        return redirect(url_for('userhome'))
    else:
        flash(data)
        return redirect(url_for('userhome'))

# route for admin to cancel reservation


@ app.route('/adcancel/<int:reservation_id>', methods=['GET'])
@ admin_required
def adcancel(user, reservation_id):
    success, data = db.admin_cancel_reservation(reservation_id)
    if success:
        return redirect(url_for('adminhome'))
    else:
        flash(data)
        return redirect(url_for('adminhome'))
