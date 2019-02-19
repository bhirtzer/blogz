from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(144))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Blog %r>' % self.title

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        new_post = Blog(title, body)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')
    
    return render_template('newpost.html')

@app.route('/blog', methods=['POST', 'GET'])
def blogpost():

    blog_id = request.args.get('id')

    if blog_id is None:
        blogs = Blog.query.all()
        return render_template('home.html', blogs=blogs)
    
    else:
        blog = Blog.query.get(blog_id)
        return render_template('blog-post.html', blog=blog)
    
     
@app.route('/', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all()

    return render_template('home.html', blogs=blogs)

if __name__ == '__main__':
    app.run()