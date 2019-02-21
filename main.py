from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(144))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'users_page', 'user_page', 'index', 'blogpost']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['email'] = email
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')
    
    return render_template('newpost.html', owner=owner)

@app.route('/blog', methods=['POST', 'GET'])
def blogpost():

    blog_id = request.args.get('id')

    if blog_id is None:
        blogs = Blog.query.all()
        return render_template('home.html', blogs=blogs)
    
    else:
        blog = Blog.query.get(blog_id)
        return render_template('blog-post.html', blog=blog)

@app.route('/user', methods=['POST', 'GET'])
def user_page():

    blog_id = request.args.get('id')

    if 'user' in request.args:
        user_id = request.args.get('user')
        blogposts = Blog.query.filter_by(owner_id=user_id)
        email = User.query.get(user_id)
        return render_template('singleUser.html', blogposts=blogposts, user_id=user_id, email=email)
    
    if 'id' in request.args:
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        return render_template('blog-post.html', blog=blog, blog_id=blog_id)

    else:
        blogs = Blog.query.all()
        return render_template('home.html', blogs=blogs)
    
@app.route('/', methods=['POST', 'GET'])
def index():        

    blogs = Blog.query.all()

    return render_template('home.html', blogs=blogs)

if __name__ == '__main__':
    app.run()