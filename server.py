from flask import Flask, request, jsonify, send_from_directory
import time
import grovepi
import threading

app = Flask(__name__)

global servo_state
servo_state = "auto"
global servo_angle
servo_angle = 0
global relay_state
relay_state = "OFF"
global temps
temps = [{"temp": 10, "stamp": "2:3:4"}, {"temp": 11, "stamp": "2:3:5"},{"temp": 8, "stamp": "2:3:6"}]
global start_time
start_time = time.perf_counter()

@app.route("/", methods=['GET'])
def landing_page():
    return send_from_directory('static', "index.html")


def temp_func():
    print('Starting a task...')
    while(1):
        global temps
        global start_time
        current_time = time.perf_counter()
        temps.append({"temp": grovepi.temp(0,'1.2'), "stamp": current_time-start_time})
        print('Task', temps[-1])
        time.sleep(5)

@app.route('/api/servo', methods=['PUT'])
def put_servo():
    global servo_state
    global servo_angle
    data = request.get_json()
    if len(data) == 0 or len(data) > 2:
        response = app.make_response("ERROR: Invalid payload")
        response.status_code = 400
        return response
    print(data)
    for key in data.keys():
        if key == "angle":
            servo_angle = data[key]
            print("Parsed angle", data[key])
        elif key == "state":
            servo_state = data[key]
            print("Parsed state", data[key])
    #desired_pwm = 12.75*(servo_angle/180)+12.75
    #grovepi.analogWrite(3,desired_pwm)
    #print(desired_pwm)
    response = app.make_response("OK")
    response.status_code = 200
    return response

@app.route('/api/relay', methods=['PUT'])
def put_relay():
    global relay_state
    data = request.get_json()
    if len(data) >= 2:
        response = app.make_response("ERROR: Invalid payload")
        response.status_code = 400
        return response
    for key in data.keys():
        print("Parsed servo state", data[key])
        relay_state = data[key]
    if relay_state == "ON":
        grovepi.digitalWrite(4,1)
    else:
        grovepi.digitalWrite(4,0)
    response = app.make_response("OK")
    response.status_code = 200
    return response

@app.route('/api/servo', methods=['GET'])
def get_servo():
    global servo_state
    global servo_angle
    data = jsonify(state=servo_state, angle=servo_angle)
    response = app.make_response(data)
    response.status_code = 200
    return response

@app.route('/api/temp', methods=['POST'])
def post_temp():
    global temps
    data = request.get_json()
    if len(data) != 1:
        response = app.make_response("ERROR: Invalid payload")
        response.status_code = 400
        return response
    print(data)
    for key in data.keys():
        values = temps[len(temps)-data[key]:]
    response = app.make_response(jsonify(values))
    response.status_code = 200
    return response

@app.route('/api/relay', methods=['GET'])
def get_relay():
    global relay_state
    data = jsonify(state=relay_state)
    response = app.make_response(data)
    response.status_code = 200
    return response

temp_thread = threading.Thread(target=temp_func)
temp_thread.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4715)
