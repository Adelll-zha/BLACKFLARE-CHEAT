import json
import requests
from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory
import cv2
import numpy as np
import mss
import ctypes
import threading
import time
from collections import deque
from datetime import datetime
import hashlib
from termcolor import colored
import os
import webbrowser
import keyboard
import socket
import subprocess
import math

app = Flask(__name__)
clear = lambda: os.system('cls')
app.secret_key = 'fefzfzefzfexzfzcghgzrxxxxgrcgzxgreczexgezxc@'
clear()

title = ''' 
 ___       ___                      ___           .-.      ___                                  
(   )     (   )                    (   )         /    \   (   )                                 
 | |.-.    | |    .---.    .--.     | |   ___    | .`. ;   | |    .---.   ___ .-.      .--.     
 | /   \   | |   / .-, \  /    \    | |  (   )   | |(___)  | |   / .-, \ (   )   \    /    \    
 |  .-. |  | |  (__) ; | |  .-. ;   | |  ' /     | |_      | |  (__) ; |  | ' .-. ;  |  .-. ;   
 | |  | |  | |    .'`  | |  |(___)  | |,' /     (   __)    | |    .'`  |  |  / (___) |  | | |   
 | |  | |  | |   / .'| | |  |       | .  '.      | |       | |   / .'| |  | |        |  |/  |   
 | |  | |  | |  | /  | | |  | ___   | | `. \     | |       | |  | /  | |  | |        |  ' _.'   
 | '  | |  | |  ; |  ; | |  '(   )  | |   \ \    | |       | |  ; |  ; |  | |        |  .'.-.   
 ' `-' ;   | |  ' `-'  | '  `-' |   | |    \ .   | |       | |  ' `-'  |  | |        '  `-' /   
  `.__.   (___) `.__.'_.  `.__,'   (___ ) (___) (___)     (___) `.__.'_. (___)        `.__.'     streamer v4       

_______________________________________________________________________________________________________________                                                                                         
'''


LICENSE_KEYS_URL = 'https://palegreen-cattle-895473.hostingersite.com/dfvdsvsvsvsrbvdnhdftbsbdhtsfshdsgvqvbrtnbsbstvvsvsqv/manage.json'
PARAMS_FILE = './params.json'
UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

interception_dll = ctypes.cdll.LoadLibrary("./interception.dll")
dll = ctypes.WinDLL('./console.dll')

try:
    print(colored("auto click test for next version..", 'green'))
    click = ctypes.CDLL('./BLACKFLARE DRIVER.dll')
    print(colored("success!", 'green'))
    click.mouse_click.restype = None
except:
    print(colored("auto click not compatible..", 'red'))
dll.move_mouse.restype = None

FOV_DEFAULT_X, FOV_DEFAULT_Y = 50, 50
CENTER_X_DEFAULT, CENTER_Y_DEFAULT = 1920 // 2, 1080 // 2
INTENSITY_DEFAULT = 1
DELAY_DEFAULT = 0.5
MAXLEN_DEFAULT = 5

LOWER_COLOR_DEFAULT = [140, 110, 150]
UPPER_COLOR_DEFAULT = [150, 195, 255]
THRESHOLD_DEFAULT = 60

LOWER_COLOR_YELLOW = [30, 170, 170]
UPPER_COLOR_YELLOW = [30, 255, 255]

MICRO_CORRECTION_DEFAULT = False

fov_x_global = FOV_DEFAULT_X
fov_y_global = FOV_DEFAULT_Y
center_x_global = CENTER_X_DEFAULT
center_y_global = CENTER_Y_DEFAULT
intensity_global = INTENSITY_DEFAULT
delay_global = DELAY_DEFAULT
lower_color_h_global = int(LOWER_COLOR_DEFAULT[0])
lower_color_s_global = int(LOWER_COLOR_DEFAULT[1])
lower_color_v_global = int(LOWER_COLOR_DEFAULT[2])
upper_color_h_global = int(UPPER_COLOR_DEFAULT[0])
upper_color_s_global = int(UPPER_COLOR_DEFAULT[1])
upper_color_v_global = int(UPPER_COLOR_DEFAULT[2])
threshold_global = THRESHOLD_DEFAULT
maxlen_global = MAXLEN_DEFAULT
micro_correction_global = MICRO_CORRECTION_DEFAULT

tolerance = 5

def hash_key(key):
    return hashlib.sha256(key.encode('utf-8')).hexdigest()

def fetch_license_keys():
    try:
        response = requests.get(LICENSE_KEYS_URL)
        response.raise_for_status()
        data = response.json()
        license_keys = {key: datetime.fromtimestamp(timestamp) for key, timestamp in data.items()}
        return license_keys
    except (requests.RequestException, ValueError) as e:
        print(colored("SERVER CLOSE", 'red'))
        return {}

def validate_license_key(key):
    clear()
    print(colored(title, 'cyan'))

    hashed_key = hash_key(key)
    license_keys = fetch_license_keys()
    if (hashed_key in license_keys) and (datetime.now() < license_keys[hashed_key]):
        print(colored(f"Expiration date for key {hashed_key}: {license_keys[hashed_key]}", 'yellow'))
        print(colored("License key is valid!", 'green'))
        print(colored("_______________________________________________________________________________________________________________", 'cyan'))
        print("")
        return True
    else:
        print(colored("Key not found in license keys or has expired.", 'red'))
    return False

def license_required(f):
    def wrapper(*args, **kwargs):
        if 'license_key' in session and validate_license_key(session['license_key']):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('license'))
    wrapper.__name__ = f.__name__
    return wrapper

def send_size(width, height):
    message = f"{width},{height}"  # Prefixing with 'size:' for clear message type
    server_address = ('127.0.0.1', 12345)  # Replace with your server IP and port
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(server_address)
            sock.sendall(message.encode())
            print(f"Sent: {width}x{height}")
    except ConnectionRefusedError:
        print("Connection refused. Is the server running?")
    except Exception as e:
        print(f"Error: {e}")

def save_params():
    send_size(fov_x_global, fov_y_global)
    params = {
        "fov_x": int(fov_x_global),
        "fov_y": int(fov_y_global),
        "center_x": int(center_x_global),
        "center_y": int(center_y_global),
        "intensity": int(intensity_global),
        "delay": float(delay_global),
        "lower_color_h": int(lower_color_h_global),
        "lower_color_s": int(lower_color_s_global),
        "lower_color_v": int(lower_color_v_global),
        "upper_color_h": int(upper_color_h_global),
        "upper_color_s": int(upper_color_s_global),
        "upper_color_v": int(upper_color_v_global),
        "threshold": int(threshold_global),
        "maxlen": int(maxlen_global),
        "micro_correction": bool(micro_correction_global)
    }
    with open(PARAMS_FILE, 'w') as file:
        json.dump(params, file)

def load_params():
    global fov_x_global, fov_y_global, center_x_global, center_y_global, intensity_global, delay_global, lower_color_h_global, lower_color_s_global, lower_color_v_global, upper_color_h_global, upper_color_s_global, upper_color_v_global, threshold_global, maxlen_global, micro_correction_global
    default_params = {
        "fov_x": FOV_DEFAULT_X,
        "fov_y": FOV_DEFAULT_Y,
        "center_x": CENTER_X_DEFAULT,
        "center_y": CENTER_Y_DEFAULT,
        "intensity": INTENSITY_DEFAULT,
        "delay": DELAY_DEFAULT,
        "lower_color_h": LOWER_COLOR_DEFAULT[0],
        "lower_color_s": LOWER_COLOR_DEFAULT[1],
        "lower_color_v": LOWER_COLOR_DEFAULT[2],
        "upper_color_h": UPPER_COLOR_DEFAULT[0],
        "upper_color_s": UPPER_COLOR_DEFAULT[1],
        "upper_color_v": UPPER_COLOR_DEFAULT[2],
        "threshold": THRESHOLD_DEFAULT,
        "maxlen": MAXLEN_DEFAULT,
        "micro_correction": MICRO_CORRECTION_DEFAULT
    }

    try:
        with open(PARAMS_FILE, 'r') as file:
            params = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        params = default_params
        with open(PARAMS_FILE, 'w') as file:
            json.dump(params, file)

    fov_x_global = int(params["fov_x"])
    fov_y_global = int(params["fov_y"])
    center_x_global = int(params["center_x"])
    center_y_global = int(params["center_y"])
    intensity_global = int(params["intensity"])
    delay_global = float(params["delay"])
    lower_color_h_global = int(params["lower_color_h"])
    lower_color_s_global = int(params["lower_color_s"])
    lower_color_v_global = int(params["lower_color_v"])
    upper_color_h_global = int(params["upper_color_h"])
    upper_color_s_global = int(params["upper_color_s"])
    upper_color_v_global = int(params["upper_color_v"])
    threshold_global = int(params["threshold"])
    maxlen_global = int(params["maxlen"])
    micro_correction_global = bool(params["micro_correction"])
    

def reset_params():
    global fov_x_global, fov_y_global, center_x_global, center_y_global, intensity_global, delay_global, lower_color_h_global, lower_color_s_global, lower_color_v_global, upper_color_h_global, upper_color_s_global, upper_color_v_global, threshold_global, maxlen_global, micro_correction_global
    fov_x_global = FOV_DEFAULT_X
    fov_y_global = FOV_DEFAULT_Y
    center_x_global = CENTER_X_DEFAULT
    center_y_global = CENTER_Y_DEFAULT
    intensity_global = INTENSITY_DEFAULT
    delay_global = DELAY_DEFAULT
    lower_color_h_global = int(LOWER_COLOR_DEFAULT[0])
    lower_color_s_global = int(LOWER_COLOR_DEFAULT[1])
    lower_color_v_global = int(LOWER_COLOR_DEFAULT[2])
    upper_color_h_global = int(UPPER_COLOR_DEFAULT[0])
    upper_color_s_global = int(UPPER_COLOR_DEFAULT[1])
    upper_color_v_global = int(UPPER_COLOR_DEFAULT[2])
    threshold_global = THRESHOLD_DEFAULT
    maxlen_global = MAXLEN_DEFAULT
    micro_correction_global = MICRO_CORRECTION_DEFAULT
    save_params()

def set_color_preset(preset):
    global lower_color_h_global, lower_color_s_global, lower_color_v_global, upper_color_h_global, upper_color_s_global, upper_color_v_global
    if preset == 'yellow':
        lower_color_h_global = int(LOWER_COLOR_YELLOW[0])
        lower_color_s_global = int(LOWER_COLOR_YELLOW[1])
        lower_color_v_global = int(LOWER_COLOR_YELLOW[2])
        upper_color_h_global = int(UPPER_COLOR_YELLOW[0])
        upper_color_s_global = int(UPPER_COLOR_YELLOW[1])
        upper_color_v_global = int(UPPER_COLOR_YELLOW[2])
    else: 
        lower_color_h_global = int(LOWER_COLOR_DEFAULT[0])
        lower_color_s_global = int(LOWER_COLOR_DEFAULT[1])
        lower_color_v_global = int(LOWER_COLOR_DEFAULT[2])
        upper_color_h_global = int(UPPER_COLOR_DEFAULT[0])
        upper_color_s_global = int(UPPER_COLOR_DEFAULT[1])
        upper_color_v_global = int(UPPER_COLOR_DEFAULT[2])
    save_params()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and file.filename.endswith('.json'):
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        return redirect(url_for('index'))
    return redirect(request.url)

@app.route('/load/<filename>')
def load_file(filename):
    global fov_x_global, fov_y_global, center_x_global, center_y_global, intensity_global, delay_global, lower_color_h_global, lower_color_s_global, lower_color_v_global, upper_color_h_global, upper_color_s_global, upper_color_v_global, threshold_global, maxlen_global, micro_correction_global
    try:
        with open(os.path.join(UPLOAD_FOLDER, filename), 'r') as file:
            params = json.load(file)
            fov_x_global = int(params["fov_x"])
            fov_y_global = int(params["fov_y"])
            center_x_global = int(params["center_x"])
            center_y_global = int(params["center_y"])
            intensity_global = int(params["intensity"])
            delay_global = float(params["delay"])
            lower_color_h_global = int(params["lower_color_h"])
            lower_color_s_global = int(params["lower_color_s"])
            lower_color_v_global = int(params["lower_color_v"])
            upper_color_h_global = int(params["upper_color_h"])
            upper_color_s_global = int(params["upper_color_s"])
            upper_color_v_global = int(params["upper_color_v"])
            threshold_global = int(params["threshold"])
            maxlen_global = int(params["maxlen"])
            micro_correction_global = bool(params["micro_correction"])
    except Exception as e:
        print(colored(f"Error loading params: {e}", 'red'))
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/list')
def list_files():
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.json')]
    return render_template('index.html', files=files)

class Flare:
    def __init__(self, x, y, grabzone_x, grabzone_y, lower_color, upper_color, threshold, intensity, delay, maxlen, tolerance, micro_correction):
        self.grabzone_x = grabzone_x
        self.grabzone_y = grabzone_y
        self.x = x
        self.y = y
        self.lower_color = lower_color
        self.upper_color = upper_color
        self.threshold = threshold
        self.intensity = intensity
        self.delay = delay
        self.maxlen = maxlen
        self.tolerance = tolerance
        self.micro_correction = micro_correction
        self.running = False
        self.positions = []

    def aim_at_point(self, player_position, enemy_position):
        # Calculate angles needed to aim at the enemy
        dx = enemy_position[0] - player_position[0]
        dy = enemy_position[1] - player_position[1]
        
        yaw = math.atan2(dy, dx) * (180 / math.pi)  # Convert radians to degrees
        
        return yaw

    def calculate_yaw_difference(self, current_yaw, target_yaw):
        # Calculate the difference in yaw angles
        yaw_difference = target_yaw - current_yaw
        
        # Normalize yaw difference to be within -180 to 180 degrees
        if yaw_difference > 180:
            yaw_difference -= 360
        elif yaw_difference < -180:
            yaw_difference += 360
        
        return yaw_difference

    def calculate_vector_distance(self, position1, position2):
        # Calculate Euclidean distance between two positions
        dx = position2[0] - position1[0]
        dy = position2[1] - position1[1]
        
        distance = math.sqrt(dx * dx + dy * dy)
        return distance

    def run(self):
        print("Active Detection: On")
        self.running = True
        self.sct = mss.mss()
        
        while self.running:
            img = self.sct.grab({'top': self.y, 'left': self.x, 'width': self.grabzone_x, 'height': self.grabzone_y})
            screen = np.array(img)
            hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
            dilated = cv2.dilate(mask, None, iterations=5)
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            cv2.imshow('Image avec filtres', dilated)

            if contours:
                contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(contour)
                center = (x + w // 2, y + h // 2)
                cX = x + w // 2
                cY = y + 17 // 2
                x_diff = cX - self.grabzone_x // 2
                y_diff = cY - self.grabzone_y // 2

                if abs(x_diff) > self.tolerance or abs(y_diff) > self.tolerance:
                    self.positions.append((x_diff * self.intensity, y_diff * self.intensity))
                    
                    if len(self.positions) > self.maxlen:
                        self.positions.pop(0)
                    
                    avg_x_diff = np.mean([pos[0] for pos in self.positions])
                    avg_y_diff = np.mean([pos[1] for pos in self.positions])
                    
                    move_x = int(avg_x_diff)
                    move_y = int(avg_y_diff)
                    
                    if self.micro_correction:
                        move_x = int(move_x / 2)
                        move_y = int(move_y / 2)

                    dll.move_mouse(move_x, move_y)
                       

            time.sleep(self.delay)
            cv2.waitKey(1)

    def stop(self):
        self.running = False

flare = Flare(center_x_global - fov_x_global // 2, center_y_global - fov_y_global // 2, fov_x_global, fov_y_global, np.array([lower_color_h_global, lower_color_s_global, lower_color_v_global]), np.array([upper_color_h_global, upper_color_s_global, upper_color_v_global]), threshold_global, intensity_global, delay_global, maxlen_global, tolerance, micro_correction_global)

@app.route('/license', methods=['GET', 'POST'])
def license():
    if request.method == 'POST':
        license_key = request.form['license_key']
        if validate_license_key(license_key):
            session['license_key'] = license_key
            return redirect(url_for('index'))
        else:
            return colored("Invalid or expired license key.", 'red')
    return render_template('license.html')

@app.route('/', methods=['GET', 'POST'])
@license_required
def index():
    global fov_x_global, fov_y_global, center_x_global, center_y_global, intensity_global, delay_global, lower_color_h_global, lower_color_s_global, lower_color_v_global, upper_color_h_global, upper_color_s_global, upper_color_v_global, threshold_global, maxlen_global, flare, tolerance, micro_correction_global

    if request.method == 'POST':
        if 'reset' in request.form:
            reset_params()
            return redirect(url_for('index'))
        elif 'set_yellow' in request.form:
            set_color_preset('yellow')
            return redirect(url_for('index'))
        elif 'set_violet' in request.form:
            set_color_preset('violet')
            return redirect(url_for('index'))
        
        fov_x_global = int(request.form['fov_x'])
        fov_y_global = int(request.form['fov_y'])
        center_x_global = int(request.form['center_x'])
        center_y_global = int(request.form['center_y'])
        intensity_global = int(request.form['intensity'])
        delay_global = float(request.form['delay'])
        lower_color_h_global = int(request.form['lower_color_h'])
        lower_color_s_global = int(request.form['lower_color_s'])
        lower_color_v_global = int(request.form['lower_color_v'])
        upper_color_h_global = int(request.form['upper_color_h'])
        upper_color_s_global = int(request.form['upper_color_s'])
        upper_color_v_global = int(request.form['upper_color_v'])
        threshold_global = int(request.form['threshold'])
        maxlen_global = int(request.form['maxlen'])
        
        tolerance = int(request.form.get('tolerance', tolerance))
        micro_correction_global = 'micro_correction' in request.form
        
        flare.stop()
        flare = Flare(center_x_global - fov_x_global // 2, center_y_global - fov_y_global // 2, fov_x_global, fov_y_global, np.array([lower_color_h_global, lower_color_s_global, lower_color_v_global]), np.array([upper_color_h_global, upper_color_s_global, upper_color_v_global]), threshold_global, intensity_global, delay_global, maxlen_global, tolerance, micro_correction_global)
        threading.Thread(target=flare.run).start()
        
        save_params()
    
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.json')]
    
    return render_template('index.html', fov_x=fov_x_global, fov_y=fov_y_global, center_x=center_x_global, center_y=center_y_global, intensity=intensity_global, delay=delay_global, lower_color_h=lower_color_h_global, lower_color_s=lower_color_s_global, lower_color_v=lower_color_v_global, upper_color_h=upper_color_h_global, upper_color_s=upper_color_s_global, upper_color_v=upper_color_v_global, threshold=threshold_global, maxlen=maxlen_global, tolerance=tolerance, micro_correction=micro_correction_global, files=files)

if __name__ == '__main__':
    load_params()
    print(colored(title, 'cyan'))
    # Run the initialization code only once
    chemin_fichier_actuel = os.path.abspath(__file__)
    repertoire_courant = os.getcwd()
    exepath = os.path.join(repertoire_courant, '_internal/BLACKFLARE GRAPH/BLACKFLARE GRAPH.exe')
    print("Chemin de l'exécutable :", exepath)
    process = subprocess.Popen(exepath, stdout=subprocess.PIPE, creationflags=0x08000000)
    webbrowser.open('http://127.0.0.1:5000/')
    app.run()