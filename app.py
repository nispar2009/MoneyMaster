from flask import Flask, render_template, redirect, request, make_response
import sqlite3
import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    connection = sqlite3.connect('cashco.db')
    cursor = connection.cursor()
    
    if len(list(cursor.execute('SELECT * FROM users WHERE username=?', (request.cookies.get('cashco_user'),)))) > 0:
        return render_template('index.html', user=request.cookies.get('cashco_user'))
    
    return redirect('http://127.0.0.1:5000')

@app.route('/transfer', methods=['POST'])
def transfer():
    connection = sqlite3.connect('cashco.db')
    cursor = connection.cursor()

    money = request.form['money']
    fr = request.cookies.get('cashco_user')
    to = request.form['to']

    if (len(list(cursor.execute('SELECT * FROM users WHERE username=?', fr))) == 1) and (len(list(cursor.execute('SELECT * FROM users WHERE username=?', to))) == 1):
        cursor.execute('UPDATE users WHERE username=? SET balance=balance+?', (to, money))
        cursor.execute('UPDATE users WHERE username=? SET balance=balance-?', (fr, money))
        cursor.execute('INSERT INTO msg (feature, receiver, cnt, date) VALUES (?, ?, ?, ?)', (5001, to, f'Dear user, {fr} has transferred to you an amount of ${money}.', datetime.datetime().utcnow()))
    else:
        return 'Transaction failed. Make sure you are <a href="http://127.0.0.1:5000>logged in</a> and that the recipient of your money exists.'

    connection.commit()
    connection.close()

@app.route('/msg')
def msg():
    connection = sqlite3.connect('cashco.db')
    cursor = connection.cursor()
    
    if len(list(cursor.execute('SELECT * FROM users WHERE username=?', (request.cookies.get('cashco_user'),)))) > 0:
        all_msg = cursor.execute('SELECT cnt FROM msg WHERE receiver=? AND feature=5001', ((request.cookies.get('cashco_user')),))
        return render_template('msg.html', msg=list(all_msg), len=len)

    connection.close()
    
    return redirect('http://127.0.0.1:5000')

app.run(debug=True, port='5001')