from flask import Flask, render_template, Response, jsonify, request,session,request,url_for,flash,redirect
import vonage
from flask import Flask, render_template, request

from flask_wtf import FlaskForm

from flask_sqlalchemy import SQLAlchemy

from wtforms import FileField, SubmitField,StringField,DecimalRangeField,IntegerRangeField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired,NumberRange
import os
import mysql.connector


import cv2


from YOLO_Video import video_detection
app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="license_plate_lookup"
)

app.config['SECRET_KEY'] = 'meetmali'
app.config['UPLOAD_FOLDER'] = 'static/files'
#Use FlaskForm to get input video file
class UploadFileForm(FlaskForm):

    file = FileField("File",validators=[InputRequired()])
    submit = SubmitField("Run")

@app.route('/search', methods=['POST'])
def search():
    license_plate = request.form['license_plate']
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vehicle_details WHERE License_Plate_Number = %s", (license_plate,))
    result = cursor.fetchone()
    cursor.close()

    return render_template('fine.html',result=result)

def generate_frames(path_x = ''):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

def generate_frames_web(path_x):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    session.clear()
    return render_template('indexproject.html')

@app.route("/webcam", methods=['GET','POST'])



def webcam():
    session.clear()
    return render_template('ui.html')

@app.route('/fine', methods=['GET','POST'])

def fine():
    return render_template('fine.html')

@app.route('/fiine',methods=['GET','POST'])
def fiine():
    return render_template('fiine.html')

@app.route('/FrontPage', methods=['GET','POST'])
def front():

    form = UploadFileForm()
    if form.validate_on_submit():

        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))  # Then save the file

        session['video_path'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                             secure_filename(file.filename))
    return render_template('videoprojectnew.html', form=form)

@app.route('/video')
def video():
    #return Response(generate_frames(path_x='static/files/bikes.mp4'), mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate_frames(path_x = session.get('video_path', None)),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/webapp')
def webapp():
    #return Response(generate_frames(path_x = session.get('video_path', None),conf_=round(float(session.get('conf_', None))/100,2)),mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate_frames_web(path_x=0), mimetype='multipart/x-mixed-replace; boundary=frame')


client = vonage.Client(key="40829774", secret="BDVyubPNU02zzYeU")
sms = vonage.Sms(client)

@app.route('/')
def index():
    return render_template('fine.html')

@app.route('/send', methods=['POST'])
def send():
    # phone_number = request.form.get("inputNumber")
    # disp_mssg = request.form.get("inputText")

    responseData = sms.send_message(
        {
            "from": "Vonage APIs",
            "to": "917757823469",
            "text": "A text message sent using the Nexmo SMS API",
        }
    )

    if responseData["messages"][0]["status"] == "0":
        return("Message sent successfully.")
    else:
        return(f"Message failed with error: {responseData['messages'][0]['error-text']}")


if __name__ == "__main__":
    #app.run(debug=True)
    app.run(debug=True, port=5001)