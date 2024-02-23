from flask import Flask, render_template, session,flash, request, redirect, url_for
import requests
from flask_mysqldb import MySQL
import re
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash,check_password_hash
from flask_bcrypt import check_password_hash


app = Flask(__name__)
app.secret_key = "Mohamed@124"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config["MYSQL_CURSORCLASS"]="DictCursor"
app.config['MYSQL_PASSWORD'] = 'Ismail@1529'
app.config['MYSQL_DB'] = 'MUTUAL_DATA'

mysql = MySQL(app)
bcrypt = Bcrypt(app)


def isloggedin():
    return "Name" is session

def is_Password_strong(Password):
   if len(Password)<=8 :
      return False
   if not re.search(r"[a-z]", Password) or not re.search(r"[A-Z]", Password) or not re.search(r"\d",Password):
        return False
   if not re.search(r"[!@#$%^&*()-+{}|\"<>]?", Password):
        return False
   return True


@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        Name = request.form['Name']
        Password = request.form['Password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM signup WHERE Name = %s",(Name,))
        user = cur.fetchone()
        cur.close()

        if user:
            return "Name is already exist"
        elif not is_Password_strong(Password):
            return "Password must contain at least one uppercase letter, one lowercase letter, and one special character"
        else:
            hash_Password = bcrypt.generate_password_hash(Password).decode('utf-8')
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO signup (Name, Password) VALUES (%s, %s)", (Name, hash_Password))
            mysql.connection.commit()
            cur.close()
            return redirect('login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Name = request.form['Name']
        Password = request.form['Password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM signup WHERE Name = %s ", (Name,))
        user = cur.fetchone()

        if user and check_password_hash(user["Password"], Password):

            session['Name'] = Name
            return redirect('home')
        else:
            return "Invalid username or password"
    return render_template('login.html')




@app.route('/home', methods=["GET", "POST"])
def home():
 if isloggedin:
  Name = session["Name"]
  cur = mysql.connection.cursor()
  cur.execute("select * from Api_data where Name=%s",(Name,))
  data = cur.fetchall()
  mysql.connection.commit()
  cur.close()
 return render_template("index.html",data=data)
url_link = "https://api.mfapi.in/mf/"

@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "POST":
        Name = request.form['Name']
        Invested_Amount = request.form['Invested_Amount']
        fund_code = request.form['fund_code']
        Units_held = request.form['Units_held']
        user = requests.get(url_link+str(fund_code))
        fund_name = user.json().get("meta").get("fund_house")
        nav = user.json().get("data")[0].get("nav")
        current_value = float(nav) * float(Units_held)
        Growth = current_value - int(Invested_Amount)
    

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Api_data (Name,Invested_Amount,fund_code,Units_held,fund_name,nav,current_value,Growth) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (Name, Invested_Amount, fund_code, Units_held,fund_name,nav,current_value,Growth))
        mysql.connection.commit()

        cur.close()
        flash("User Created Successfully")
        return redirect(url_for('home'))
    return render_template("add.html")

@app.route('/EDIT/<string:id>',methods=["GET","POST"])
def EDIT(id):
    if request.method == "POST":
        Name = request.form['Name']
        Invested_Amount = request.form['Invested_Amount']
        fund_code = request.form['fund_code']
        Units_held = request.form['Units_held']
        user = requests.get(url_link+str(fund_code))
        fund_name = user.json().get("meta").get("fund_house")
        nav = user.json().get("data")[0].get("nav")
        current_value = float(nav) * float(Units_held)
        Growth = current_value - int(Invested_Amount)
        
       


        cur = mysql.connection.cursor()
        cur.execute("UPDATE Api_data SET Name=%s,Invested_Amount=%s,Units_held=%s,fund_name=%s,nav=%s,current_value=%s,Growth=%s WHERE id=%s",
                    (Name,Invested_Amount,Units_held,fund_name,nav,current_value,Growth,id))
        mysql.connection.commit()
        cur.close()
        flash("user Updtate","Successfully")
        return redirect(url_for('home'))
 

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Api_data WHERE id=%s",(id,))
    data = cur.fetchall()
    cur.close()
    return render_template("edit.html",data=data)

@app.route('/Delete/<string:id>',methods=["GET","POST"])
def Delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Api_data where id=%s",(id,))
    mysql.connection.commit()
    cur.close()
    flash("user delete","successfully")
    return redirect(url_for('home'))

@app.route('/')
def logout():
    session.pop("Name",None)
    return redirect(url_for("login"))
    


if __name__ == "__main__":
    app.run(debug=True)
