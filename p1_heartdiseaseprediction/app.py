from flask import Flask, render_template, request, redirect, session, url_for
from sqlite3 import *
from flask_mail import Mail, Message
from random import randrange
import pickle
import smtplib, ssl

app = Flask(__name__)
app.secret_key = "finalyearproject"
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'projectgroup8.srms@gmail.com'
app.config['MAIL_PASSWORD'] = 'goloavprdgpuolxa'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


mail = Mail(app)

@app.route("/")
def home():
	if 'username' in session:
		return render_template("home.html", name = session['username'])
	else:
		return redirect(url_for('signup'))

@app.route("/find")
def find():
	if 'username' in session:
		return render_template("find.html", name = session['username'])
	else:
		return redirect(url_for('home'))

@app.route("/check", methods = ["POST"])
def check():
	if request.method == "POST":
		if 'username' in session:
			name = session['username']
		age = float(request.form["age"])
		gender = str(request.form["gender"])
		r1 = request.form["r1"]
		if r1 == "1":
			cp = 1
		elif r1 == "2":
			cp = 2	
		elif r1 == "3":
			cp = 3
		else:
			cp = 4
		BP = float(request.form["BP"])
		CH = float(request.form["CH"])
		maxhr = float(request.form["maxhr"])
		STD = float(request.form["STD"])
		fluro = float(request.form["fluro"])
		Th = float(request.form["Th"])
		d = [[age, cp, BP, CH, maxhr, STD, fluro, Th]]	
		con = None
		try:
			con = connect("group8.db")
			cursor = con.cursor()
			sql = "insert into heartdb values('%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s')"
			con.execute(sql % (str(age), str(gender),str(cp), str(BP), str(CH), str(maxhr), str(STD), str(fluro), str(Th)))
			con.commit()
		except Exception as e:
			print(e)
		with open("heartdiseaseprediction.model", "rb") as f:
			model = pickle.load(f)	
		res = model.predict(d)
		return render_template("find.html", msg = res[0], name = session['username'])	
	else:
		return render_template("home.html")

@app.route("/signup", methods = ["GET", "POST"])
def signup():
	if request.method == "POST":
		em = request.form["em"]
		un = request.form["un"]
		pw = ""
		text = "0123456789"
		for i in range(6):
			pw = pw + text[randrange(len(text))]
		print(pw)
		msg = Message("Welcome to HeartDiseasePrediction", sender = "heartdiseasepredictorml@outlook.com", recipients = [em])
		msg.body = "Greetings from HeartDiseasePredictor! Your password is " + str(pw)
		mail.send(msg)
		con = None
		try:
			con = connect("group8.db")
			cursor = con.cursor()
			sql = "insert into user values('%s', '%s')"
			con.execute(sql % (un, pw))
			con.commit()
			return render_template("login.html", msg = "Password has been mailed to you")
		except Exception as e:
			con.rollback()
			return render_template("signup.html", msg = "User already exists" + str(e))
	else:
		return render_template("signup.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
	if request.method == "POST":
		un = request.form["un"]
		pw = request.form["pw"]
		con = None
		try:
			con = connect("group8.db")
			cursor = con.cursor()
			sql = "select * from user where username = '%s' and password = '%s'"
			cursor.execute(sql % (un,pw))
			data = cursor.fetchall()
			if len(data) == 0:
				return render_template("login.html", msg = "invalid login")
			else:	
				session['username'] = un
				return redirect( url_for('home'))
		
		except Exception as e:
			msg = "Issue " + str(e)
			return render_template("login.html", msg = msg)
	else:
		return render_template("login.html")

@app.route("/forgot", methods = ["GET", "POST"])
def forgot():
	if request.method == "POST":
		un = request.form["un"]
		em = request.form["em"]
		con = None
		try:
			con = connect('group8.db')		
			cursor = con.cursor()
			sql = "select * from user where username = '%s'"
			cursor.execute(sql % (un))
			data = cursor.fetchall()
			if len(data) == 0:
				return render_template("forgot.html", msg = "invalid login")
			else:	
				session['username'] = un
				pw1 = ""
				text = "0123456789"
				for i in range(6):
					pw1 = pw1 + text[randrange(len(text))]
				print(pw1)
				msg = Message("Hello again from HeartDiseasePrediction", sender = "heartdiseasepredictorml@outlook.com", recipients = [em])
				msg.body = "Greetings from HeartDiseasePredictor! Seems like you forgot your password. Your new password is " + str(pw1)
				mail.send(msg)
				try:
					con = connect("group8.db")
					cursor = con.cursor()
					sql = "update user set password = '%s' where username = '%s'"
					con.execute(sql % (pw1, un))
					con.commit()
					return render_template("login.html", msg = "Password has been mailed to you")
				except Exception as e:
					con.rollback()
					return render_template("forgot.html", msg = "Some Issue: " + str(e))
		except Exception as e:
			msg = "Issue " + str(e)
			return render_template("forgot.html", msg = msg)	
	else:
		return render_template("forgot.html")			

@app.route("/logout", methods = ["POST"])
def logout():
	session.clear()	
	return redirect(url_for("login"))

if __name__ == "__main__":
	app.run(debug = True)
