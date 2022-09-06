# Remote Laboratory development for embedded development boards
![contributors](https://img.shields.io/badge/Platforms%20supported-ESP32%2C%20Arduino-orange)
![lastupdate](https://img.shields.io/github/last-commit/joubiti/RemoteLaboratory)


This project is inspired by the [WebLab-Deusto](https://weblab.deusto.es/website/) initiative, which offers a variety of remote laboratories free of charge for students to experiment freely without any budget constraints, by having a set of scientific and electronic tools and platforms available for use over the web.

## Overview
The remote laboratory presented is developed with Flask, and offers a set of basic functionalities to start with for the development of a custom lab.

![image](https://user-images.githubusercontent.com/104909670/188487500-2c0aeca4-b3f8-4bbd-9322-1c13d50ac253.png)

Some of the functionalities implemented in this application are:
- One user allowed at a time, and automatic ejection of user when allocated time expires
- Real-time update of laboratory status 
- Live video stream included with the platform

## Hardware Requirements
- Raspberry Pi 4, or any other Linux platform, to run the web server
- A router, to set up port forwarding
- (Optional) A webcam, or a Raspi-Cam for live streaming
- ESP32 running [MicroPython](https://pythonforundergradengineers.com/how-to-install-micropython-on-an-esp32.html)
- Arduino board and AVRDUDE software installed on the host machine (or directly on the Raspberry Pi)

## Software Requirements
- Redis server running on the Raspberry Pi, which will store server-side variables pertaining to the remote laboratory
- Flask, along with its dependencies, behind an NGINX reverse proxy HTTP server.
- SSHD server running on the host machine
- [Paramiko](https://github.com/paramiko/paramiko) and [mpfshell](https://github.com/wendlers/mpfshell)

## Usage
```
git clone https://github.com/joubiti/RemoteLaboratory
```

To run the remote laboratory on your Raspberry Pi, first change the SSH variables and the IP addresses to their corresponding values.
You can then use Gunicorn and Eventlet to run your production server on the Raspberry Pi:
```
gunicorn -k eventlet -w 1 app:app
```
You should also edit your NGINX default config file on etc/nginx/sites-enabled with either nano or vim (with root), and add the following lines, and add the additional routes the same way:

```
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_set_header   X-Forwarded-For $remote_addr;
        proxy_set_header   Host $http_host;
        proxy_pass         "http://127.0.0.1:8000";
    }
    location /socket.io {
        include proxy_params;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_pass http://127.0.0.1:8000/socket.io;
    }
}
```
You should also set up port forwarding on your router, by going to 192.168.0.1 or whatever home page corresponds to your ISP, and open the port 80 on your Raspberry Pi's local IP address.

## Demo

![image](https://user-images.githubusercontent.com/104909670/188634630-781f69e4-01ef-401e-add0-10e135851e78.png)




## Contributing
Pull requests are welcome.
