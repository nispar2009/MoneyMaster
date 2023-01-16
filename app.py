from flask import Flask, render_template, redirect, request, make_response
import sqlite3
import security

app = Flask(__name__)

connection = sqlite3.connect('moneymaster.db')
cursor = connection.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS users (username text, password text, balance int)')

connection.commit()
connection.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    connection = sqlite3.connect('moneymaster.db')
    cursor = connection.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        login = security.login(username, password)

        if login['user_exists']:
            if login['auth']:
                response = make_response('You are logged in to your account. Click <a href="/">here</a>.')
                response.set_cookie('moneymaster_user', username)
                return response
            else:
                return 'Error: Incorrect password'

        cursor.execute('INSERT INTO users (username, password, balance) VALUES (?, ?, 0)', (username, password))
        connection.commit()
        response = make_response('Your new account has been created. Click <a href="/">here</a>.')
        response.set_cookie('moneymaster_user', username)
        return response

    print(request.cookies.get('moneymaster_user'))

    connection.commit()
    
    if len(list(cursor.execute('SELECT * FROM users WHERE username=?', (request.cookies.get('moneymaster_user'),)))) > 0:
        return render_template('index.html', user=request.cookies.get('moneymaster_user'))
    
    return render_template('login.html')

@app.route('/signout')
def signout():
    response = make_response(f'You are signed out from your previous account ({request.cookies.get("moneymaster_user")}). Click <a href="/">here</a> to log on from another account.')
    response.set_cookie('moneymaster_user', '')
    return response



app.run(debug=True, port='5000')