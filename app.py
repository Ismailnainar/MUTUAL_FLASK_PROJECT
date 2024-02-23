from flask import Flask, render_template, flash, request, redirect, url_for
import requests
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "Mohamed@124"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ismail@1529'
app.config['MYSQL_DB'] = 'MUTUAL_DATA'

mysql = MySQL(app)
url_link = "https://api.mfapi.in/mf/"

@app.route('/', methods=["GET", "POST"])
def add():
    if request.method == "POST":
        Name = request.form['Name']
        Invested_Amount = request.form['Invested_Amount']
        fund_code = request.form['fund_code']
        Units_held = request.form['Units_held']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Api_data (Name,Invested_Amount,fund_code,Units_held) VALUES (%s,%s,%s,%s)",
                    (Name, Invested_Amount, fund_code, Units_held))
        mysql.connection.commit()

        cur.close()
        flash("User Created Successfully")
        return redirect(url_for('home'))
    return render_template("add.html")

@app.route('/home', methods=["GET", "POST"])
def home():
    user_list = []

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Api_data")
    data = cur.fetchall()
    cur.close()
    for row in data:
        id = row[0]
        Name = row[1]
        Invested_Amount = row[2]
        fund_code = row[3]
        Units_held = row[4]
        complete_url = requests.get(url_link + str(fund_code))

        fund_name = complete_url.json().get("meta").get("fund_house")
        nav = complete_url.json().get("data")[0].get("nav")
        current_value = float(nav) * float(Invested_Amount)
        Growth = current_value - float(Units_held)

        mydic = {
            "id": id,
            "Name": Name,
            "Invested_Amount": Invested_Amount,
            "Units_held": Units_held,
            "fund_name": fund_name,
            "nav" : nav,
            "current_value": current_value,
            "Growth": Growth
        }
        user_list.append(mydic)
    return render_template("add.html", data=user_list)

if __name__ == "__main__":
    app.run(debug=True)
