from flask import request, render_template, jsonify
from app import app, db, socketio
from app.models import Sensor
from app.process_sensor_data import get_latest_sensor_value
import app.constants as CONSTANTS
from flask_socketio import SocketIO
from flask_socketio import emit


ON = CONSTANTS.ON
OFF = CONSTANTS.OFF


# @app.route('/index/<uuid>', methods=['GET','POST'])
# def index(uuid):
#     content = 0
#     if request.method == 'POST':
#         app.logger.info('successfully posted')
#         content = request.get_json()
#         # data_str = content.decode('utf-8')
#         # json_data = simplejson.loads(data_str, strict=False)
#         #sensorValue = content.get("sensorValue")
#         print "CONTENT ", content
#         #print "SENSORVAL ", sensorValue
#         return "STATUS: SUCCESS "
#     posted_data = content
#     if request.method == 'GET':
#         print "POSTED CONTENT ", posted_data
#         return render_template('index.html', content=posted_data)

# @app.route('/index', methods=['GET'])
# def view_index():
#     print "Get Content:", contents

## Need to update and migrate the database.... because of the changes

@app.route('/index', methods=['GET','POST'])
def index():
    app.logger.info('successfully posted')
    print("making a post request....")
    # logger.debug("making a post request....")
    content = request.get_json()
    if content:
        print(content)
        # logger.debug(content)
        value = int(content.get("sensorValue"))
        college = str(content.get("college"))
        machineLabel = str(content.get("machineLabel"))

        sensor = Sensor(sensorValue=value, college=college, machineLabel=machineLabel)

        db.session.add(sensor)
        db.session.commit()

        print(get_latest_sensor_value(college=college, machineLabel=machineLabel))

        return "STORE SUCCESS "
    return render_template('index.html', content=content)


@app.route('/test')
def view_index_test():
    queried_value = Sensor.query.order_by(Sensor.timestamp.desc()).first()
    value = queried_value.sensorValue
    print("DB VAL ", value)
    elm_washer1, _ = get_latest_sensor_value(college='Elm', machineLabel='Washer_1')
    elm_washer2, _ = get_latest_sensor_value(college='Elm', machineLabel='Washer_2')
    elm_washer3, _ = get_latest_sensor_value(college='Elm', machineLabel='Washer_3')
    elm_washer4, _ = get_latest_sensor_value(college='Elm', machineLabel='Washer_4')
    elm_washer5, _ = get_latest_sensor_value(college='Elm', machineLabel='Washer_5')
    elm_washer6, _ = get_latest_sensor_value(college='Elm', machineLabel='Washer_6')

    return render_template('index.html', elm_washer1=elm_washer1, elm_washer2=elm_washer2, elm_washer3=elm_washer3, elm_washer4=elm_washer4, elm_washer5=elm_washer5, elm_washer6=elm_washer6)

@app.route('/')
def view_index():
    return render_template('coming_soon.html')


@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it!'})

# if __name__ == '__main__':
#     socketio.run(app)
