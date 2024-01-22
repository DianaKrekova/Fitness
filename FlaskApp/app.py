from flask import Flask, render_template, request, redirect, flash, url_for
import mysql.connector
from datetime import datetime
import random


app = Flask(__name__)
app.secret_key = "Fitness"
    
# MySQL configurations
connection = mysql.connector.connect(
        host='127.0.0.1',
        database='diana_db',
        user='root',
        password='root'  
)

@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method=='GET':
        return render_template('reg.html')
    if request.method=='POST':
        _series = request.form['passport_series']
        _number = request.form['passport_number']
        _full_name =  request.form['full_name']
        _phone =  request.form['phone']
        _address =  request.form['address']

        with connection.cursor() as cursor:
        #passport
            cursor.execute("INSERT INTO passport (number, series) VALUES (%s, %s)", (_number, _series))
            connection.commit()
        #fingerprint
            cursor.execute("INSERT INTO fingerprint (Finger) VALUES (%s)", (random.randint(1000000, 9999999),))
            connection.commit()
        #client
            args = [_full_name, _phone, _address]
            cursor.callproc('sp_createClient',args)
            connection.commit()
        return redirect('/membership')

@app.route('/membership', methods=['GET','POST'])
def membership():
    if request.method=='GET':
        return render_template('membership.html')
    if request.method=='POST':
        with connection.cursor() as cursor:
            subscription = request.form.getlist('subscription')
            cursor.callproc('sp_createSale',subscription)
            connection.commit()
            if request.form.get('plan5'):
                cursor.callproc('sp_createSale_2')
                connection.commit()
        return redirect('/select')

@app.route('/select', methods=['GET','POST'])
def select():
    if request.method=='GET':
        return render_template('select.html')
    if request.method=='POST':
        _start_time = datetime.strptime(request.form['start-time'],'%H:%M')
        _end_time = datetime.strptime(request.form['end-time'],'%H:%M')
        _coach = request.form['coach']
        _service = request.form['service']
        _zone = request.form['zone']
        _training = request.form['training']
        if (_zone == 2):
            _zone = random.randint(2, 3)
        if (_training != 1):
            _group = random.randint(1, 4)
        with connection.cursor() as cursor:
            args = [_start_time.time(),_end_time.time(),_coach,_service,_zone,_training, _group]
            check = 1
            cursor.execute("SELECT sp_checkTraining(%s, %s, %s, %s)", (_start_time.time(),_end_time.time(),_training,_coach))
            check = cursor.fetchone()
            if check[0]:
                cursor.callproc('sp_createSch', args)
                connection.commit()
                return redirect(url_for("result"))
            else: 
                flash("Это вермя занято или некорректно, выберите другого тренера или время.")
                return redirect(url_for("select"))                                                                                                                                    

@app.route('/result',methods=['GET','POST'])
def result():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM client_pay where id_client = (select max(id_client) from client)")
        pay = cursor.fetchall()
        connection.commit()
        cursor.execute("SELECT * FROM client_schedule where id_client = (select max(id_client) from client)")
        clsch = cursor.fetchall()
        connection.commit()
    return render_template('result.html', pay=pay, clsch=clsch)


@app.route("/schedule", methods=['GET', 'POST'])
def schedule():
    if request.method=='GET':
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM schedule_fitness_admin")
            sch = cursor.fetchall()
            connection.commit()
        return render_template('schedule.html', sch=sch)
    if request.method=='POST':
        _id = request.form['id']
        _name = request.form['name']
        _coach = request.form['coach']
        _zone = request.form['zone']
        if (_zone == 2):
            _zone = random.randint(2, 3)
        with connection.cursor() as cursor:
            if (_id==0  or _coach=="" or _zone=="") and _name!="":
                cursor.execute("SELECT * FROM schedule_fitness_admin WHERE id_visit = %s or Full_name LIKE CONCAT('%',%s, '%') or Full_name_coach = %s or Name_type = %s", (_id,_name,_coach,_zone))
                sch_s = cursor.fetchall()
                connection.commit()
                return render_template('schedule.html', sch=sch_s)
            if (_id=="" or _name=="") and _coach=="" and _zone=="":
                cursor.execute("SELECT * FROM schedule_fitness_admin WHERE id_visit = %s or (Full_name_coach = %s and Name_type = %s)", (_id,_coach,_zone))
                sch_s = cursor.fetchall()
                connection.commit()
                return render_template('schedule.html', sch=sch_s)
            if (_id=="" or _name=="") and _coach!="" or _zone!="":
                cursor.execute("SELECT * FROM schedule_fitness_admin WHERE id_visit = %s or Full_name_coach = %s or Name_type = %s", (_id,_coach,_zone))
                sch_s = cursor.fetchall()
                connection.commit()
                return render_template('schedule.html', sch=sch_s)
            if _id!=0 and _name!="" and _coach!="" and _zone!="":
                cursor.execute("SELECT * FROM schedule_fitness_admin WHERE id_visit = %s and Full_name LIKE CONCAT('%',%s, '%') and Full_name_coach = %s and Name_type = %s", (_id,_name, _coach,_zone))
                sch_s = cursor.fetchall()
                connection.commit()
                return render_template('schedule.html', sch=sch_s)


    
    
@app.route('/update/<int:id>',methods = ['GET','POST'])
def update(id):
    if request.method == 'GET':
        with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM schedule_fitness_admin WHERE id_visit = %s", (id,))
                sch = cursor.fetchall()
                connection.commit()
                cursor.execute("SELECT schedule.id_coach, schedule.id_service,schedule.id_zone, schedule.id_training  FROM visit join schedule using(id_entry) WHERE id_visit = %s", (id,))
                id_m = cursor.fetchall()
                if id_m[0][2] == 3:
                     id_m[0][2] == 2
        return render_template("add.html", sch = sch, id_m=id_m)
    if request.method == 'POST':
        _name = request.form['name']
        _start_time = datetime.strptime(request.form['start-time'],'%H:%M')
        _end_time = datetime.strptime(request.form['end-time'],'%H:%M')
        _coach = request.form['coach']
        _service = request.form['service']
        _zone = request.form['zone']
        _training = request.form['training']
        if (_zone == 2):
            _zone = random.randint(2, 3)
        if (_training != 1):
            _group = random.randint(1, 4)
        with connection.cursor() as cursor:
            args = [id, _name,_start_time.time(),_end_time.time(),_coach,_service,_zone,_training, _group]
            check = [1]
            cursor.execute("SELECT sp_checkTraining_up(%s, %s, %s, %s, %s)", (_start_time.time(),_end_time.time(),_training,_coach,id))
            check = cursor.fetchone()
            print(check)
            if check[0] and _start_time.time()<_end_time.time():
                cursor.callproc('sp_updateAll', args)
                connection.commit()
                return redirect('/schedule')
            else: 
                flash("Это вермя занято или некорректно, выберите другого тренера или время.")
                return redirect(url_for('update', id=id))

@app.route('/delete/<int:id>')
def delete(id):
    with connection.cursor() as cursor:
        cursor.callproc('sp_deleteAll', (id,))
        connection.commit()
    return redirect('/schedule')


if __name__ == '__main__':
    app.run(debug=True)