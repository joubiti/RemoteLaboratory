from flask import Flask, render_template, session, url_for, request, redirect, Response
from redis import Redis
from werkzeug.utils import secure_filename
import serial
import os
import time
import cv2
import datetime 
from flask_socketio import SocketIO, emit
import paramiko
from scp import SCPClient
from threading import Thread, Event
import subprocess




app = Flask(__name__)
app.secret_key = "SECRET KEY"

upload_folder= "hex/"
if not os.path.exists(upload_folder):
   os.mkdir(upload_folder)
app.config['UPLOAD_FOLDER']= upload_folder

socketio = SocketIO(app, cors_allowed_origins=[], async_mode=None, logger=True, engineio_logger=True)

# SSH credentials (update values with SSH credentials of remote machine)
host = '192.168.0.7'   
username = 'user'   
password = 'passwd' 

# SSH connection   
con = paramiko.SSHClient()   
con.set_missing_host_key_policy(paramiko.AutoAddPolicy())   
con.connect(host, username=username, password=password, port=22) 

#Redis connection and initialize status of Remote Lab 
redis_host = '192.168.0.8'    #update value with local IP address of Raspberry Pi
r = Redis(redis_host, decode_responses=True)
r.set('status','available')
r.set('statusesp','available')

#Define thread for WebSockets
thread1 = Thread()
thread1_stop_event = Event()

## COMMENT THE LINES BELOW IF YOU DONT HAVE A WEBCAM/PI CAM CONNECTED TO YOUR RASPBERRY PI

#Camera configuration
camera= cv2.VideoCapture(0)

def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  
            time.sleep(0) #very important for cooperative multitasking or else your eventlet worker won't properly function



def checkHex(filename):
   #checks if uploaded file is a .hex file
   return filename.split('.')[-1] == 'hex'

def checkPy(filename):
   #checks if uploaded file is a .py file
   return filename.split('.')[-1] == 'py'


def GetStatus():
   #Secondary thread for Websockets
   while not thread1_stop_event.isSet():

      #Fetch remote laboratory status and timeleft from Redis

      status= r.get('status')
      statusesp=r.get('statusesp')
      timeleft= r.ttl('session')
      timeleftesp= r.ttl('sessionesp')


      #Emit to client-side using JSON format

      socketio.emit('response', {'data': status, 'esp': statusesp})
      socketio.sleep(1)
      socketio.emit('timeleft', {'data': timeleft})
      socketio.emit('timeesp', {'data': timeleftesp})

      #Check if session expired, and redirect user to home page

       if not r.get('sessionesp'):
           r.set('statusesp', 'available')
           with app.app_context(), app.test_request_context():
               socketio.emit('redirectesp', {'url': url_for('test')})
       
       if not r.get('session'):
           r.set('status', 'available')
           with app.app_context(), app.test_request_context():
               socketio.emit('redirect', {'url': url_for('test')})
        

#clean up ressources, upload empty .hex file
@app.before_first_request
def before_first_request():
   pass


@socketio.on('connect')
#Function to execute on client connection to sockets server, launching secondary thread
def test_connect():
    global thread1
    if not thread1.is_alive():
        print("Starting Thread 1")
        thread1 = socketio.start_background_task(GetStatus)


@socketio.on('disconnect')
#Function to execute on client disconnection
def test_disconnect():
	print("Client disconnected")


@app.route('/redirects',methods=['GET','POST'])
def redirects():
   if request.method== 'POST':
      #check if Arduino platform is currently being used (session variable set)
       if r.get('session'):
           return redirect(url_for('test'))
      #set time_limit on application side for session
       session.permanent=True
       app.permanent_session_lifetime = datetime.timedelta(minutes=0.5)
       session['user']='ok'
      #set time_limit on Redis side for session using TTL (time-to-live)
       r.set('status','unavailable')
       r.set('session' ,'ok')
       r.expire('session', 30)
       return redirect(url_for('index'))

@app.route('/redirectesp',methods=['GET','POST'])
def redirectesp():
   if request.method== 'POST':
      if r.get('sessionesp'):
          return redirect(url_for('test'))
      session.permanent = True
      app.permanent_session_lifetime = datetime.timedelta(minutes=0.5)
      session['user']='ok'
      r.set('statusesp','unavailable')
      r.set('sessionesp','ok')
      r.expire('sessionesp',30)
      return redirect(url_for('index_esp'))

@app.route('/index')
def index():
   if not session.get('user'):
      return redirect(url_for('test'))
   return render_template('arduino.html',async_mode=None)


@app.route('/esp')
def index_esp():
   if not session.get('user'):
      return redirect(url_for('test'))
   return render_template('esp.html',async_mode=None)

@app.route('/video_feed')
def video_feed():
   return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def test():
    return render_template('home.html')

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      if (checkHex(f.filename)):
         f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
         hex_file=f'hex/{f.filename}'
         #update COM port with corresponding value, programming the Arduino directly from Raspi
         subprocess.run(f'avrdude -v -p atmega328p -c arduino -P /dev/ttyACM0 -b 115200 -D -U flash:w:{hex_file}:i', shell=True)
         return redirect(url_for('index'))

         #uncomment the lines below if you wish to program the Arduino from the remote machine running SSHD and update path and COM values

         #with SCPClient(con.get_transport()) as scp:   
            #scp.put(f'hex/{f.filename}', 'C:/Users/Asus/Desktop/test')
            #hex_file=f'C:/Users/Asus/Desktop/test/{f.filename}'
            #stdin, stdout, stderr = con.exec_command(f'avrdude -v -p atmega328p -c arduino -P COM9 -b 115200 -D -U flash:w:{hex_file}:i')
            #return redirect(url_for('index'))
      else:
         return "Wrong file extension!"


@app.route('/upload_esp', methods=['GET','POST'])
def upload_to_esp():
   if request.method=='POST':
      f=request.files['file']
      if (checkPy(f.filename)):
         f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))

         #uncomment the lines below if you wish to program the ESP32 directly from the Raspberry Pi
         
         #py_file=f'hex/{f.filename}'
         #subprocess.run(f'mpfshell -n -c "open ttyUSB0; put {py_file} main.py"', shell=True)
         #return redirect(url_for('index_esp'))

         #update path and COM port with corresponding values, SCP and SSH to program ESP on remote machine
         with SCPClient(con.get_transport()) as scp:
            scp.put(f'hex/{f.filename}', 'C:/Users/Asus/Desktop/test')
            py_file=f'C:/Users/Asus/Desktop/test/{f.filename}'
            stdin, stdout, stderr= con.exec_command(f'mpfshell -n -c "open COM9; put {py_file} main.py"')
            return redirect(url_for('index_esp'))
      else:
         return "Wrong file extension"


if __name__ == '__main__':
	# app.run(host="0.0.0.0", port=8000, debug= True)
   socketio.run(app,host="0.0.0.0", port=8000, debug=True)
