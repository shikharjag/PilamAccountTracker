#from flask import request, redirect
from flask import Flask
from flask import request, redirect
from flask import render_template, session
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('PLP Bills-5644a9b3a0f7.json', scope)
client = gspread.authorize(creds)



app = Flask(__name__)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'



def verify_password(user, password):
	sheet = client.open("PLP Brother to Kerb to ID").sheet1
	users = sheet.col_values(2)
	targetRow=None

	if user in users:
		targetRow = users.index(user)+1
		session['row'] = targetRow

	if targetRow:
		#print(password, sheet.cell(targetRow, 3).value.strip())
		if password in [sheet.cell(targetRow, 3).value.strip()]:
			return redirect('/home')
		else:
			return render_template('index.html', error_message = "Incorrect username or password.")
	else:
		return render_template('index.html', error_message = "User does not exist")



@app.route('/')
def hello_world(x=None, y=None):
	#app = Flask(__name__)
	scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name('PLP Bills-5644a9b3a0f7.json', scope)
	client = gspread.authorize(creds)
	return render_template('index.html',error_message="")

@app.route('/signin', methods = ['POST'])
def signup():
	user = request.form['username']
	password = request.form['password']
	session['user'] = user

	return verify_password(user, password)

def convert_to_percent(numerator, denominator):
	return round(numerator/denominator*100)

@app.route('/securitydeposit')
def display_security_deposit_page():
	sheet = client.open('Housework Tracker 19 Fall').sheet1
	name = session['name']
	row = sheet.find(name).row
	values = sheet.row_values(row)
	depo = 400
	count=-1
	misscount=0
	print(values)
	ind=0
	for i in values:
		if 'Missing' not in i:
			count+=1
		if depo <400 and 'Missing' not in i and ind>3:
			depo+=100
		elif "Missing" in i:
			misscount+=1
			depo-=100
		ind+=1
	error_message=""
	if depo <=100:
		error_message = "Submit an additional $300 deposit"
	if count>3:
		count=3
	return render_template('sec_deposit.html', error_message=error_message, deposit=depo, count = convert_to_percent(count,3), user= name, num = count, missed = misscount)

@app.route('/home')
def display_login_home():
	sheet = client.open("PLP Brother to Kerb to ID").sheet1
	row = session['row']

	name = sheet.cell(row,1).value
	session['name'] = name

	sheet = client.open('F_19 Expenses').sheet1
	row = sheet.find(" "+name+" ").row
	values = sheet.row_values(row)[3:]
	charges=[]
	for i in range(len(values)):
		if i ==1:
			charges.append(('backdebt', values[i]))
		elif i==0:
			charges.append(('housebill', values[i]))
		elif i==2 or i==3:
			if "-" not in values[i] or values[i]=='':
				charges.append(('payment', values[i]))
		elif i>4:
			charges.append(('reimbursement', values[i]))


	return render_template('login.html', user=name, total=sheet.cell(row, 3).value, account = charges)


if __name__ == '__main__':
    app.run()



