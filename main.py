from flask import Flask, render_template,request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from datetime import*
import json
import math

app = Flask(__name__)

with open('config.json', 'r') as c:
    param = json.load(c)["parameters"]

if param["local_server"]:
    app.config['SQLALCHEMY_DATABASE_URI'] = param["local_url"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = param["prod_url"]

SECRET_KEY = param["secret_key"]

app.config['SECRET_KEY']

db = SQLAlchemy(app)
#pip install mysqlclient
# pip3 install mysql-connector



class Contact(db.Model):
    sno = db.Column('sno',db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(20))

class Posts(db.Model):
    post_id = db.Column('post_id',db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    sub_title = db.Column(db.String(200))
    location = db.Column(db.String(50))
    author = db.Column(db.String(30))
    date_posted = db.Column(db.Date)
    image = db.Column(db.String(150))
    content_1= db.Column(db.Text)
    content_2 = db.Column(db.Text)
    slug = db.Column(db.String(100), unique=True)

@app.route("/")
def home():
    db.session.commit()
    post_data = Posts.query.all()
    n = 2
    last = math.ceil(len(post_data)/n)
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    j = (page-1)*n
    posts = post_data[j:j+n]

    if page == 1:
        prev = "#"
        next = "/?page="+str(page+1)
    elif page == last:
        prev = "/?page="+str(page-1)
        next = "#"
    else:
        prev = "/?page="+str(page-1)
        next = "/?page="+str(page+1)


    return render_template("index.html", posts=posts, param=param, prev=prev, next=next)


@app.route("/post/<slug>", methods=['GET'])
def post(slug):
    single_post = Posts.query.filter_by(slug=slug).first()
    return render_template("post.html", post=single_post,param=param)

@app.route("/about")
def about():
    return render_template("about.html", param=param)

@app.route("/login")
def login():
    return render_template("login.html", param=param)

@app.route("/contact",methods=['GET','POST'])
def contact():
    if (request.method=='POST'):
        Name = request.form.get('name')
        Email = request.form.get('email')
        Msg = request.form.get('message')
        entry = Contact(name=Name,email=Email, message=Msg, date=datetime.today().date())
        db.session.add(entry)
        db.session.commit()
    return render_template("contact.html", param=param)

@app.route("/admin",methods=['GET', 'POST'])
def dashboard():
    posts = Posts.query.filter_by().all()
    contacts = Contact.query.filter_by().all()
    return render_template("admin/index.html", param=param, posts=posts, contacts=contacts)


@app.route("/edit")
def edithtml():
    return render_template("admin/editPost.html", param=param)





if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8080)