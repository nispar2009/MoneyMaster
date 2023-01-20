from flask import Flask, render_template, redirect, request
import sqlite3

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    connection = sqlite3.connect('cashco.db')
    cursor = connection.cursor()
    
    if len(list(cursor.execute('SELECT * FROM users WHERE username=?', (request.cookies.get('cashco_user'),)))) > 0:
        return render_template('index.html', user=request.cookies.get('cashco_user'), balance=(list(cursor.execute('SELECT * FROM users WHERE username=?', (request.cookies.get('cashco_user'),))))[0][2])
    
    return redirect('http://127.0.0.1:5000')

@app.route('/transfer', methods=['POST'])
def transfer():
    connection = sqlite3.connect('cashco.db')
    cursor = connection.cursor()

    money = int(request.form['money'])
    fr = request.cookies.get('cashco_user')
    to = request.form['to']

    if (len(list(cursor.execute('SELECT * FROM users WHERE username=?', (fr,)))) == 1) and (len(list(cursor.execute('SELECT * FROM users WHERE username=?', (to,)))) == 1):
        cursor.execute('UPDATE users SET balance=balance+? WHERE username=?', (money, to))
        cursor.execute('UPDATE users SET balance=balance-? WHERE username=?', (money, fr))
        cursor.execute('INSERT INTO msg (feature, receiver, cnt) VALUES (5001, ?, ?)', (to, (f'Dear user, {fr} has transferred to you an amount of ${money}.')))
        cursor.execute('INSERT INTO msg (feature, receiver, cnt) VALUES (5001, ?, ?)', (fr, (f'Dear user, an amount of ${money} has been transferred from your account to {to}.')))
        print(list(cursor.execute('SELECT * FROM msg')))   
        connection.commit()
        connection.close()
    else:
        return 'Transaction failed.'

    return redirect('/')

@app.route('/msg')
def msg():
    connection = sqlite3.connect('cashco.db')
    cursor = connection.cursor()
    
    if len(list(cursor.execute('SELECT * FROM users WHERE username=?', (request.cookies.get('cashco_user'),)))) > 0:
        all_msg = list(cursor.execute('SELECT * FROM msg WHERE feature=5001 AND receiver=?', ((request.cookies.get('cashco_user')),)))
        print(all_msg)
        print(list(cursor.execute('SELECT * FROM msg')))
        return render_template('msg.html', all_msg=all_msg, len1=len)
    connection.close()
    return redirect('http://127.0.0.1:5000')

app.run(debug=True, port='5001')