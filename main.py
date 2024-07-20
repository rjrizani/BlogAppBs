from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy
from datetime import*

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root@127.0.0.1/BlogApp"
db = SQLAlchemy(app)
#pip install mysqlclient
# pip3 install mysql-connector



class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(20))

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/post")
def post():
    return render_template("post.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/contact",methods=['GET','POST'])
def contact():
    if (request.method=='POST'):
        Name = request.form.get('name')
        Email = request.form.get('email')
        Msg = request.form.get('message')
        entry = Contact(name=Name,email=Email, message=Msg, date=datetime.today().date())
        db.session.add(entry)
        db.session.commit()
    return render_template("contact.html")




if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)