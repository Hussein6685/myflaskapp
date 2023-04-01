from flask import Flask, render_template, flash, redirect, url_for,session, request, logging
#from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps 
app = Flask(__name__)
app.secret_key='secret123'

#contig MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '4476'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#init MYSQL
mysql = MySQL(app)

#Articles = Articles()
# Index
@app.route('/')
def index():
    return render_template('home.html')
# About
@app.route('/about')
def about():
    return render_template('about.html')
1
#Articles
@app.route('/articles')
def articles():
       # Create cursor
    cur = mysql.connection.cursor()
    #get articles
    result = cur.execute('SELECT * FROM articles')
    article = cur.fetchall()
    if result > 0:
        return render_template('article.html', articles = articles)
    else:
        msg = 'NO Articles Found'
        return render_template('articles.html', msg=msg)
    #close connection
    cur.close()
#Single Article
@app.route('/article/<string:id>/')
def article(id):
           # Create cursor
    cur = mysql.connection.cursor()
    #get article
    result = cur.execute('SELECT * FROM articles WHERE id = %s', [id])
    article = cur.fetchone()

    return render_template('Article.html', article=article)
 # Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username  = StringField('userName', [validators.length(min=4, max=25)])
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='passwords do not match')
    ])
    confirm = PasswordField('confirm password')
    #User Register
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # create cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))


        #commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You are now registered and can long in', 'success')


    return render_template('register.html', form=form)    
# user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #get form fields
        username = request.form['username']
        password_candidate = request.form['password']
        #create cursor
        cur = mysql.connection.cursor()

        # get user by username
        result = cur.execute('SELECT * FROM users WHERE username = %s', [username])
        
        if result > 0:
            #get stored hash
            data = cur.fetchone()
            password = data['password']

            # compare passwords
            if sha256_crypt.verify(password_candidate,password):
                #passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error = error )
            # close connection
            cur.close()
            
    else:
        error = 'Username not found'
        return render_template('login.html', error = error)
    
    return render_template('login.html')
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
             flash('Unauthorized, Please login', 'danger')
             return redirect(url_for('login'))
    return  wrap       

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'succes')
    return redirect(url_for('login'))
#Dashbaord
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()
    #get articles
    result = cur.execute('SELECT * FROM articles')
    article = cur.fetchall()
    if result > 0:
        return render_template('dashboard.html', articles = articles)
    else:
        msg = 'NO Articles Found'
        return render_template('dashboard.html', msg=msg)
    #close connection
    cur.close()

 # Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = StringField('body', [validators.length(min=30)])


#Add Article
@app.route('/add_article', methods= ['GET', 'POST'])

@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        #Create Cursor
        cur = mysql.connection.cursor()

        #Execute
        cur.execute('INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)',(title, body, session['username']))
        #Ccommit to DB
        mysql.connection.commit()

        #Close connecion 
        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form = form )


#Edit Article
@app.route('/Edit_article<string:id>', methods= ['GET', 'POST'])
@is_logged_in
def edit_article(id):
    #Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute("SELECT * FROM articles where id = %s", [id])

    article = cur.fetchone()

    #Get form
    form = ArticleForm(request.form)


    #form.title.data = article['title']
    form.body.data = article[body]



    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        #Create Cursor
        cur = mysql.connection.cursor()

        #Execute
        cur.execute ("UPDATE articles SET title=%s, body=%s, WHERE id = %s", ( title , body, id))
        #Ccommit to DB
        mysql.connection.commit()

        #Close connecion 
        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form = form )

#Delete Article
@app.route('/delete_article/<string:id>', method=['POST'])
@is_logged_in
def delete_article(id):
    #Create cursor
    cur = mysql.connection.cursor()

    #Execute
    cursor.execute("DELETE FROM articles WHRE id = %s", [id])
    
    
    #Ccommit to DB
    mysql.connection.commit()
    #Close connecion 
    cur.close()

if __name__ == '__main__':
    app.run(debug=True)
