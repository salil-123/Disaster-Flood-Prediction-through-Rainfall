from flask import Flask, render_template, abort,request,redirect,url_for,flash
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email
import driver
import Rainfall
import alerter
import pyrebase
 
app = Flask(__name__)

app.secret_key='5791628bb0b13ce0c676dfde280ba245' 
#app.config['SECRET_KEY']='5791628bb0b13ce0c676dfde280ba245'
 
# @app.route('/')
# def home():
#     return render_template('main.html')

config1 = {
  "apiKey": "AIzaSyCEYsHCiNkski8SC5qZ_wOqUac-a5aYnWY",
  "authDomain": "aiml-project-31fc6.firebaseapp.com",
  "databaseURL": "https://aiml-project-31fc6-default-rtdb.asia-southeast1.firebasedatabase.app/",
  "storageBucket": "aiml-project-31fc6.appspot.com"
}

firebase = pyrebase.initialize_app(config1)
auth = firebase.auth()
db = firebase.database()

person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/index')
def index():
    if person["is_logged_in"] == True:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        try:
            # Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            print(f"Successfully signed in user: {user}")
            # Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]

            # Get the name of the user from the Realtime Database
            user_data = db.child("users").child(person["uid"]).get().val()
            if user_data:
                person["name"] = user_data.get("name", "")
            else:
                person["name"] = ""

            # Redirect to welcome page
            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error signing in user: {e}")
            # If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
        
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            #Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            #Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            #Append data to the firebase realtime database
            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)
            #Go to welcome page
            return redirect(url_for('index'))
        except:
            #If there is any error, redirect to register
            return redirect(url_for('register'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('register'))


@app.route('/refreshFlood')
def refreshFlood():
    alerter.water_level_predictior()#To refresh the flood warning data
    return redirect(url_for('floodHome'))

@app.route('/about')
def about_team():
    return render_template('about-team.html')

@app.route('/contacts')
def contact():
    return render_template('contact.html')

@app.route('/services')
def service():
    return render_template('service.html')


@app.route('/floodHome')
def floodHome():
    res=alerter.alerting()
    for i in range(len(res)):
        res[i]='Flood ALERT for '+res[i]
    return render_template('flood_entry.html',result=res)


@app.route('/rainfallHome')
def rainfallHome():
    return render_template('rain_entry.html')


@app.route('/floodResult',methods=['POST', 'GET'])
def floodResult():
    if request.method == 'POST':
        if len(request.form['DATE'])==0:
            return redirect(url_for('floodHome'))
        else:
            user_date=request.form['DATE']
            river=request.form['SEL']
            # print("##3#######",user_date,"#####",river,"#############")
            # print(type(user_date))
            # print(type(river))
            results_dict=driver.drive(river,user_date)
            # results_dict={'Mse':0.5,
            #         'discharge':1400}
            print("-----------",type(results_dict),"----------")
            Table = []
            for key, value in results_dict.items(): 
                # temp = []
                # temp.extend([key,value])  #Note that this will change depending on the structure of your dictionary
                Table.append(value) 
            return render_template('flood_result.html',result=Table)
    else:
        return redirect(url_for('floodHome'))

   # return render_template('floodResult.html')
@app.route('/rainfallResult',methods=['POST','GET'])
def rainfallResult():
    if request.method == 'POST':
        if len(request.form['Year'])==0:
            flash("Please Enter Data!!")
            return redirect(url_for('rainfallHome'))
        else:
            year=request.form['Year']
            region=request.form['SEL']
            print("##3#######",year,"#####",region,"#############")
            mae,score=Rainfall.rainfall(year,region)
            return render_template('rain_result.html',Mae=mae,Score=score)
            
    else:
        return redirect(url_for('rainfallHome'))
    # return render_template('rainfallResult.html')


if __name__ == '__main__':
    app.run(debug = True)