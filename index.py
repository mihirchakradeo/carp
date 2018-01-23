from flask import Flask, request, render_template
import matplotlib.pyplot as plt
#from flask_mysqldb import MySQL
from flaskext.mysql import MySQL
import smtplib
import string
import random
import hashlib

a=[]

import random
import time

app = Flask(__name__)

import tensorflow as tf
import numpy as np


learn=tf.contrib.learn

tf.logging.set_verbosity(tf.logging.ERROR)

mnist=learn.datasets.load_dataset('mnist')

data=mnist.train.images
labels=np.asarray(mnist.train.labels,dtype=np.int32)
#print labels
test_data=mnist.test.images
test_labels=np.asarray(mnist.test.labels,dtype=np.int32)

max_examples=10000
data=data[:max_examples]
labels=labels[:max_examples]
'''
OLD METHOD TO CONNECT TO MYSQL
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MSQL_PASSSWORD'] = ''
app.config['MYSQL_DB'] = ''
mysql = MySQL(app)
'''

#NEW METHOD TO CONNECT TO MYSQL
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = ''
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = ''
app.config['MYSQL_DATABASE_HOST'] = ''
mysql.init_app(app)


def randomImageGenerator(t):
	

	randomArray = []
	global a
	for x in xrange(36):
		randomArray.append(random.randint(0,1796))
		a.append(0)

	print "Starting to plot"
	for i in xrange(0,36):
		#print randomArray[i]
		plt.subplot(6,6,i+1)
		plt.imshow(test_data[randomArray[i]].reshape((28,28)), cmap=plt.cm.gray_r, interpolation="nearest")
		a[i] = (test_labels[randomArray[i]])
		print "Plotted image %s"%i

	print "Saving svg"

	plt.savefig("static/"+t+".png", size=(800, 600), dpi=1200)

	print a


@app.route('/')
def index():
	return render_template('index-bootstrap.html')


#redirect here from zxcv html
@app.route('/result', methods=['POST', 'GET'])
def result():
	if request.method == 'POST':
		result = request.form
		return render_template("result.html", result = result)


@app.route('/login')
def login():
	print "Calling function"
	t = time.time()
	t= str(t)
	randomImageGenerator(t)
	print "DONE"
	return render_template("login-bootstrap.html", t=t)


#tablewithvalues html (after completing test)
@app.route('/complete')
def complete():

	#initializing mysql connection
	
	
	#OLD METHOD
	#cur = mysql.connection.cursor()
	#cur.execute('''SELECT login from default_user_table WHERE id=1''')
	#rv = cur.fetchall()
	#rv = str(rv)
	
	
	#NEW METHOD
	conn = mysql.connect()
	cur =conn.cursor()
	cur.execute('''SELECT login from default_user_table WHERE id=1''')
	rv = cur.fetchone()
	print rv
	
	return render_template('tablewithvalues.html', rv=rv)


@app.route('/dashboardprompt')
def dashboardprompt():
	return render_template('dashboardlogin-bootstrap.html')


@app.route('/dashboardlogin', methods=['POST','GET'])
def dashboardlogin():

	username = request.form['username']
	password = request.form['password']


	#write logic to check mysql entry here
	conn = mysql.connect()
	cur =conn.cursor()
	
	hash_object = hashlib.sha1(password)
	hex_dig = hash_object.hexdigest()
	print "Calculated ",hex_dig


	cur.execute("select password from default_user_table where login='%s'"%(username))
	res = cur.fetchone()
	res = str(res[0])
	print "Retrieved ",res

	if res==hex_dig:

		print "Success"
		#get sem and theta, send sem and theta to tablewithvalues
		cur.execute("select dr.sem,dr.theta from default_cat_response_table as dr where (dr.session_id = (select concat('i',(select convert((select ds.internal_id from default_session_table as ds where (ds.user_id = (select du.id from default_user_table as du where du.login='%s')) ORDER BY ds.id DESC LIMIT 1),CHAR(225)))))COLLATE utf8_unicode_ci) ORDER BY id DESC LIMIT 1"%(username))
		res = cur.fetchone()
		print res[0] #sem
		print res[1] #theta
		theta = res[1]
		sem = res[0]

		
		if (theta >= -2 and theta < -1.2):
			print "Inside case 1"
			randomNum = random.randint(0,9)
			fun = 'x+%s'%(randomNum)

		elif (theta >= -1.2 and theta < -0.4):
			print "Inside case 2"
			randomNum = random.randint(0,99)
			fun = 'x+%s'%(randomNum)

		elif (theta >= -0.4 and theta < 0.4):
			print "Inside case 3"
			randomNum = random.randint(0,9)
			fun = 'x*%s'%(randomNum)
			
		elif (theta >= 0.4 and theta < 1.2):
			print "Inside case 4"
			randomNum = random.randint(0,9)
			fun = 'x*x+%s'%(randomNum)

		elif (theta >= 1.2 and theta < 3.0):
			print "Inside case 5"
			randomNum = random.randint(0,9)
			fun = 'x*x+2*x+%s'%(randomNum)

		#print "Function ",fun
		return render_template('dashboard-bootstrap.html',username=username, fun=fun, hex_dig=hex_dig)
		

	else:
		print "Failed"
		return '<h1>Invalid Details, try again</h1>'



	#QUERY:
	#select dr.sem,dr.theta from default_cat_response_table as dr where (dr.session_id = (select concat('i',(select convert((select ds.internal_id from default_session_table as ds where (ds.user_id = (select du.id from default_user_table as du where du.login='admin')) ORDER BY ds.id DESC LIMIT 1),CHAR(225)))))COLLATE utf8_unicode_ci) ORDER BY id DESC LIMIT 1;


	#cur.execute('''select dr.sem,dr.theta from default_cat_response_table as dr where (dr.session_id = (select concat('i',(select convert((select ds.internal_id from default_session_table as ds where (ds.user_id = (select du.id from default_user_table as du where du.login='admin')) ORDER BY ds.id DESC LIMIT 1),CHAR(225)))))COLLATE utf8_unicode_ci) ORDER BY id DESC LIMIT 1''')
	
	#cur.execute('''SELECT login from default_user_table WHERE id=1''')
	#rv = cur.fetchone()

	#statically checking just for demo purpose


@app.route('/createnew', methods=['POST', 'GET'])
def createnew():
	if request.method == 'POST':
		username = request.form['username']
		rowcol = request.form['textarea_cell']
		fun = request.form['textarea_fn']
		n=6
		#processing row col
		print rowcol

		rowcol = str(rowcol)

		rc = rowcol.split(',')

		print "RC %s %s"%(rc[0],rc[1])


		loc = int(rc[0])*n + int(rc[1])


		conn = mysql.connect()
		cur =conn.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS processed_table(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, username VARCHAR(40) UNIQUE, location INT NOT NULL, fun VARCHAR(10))")

		print "%s %s %s"%(username, loc, fun)

		cur.execute("DELETE FROM processed_table WHERE username='%s'"%username)

		cur.execute("INSERT INTO processed_table (username,location,fun) VALUES ('%s', %d, '%s')"%(username,loc,fun))
		conn.commit()
		 
		#fun = result['textarea_fn']
		#password = result['res']
		#rowcol = result['textarea_cell']
		#return "<h1>{{username}} {{fun}} {{password}} {{rowcol}}</h1>"
		return render_template('index-bootstrap.html')



@app.route('/testlogin', methods=['GET', 'POST'])
def testlogin():
	if request.method == 'POST':
		global a
		username = request.form['username']
		password = request.form['password']
		password = int(password)
		#a = request.form['a']
		#a = str(a)
		#a = a.split(',')
		print '----------------------------------------'
		print a
		conn = mysql.connect()
		cur =conn.cursor()
		cur.execute("SELECT location, fun FROM processed_table WHERE username='%s'"%(username))
		res = cur.fetchone()

		#getting the number at location
		ans = a[res[0]]
		x = ans
		expr = res[1]
		s = eval(expr)

		print "PASSWORD %s ANSWER CALC %s"%(password, s)

		if int(password)==int(s):
			return render_template("loggedin-bootstrap.html",username=username,password=password,s=s)

		elif int(password)!=int(s):
			return render_template("incorrect.html",username=username,password=password,s=s)


@app.route('/api')
def api():
	return render_template('api.html')


@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/forgotpassword')
def forgotpassword():
	return render_template('forgotpasswordclicked.html')

@app.route('/forgotpassword2', methods=["POST","GET"])
def forgotpassword2():
	username = request.form['username']
	conn = mysql.connect()
	cur =conn.cursor()
	cur.execute("SELECT email FROM default_user_table WHERE login='%s'"%(username))
	res = cur.fetchone()
	sendNewPassword(res,username)
	return render_template("dashboardlogin-bootstrap.html")


def sendNewPassword(email,username):

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login("", "")
	password = str(id_generator())
	print "INSIDE SENDNEWPASSWORD: ",password
	#storing new password into table
	hash_object = hashlib.sha1(password)
	hex_dig = hash_object.hexdigest()
	print hex_dig
	conn = mysql.connect()
	cur =conn.cursor()
	cur.execute("UPDATE default_user_table SET password = '%s' WHERE login='%s'"%(hex_dig, username))
	conn.commit()

	server.sendmail("", email, password)
	server.quit()
	return

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

if __name__=="__main__":
	app.run(debug=True, port=8000)
