from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests
import json
import flask_socketio
from datetime import datetime
import time
import random
import numpy as np
import pytz
import schedule
from multiprocessing import Process, Manager
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
DEVICE_IP = 'http://192.168.1.59'#'http://192.168.43.220'
PORT = '8080'
tz = pytz.timezone('Singapore')

URL = DEVICE_IP + ":" + PORT + "/displays/10/"

UP = 33 #PAGEUP
RIGHT = 190 #BLACKSCREEN
DOWN = 34 #PAGEDOWN
CENTER = 116 #FULLSCREEN

global scheduler_time
global curr_activity

logging.basicConfig(filename='app.log', filemode='a', level=logging.INFO)
# curr_activity = None

# manager = Manager()
# curr_activity = manager.dict()
# curr_activity['activity'] = None
# curr_activity['option'] = 0

MENU_3 = 'Menu3'
MENU_1 = 'Menu1'
MENU_2 = 'Menu2'
MENU_4 = 'Menu4'
PHONE_CALL_DAD = 'Phone Dad'
PHONE_CALL_WORK = 'Phone Work'
LOCATION = 'Location Question'
RAINING = 'Raining Question'

# start_time = datetime.datetime(2020, 09, 13, 17, 04, 30)

activity_dict = {'Phone Dad': {'heading': '<font color=#ffffff> Incoming Call </font>', \
           'subheading': 'Question', \
           'content': '&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; from Dad <br><br><b> &nbsp; &nbsp; &nbsp; &nbsp; <font color=#ff0000> Reject</font>   &nbsp; &nbsp; &nbsp; <font color=#00ff00>  Accept </font>',\
           'html': 'true', \
           'image':'#ff00ff00 call'},\
                'Menu3': {"heading": "&#8594 Menu",\
                          "content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1 <br>  &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2  <br> <font color=#ff0000> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3 </font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4",\
                          "html": 'true'},\
                 'Call Accepted': {'html':'true',\
            'content': 'Call Accepted! Please help us by filling the survey',\
           'image':'#ff00ff00 call'},\
                 'Call Rejected':  {'html':'true',\
            'content': 'Call Rejected! Please help us by filling the survey',\
           'image':'#ff000000 call'},
                'Menu3 Option1': {"heading": "&nbsp; &nbsp; Menu",
"content": "<font color=#008800> &nbsp; &nbsp; &nbsp; &nbsp; &#8594 Option 1 </font> <br>  &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2  <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3* </font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4",
"html": 'true'},\
        'Menu3 Option2': {"heading": "&nbsp; &nbsp; Menu",
"content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1 <br> <font color=#008800>  &nbsp; &nbsp; &nbsp; &nbsp; &#8594 Option 2 </font>  <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3* </font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4",
"html": 'true'},\
        'Menu3 Option3': {"heading": "&nbsp; &nbsp; Menu",
"content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1 <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2  <br> <font color=#008800> &nbsp; &nbsp; &nbsp; &nbsp; &#8594  Option 3* </font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4",
"html": 'true'},\
         'Menu3 Option4': {"heading": "&nbsp; &nbsp; Menu",
"content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1 <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2 <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3* <br> <font color=#008800> &nbsp; &nbsp; &nbsp; &nbsp; &#8594 Option 4  </font> ",
"html": 'true'},\
        'Menu1': {"heading": "&#8594 Menu",\
                  "content": "<font color=#ff0000> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1 </font>  <br>  &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2  <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3<br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4",\
                   "html": 'true'},\
        'Menu1 Option1': {"heading": "&nbsp; &nbsp; Menu",
"content": "<font color=#008800> &nbsp; &nbsp; &nbsp; &nbsp; &#8594 Option 1* </font> <br>  &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2  <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3 </font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4",
"html": 'true'},\
        'Menu1 Option2': {"heading": "&nbsp; &nbsp; Menu",
"content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1* <br> <font color=#008800>  &nbsp; &nbsp; &nbsp; &nbsp; &#8594 Option 2 </font>  <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3 </font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4",
"html": 'true'},\
        'Menu1 Option3': {"heading": "&nbsp; &nbsp; Menu",
"content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1* <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2  <br> <font color=#008800> &nbsp; &nbsp; &nbsp; &nbsp; &#8594  Option 3 </font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4",
"html": 'true'},\
         'Menu1 Option4': {"heading": "&nbsp; &nbsp; Menu",
"content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1* <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2 <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3 <br> <font color=#008800> &nbsp; &nbsp; &nbsp; &nbsp; &#8594 Option 4  </font> ",
"html": 'true'},\
         'Menu2': {"heading": "&#8594 Menu",\
                  "content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1<br> <font color=#ff0000> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2 </font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3<br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4",\
                   "html": 'true'},\
        'Menu2 Option1': {"heading": "&nbsp; &nbsp; Menu",
"content": "<font color=#008800> &nbsp; &nbsp; &nbsp; &nbsp; &#8594 Option 1 </font> <br>  &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2*  <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3 </font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4",
"html": 'true'},\
        'Menu2 Option2': {"heading": "&nbsp; &nbsp; Menu",
"content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1 <br> <font color=#008800>  &nbsp; &nbsp; &nbsp; &nbsp; &#8594 Option 2* </font>  <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3 </font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4",
"html": 'true'},\
        'Menu2 Option3': {"heading": "&nbsp; &nbsp; Menu",
"content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1 <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2*  <br> <font color=#008800> &nbsp; &nbsp; &nbsp; &nbsp; &#8594  Option 3 </font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4",
"html": 'true'},\
         'Menu2 Option4': {"heading": "&nbsp; &nbsp; Menu",
"content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1 <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2* <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3 <br> <font color=#008800> &nbsp; &nbsp; &nbsp; &nbsp; &#8594 Option 4  </font> ",
"html": 'true'},\
        'Menu4': {"heading": "&#8594 Menu",\
                  "content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1<br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2 <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3<br><font color=#ff0000>  &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4</font> ",\
                   "html": 'true'},\
        'Menu4 Option1': {"heading": "&nbsp; &nbsp; Menu",
"content": "<font color=#008800> &nbsp; &nbsp; &nbsp; &nbsp; &#8594 Option 1 </font> <br>  &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2  <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3</font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4*",
"html": 'true'},\
        'Menu4 Option2': {"heading": "&nbsp; &nbsp; Menu",
"content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1 <br> <font color=#008800>  &nbsp; &nbsp; &nbsp; &nbsp; &#8594 Option 2 </font>  <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3</font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4*",
"html": 'true'},\
        'Menu4 Option3': {"heading": "&nbsp; &nbsp; Menu",
"content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1 <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2  <br> <font color=#008800> &nbsp; &nbsp; &nbsp; &nbsp; &#8594  Option 3</font> <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 4*",
"html": 'true'},\
         'Menu4 Option4': {"heading": "&nbsp; &nbsp; Menu",
"content": "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 1 <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 2 <br> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Option 3<br> <font color=#008800> &nbsp; &nbsp; &nbsp; &nbsp; &#8594 Option 4* </font> ",
"html": 'true'},\
        'Menu1 Selected': {"content": "<font color=#008800> Option 1 Selected! Please help us by filling the survey </font>", "html": 'true'},\
        'Menu2 Selected': {"content": "<font color=#008800>  Option 2 Selected! Please help us by filling the survey </font>", "html": 'true'},\
        'Menu3 Selected': {"content": "<font color=#008800>  Option 3 Selected! Please help us by filling the survey</font>", "html": 'true'},\
        'Menu4 Selected': {"content": "<font color=#008800>  Option 4 Selected! Please help us by filling the survey</font>", "html": 'true'},\
        'Incorrect Option Selected': {"content": "<font color=#ff0000>  Wrong Menu Item Selected! Please help us by filling the survey </font>", "html": 'true'},\
        'Raining Question': {'heading': '<font color=#008800> Question </font>',
           'subheading': 'Question',
           'content': '<font color=#ff0000> &nbsp; &nbsp; Is it raining today? </font> <br><br><b> &nbsp; &nbsp; &nbsp; &nbsp;  a) No  &nbsp; &nbsp; &nbsp; b) Yes',
           'html': 'true',
           'image':'#ff00ff00 mail'},\
        'Location Question': {'heading': '<font color=#008800> Question </font>',
           'subheading': 'Question',
           'content': '<font color=#ff0000> &nbsp; &nbsp; Are you indoors our outside? </font> <br><br><b> &nbsp; &nbsp; &nbsp; &nbsp;  a) Indoors  &nbsp; &nbsp; &nbsp; b) Outside',
           'html': 'true',
           'image':'#ff00ff00 mail'},\
        'Phone Work': {'heading': '<font color=#ffffff> Incoming Call </font>', \
           'subheading': 'Question', \
           'content': '&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; from Work <br><br><b> &nbsp; &nbsp; &nbsp; &nbsp; <font color=#ff0000> Reject</font>   &nbsp; &nbsp; &nbsp; <font color=#00ff00>  Accept </font>',\
           'html': 'true', \
           'image':'#ff00ff00 call'},\
        'Question Answered': {"content": "<font color=#008800>  Thanks for answering! Please help us by filling the survey </font>", "html": 'true'}
}


def schedule_event(post_data=activity_dict['Phone Dad']):
    # global scheduler_time
    # ts = time.time()
    # times = np.random.uniform(low=1, high=16, size=(8,)).astype(int)
    # # for t in times:
    # trigger_time = ts + 1 * 60
    # utc_dt = datetime.utcfromtimestamp(trigger_time).replace(tzinfo=pytz.utc)
    # dt = utc_dt.astimezone(tz)
    # # scheduler_time = dt.strftime('%H:%M')
    send_request_to_smartglasses(URL, post_data)
    return schedule.CancelJob


@app.route('/')
def index():
    print("HEREE")
    socketio.emit('my_response', {'data': 'msg'})
    return render_template('coming_soon.html')

@socketio.on('my_event')
def test_message(message):
    print(message)
    # emit('my_response',
    #      {'data': message['data'], 'count': session['receive_count']})


def send_request_to_smartglasses(url, data):
    global curr_activity

    # print('sendRequest: {}, {}'.format(url, data))

    if data == activity_dict['Menu3']:
        curr_activity['activity'] = MENU_3
    elif data == activity_dict['Phone Dad']:
        curr_activity['activity'] = PHONE_CALL_DAD
    elif data == activity_dict['Phone Work']:
        curr_activity['activity'] = PHONE_CALL_WORK
    elif data == activity_dict['Location Question']:
        curr_activity['activity'] = LOCATION
    elif data == activity_dict['Raining Question']:
        curr_activity['activity'] = RAINING
    elif data == activity_dict['Menu1']:
        curr_activity['activity'] = MENU_1
    elif data == activity_dict['Menu2']:
        curr_activity['activity'] = MENU_2
    elif data == activity_dict['Menu4']:
        curr_activity['activity'] = MENU_4

    logging.info(str(time.time()) + " " + str(data))
    try:
        # data = json.dumps(data)
        header = {'Content-Type': 'raw'}
        x = requests.post(url, data=str(data), timeout=3.5, headers=header)
        # print("{} \n".format(x.status_code))
        return True
    except Exception as e:
        print('Failed to send request', e._class_)
        return False


def clear_screen_glasses():
    data = {'html':'true',\
            'content': ""}
    send_request_to_smartglasses(URL, data)
    return schedule.CancelJob


def respond_to_phone_call(key):
    global curr_activity
    if key == RIGHT:
        send_request_to_smartglasses(URL, activity_dict['Call Accepted'])
    elif key == CENTER:
        send_request_to_smartglasses(URL, activity_dict['Call Rejected'])
    curr_activity['activity'] = None
    schedule.every(5).seconds.do(clear_screen_glasses)


def respond_to_question(key):
    global curr_activity
    if key == RIGHT:
        send_request_to_smartglasses(URL, activity_dict['Question Answered'])
    elif key == CENTER:
        send_request_to_smartglasses(URL, activity_dict['Question Answered'])
    curr_activity['activity'] = None
    schedule.every(5).seconds.do(clear_screen_glasses)


def respond_to_menu_selection(menu_num, key):
    global curr_activity
    if key == UP:
        if curr_activity['option'] == 0:
            dict_key = menu_num
            send_request_to_smartglasses(URL, activity_dict[menu_num])
        elif curr_activity['option'] == 1:
            dict_key = menu_num
            curr_activity['option'] == 0
            send_request_to_smartglasses(URL, activity_dict[menu_num])
        elif curr_activity['option'] == 2:
            dict_key = menu_num + " " + 'Option1'
            curr_activity['option'] = 1
            send_request_to_smartglasses(URL, activity_dict[dict_key])
        elif curr_activity['option'] == 3:
            dict_key = menu_num + " " + 'Option2'
            curr_activity['option'] = 2
            send_request_to_smartglasses(URL, activity_dict[dict_key])
        elif curr_activity['option'] == 4:
            curr_activity['option'] = 3
            dict_key = menu_num + " " + 'Option3'
            send_request_to_smartglasses(URL, activity_dict[dict_key])
    elif key == DOWN:
        if curr_activity['option'] == 0:
            dict_key = menu_num + " " + 'Option1'
            curr_activity['option'] = 1
            send_request_to_smartglasses(URL, activity_dict[dict_key])
        elif curr_activity['option'] == 1:
            dict_key = menu_num + " " + 'Option2'
            curr_activity['option'] = 2
            send_request_to_smartglasses(URL, activity_dict[dict_key])
        elif curr_activity['option'] == 2:
            curr_activity['option'] = 3
            dict_key = menu_num + " " + 'Option3'
            send_request_to_smartglasses(URL, activity_dict[dict_key])
        elif curr_activity['option'] == 3:
            curr_activity['option'] = 4
            dict_key = menu_num + " " + 'Option4'
            send_request_to_smartglasses(URL, activity_dict[dict_key])
        elif curr_activity['option'] == 4:
            dict_key = menu_num + " " + 'Option4'
            send_request_to_smartglasses(URL, activity_dict[dict_key])

    elif key == CENTER:
        if curr_activity['option'] == int(menu_num[-1]):
            dict_key = menu_num + " " + 'Selected'
            send_request_to_smartglasses(URL, activity_dict[dict_key])
            curr_activity['option'] = 0
            curr_activity['activity'] = None
            schedule.every(5).seconds.do(clear_screen_glasses)
        elif curr_activity['option'] == 0:
            print("Nothing doing")
        else:
            send_request_to_smartglasses(URL, activity_dict['Incorrect Option Selected'])
            curr_activity['option'] = 0
            curr_activity['activity'] = None
            schedule.every(5).seconds.do(clear_screen_glasses)


@socketio.on('from_web_ringmouse')
def from_web_message(message):
    # print(message)
    key = message['data']

    if curr_activity['activity'] == PHONE_CALL_DAD:
        respond_to_phone_call(key)
    elif curr_activity['activity'] == PHONE_CALL_WORK:
        respond_to_phone_call(key)
    elif curr_activity['activity'] == LOCATION:
        respond_to_question(key)
    elif curr_activity['activity'] == RAINING:
        respond_to_question(key)
    elif curr_activity['activity'] == MENU_1:
        respond_to_menu_selection(MENU_1, key)
    elif curr_activity['activity'] == None:
        print('Nothing to do yet')
    elif curr_activity['activity'] == MENU_2:
        respond_to_menu_selection(MENU_2, key)
    elif curr_activity['activity'] == MENU_3:
        respond_to_menu_selection(MENU_3, key)
    elif curr_activity['activity'] == MENU_4:
        respond_to_menu_selection(MENU_4, key)

    # data = {'heading': '<font color=#ffffff> Incoming Call </font>', \
    #        'subheading': 'Question', \
    #        'content': '&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; from Dad <br><br><b> &nbsp; &nbsp; &nbsp; &nbsp; <font color=#ff0000> Reject</font>   &nbsp; &nbsp; &nbsp; <font color=#00ff00>  Accept </font>',\
    #        'html':True, \
    #        'image':'#ff00ff00 call'}

    # send_request_to_smartglasses(url, data)
    # socketio.emit('to_ios', {'data': message['data']})

# ts = time.time()
# trigger_time = ts + (5*60)
# prev_t = 5
# for t in times:
#     utc_dt = datetime.utcfromtimestamp(trigger_time).replace(tzinfo=pytz.utc)
#     dt = utc_dt.astimezone(tz)
#     scheduler_time = dt.strftime('%H:%M')
#     print(scheduler_time)
#     trigger_time += (t)*60 + prev_t*60
#     prev_t = (15-t)

@socketio.on('from_web_triggerCall')
def from_web_message_call(message):
    print(message)
    print("TRIGGERING SCHEDULER")

    ts = time.time()

    times = np.random.uniform(low=1, high=16, size=(8,)).astype(int)
    print("Times: ", times)
    i = 0
    trigger_time = ts + (5 * 60)
    prev_t = 5
    for t in times:
        trigger_time += 60
        utc_dt = datetime.utcfromtimestamp(trigger_time).replace(tzinfo=pytz.utc)
        dt = utc_dt.astimezone(tz)
        scheduler_time = dt.strftime('%H:%M')
        print("TIME for trigger: ", scheduler_time)
        if i % 2 == 0:
            # schedule.every(10).seconds.do(schedule_event, activity_dict['Menu'])
            if i == 0:
                schedule.every().day.at(scheduler_time).do(schedule_event, activity_dict['Menu3'])
            elif i == 2:
                schedule.every().day.at(scheduler_time).do(schedule_event, activity_dict['Menu2'])
            elif i == 4:
                schedule.every().day.at(scheduler_time).do(schedule_event, activity_dict['Menu1'])
            elif i == 6:
                schedule.every().day.at(scheduler_time).do(schedule_event, activity_dict['Menu4'])
        else:
            # schedule.every(10).seconds.do(schedule_event, activity_dict['Phone'])
            if i == 1:
                schedule.every().day.at(scheduler_time).do(schedule_event, activity_dict['Phone Dad'])
            elif i == 3:
                schedule.every().day.at(scheduler_time).do(schedule_event, activity_dict['Raining Question'])
            elif i == 5:
                schedule.every().day.at(scheduler_time).do(schedule_event, activity_dict['Phone Work'])
            elif i == 7:
                schedule.every().day.at(scheduler_time).do(schedule_event, activity_dict['Location Question'])
        i+=1
        trigger_time += (t) * 60 + prev_t * 60
        prev_t = (15 - t)

    # schedule.every(30).seconds.do(schedule_event)
    while True:
        schedule.run_pending()
        time.sleep(1)
    # socketio.emit('trigger_call', {'data': 'triggering call'})

@socketio.on('from_web_endCall')
def from_web_message_call(message):
    print(message)
    socketio.emit('end_call', {'data': 'ending call'})

@socketio.on('from_web_acceptCall')
def from_web_message_call2(message):
    print(message)
    socketio.emit('accept_call', {'data': 'accepting call'})


if __name__ == '__main__':
    manager = Manager()
    curr_activity = manager.dict()
    curr_activity['activity'] = None
    curr_activity['option'] = 0

    data = {'html':'true',\
            'content': ""}
    send_request_to_smartglasses(URL, data)

    socketio.run(app, debug=True)





