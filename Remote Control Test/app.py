#!/usr/bin/env python

import pickle
import mysql.connector
import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import flask_login


#Leon Lam, 3 Aug 2016
#To-do: Implement flask-login (login) + flask-principal? (different access levels), secure SQL input, tagging specific stations (RFID readers) to clusters of steps

"""
protocol_main allows you to input a bunch of steps, create dividers, and cluster the steps between the dividers you make. 
Now we can include the NLP parsing from Smartprotocol/application/ to split protocols into steps and feed those back to the console. 
From there, the edit_SQL functions will allow us to update a protocol in the database.
"""

###################
#      Init       #
###################

#I have very little idea what this actually does. We want to set async_mode to 'eventlet' if possible, apparently. Some sort of event handler?

async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary if this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

app = Flask(__name__, template_folder='Templates')
app.config['SECRET_KEY'] = 'fookin \'ell, m8, i\'ll correspondence yer \'ead in, swear on me mum'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while 1==2:
        time.sleep(10)
        count += 1
        print count
        socketio.emit('my response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')


###################
#      Login      #
###################

#this is ok for a single user on the app - if there's multiple users we want to make sure some can be logged on as admin while the rest aren't.
#Flask-login or flask-security might work.

global administrator
administrator = False


def login_success(user,pw): #user puts in their username and password here
    login_data = pickle.load(open('pw.txt','r')) #login data is a dictionary with username:(password, name)
    try:
        if login_data[user][0] == pw:
            return True
        else:
            return False
    except:
        return False


###################
#    Sitemap      #
###################
"""
A basic site for now. Login, search/add experiments, search/add/edit protocol.
"""

# pickle.dump(login_data,open('pw.txt','w'))

@app.route('/', methods = ['GET','POST'])
@app.route('/index', methods = ['GET','POST'])
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    administrator = False
    if request.method == "POST": 
        try:
            if login_success(request.form['user'],request.form['pw']):
                administrator = True
                return render_template('/index.html', admin = administrator)
            else:
                return render_template('/index.html', admin = administrator)
        except KeyError:
            print 'KeyError'
            return render_template('/index.html', admin = administrator)
    else:
        print 'method GET'
        return render_template('/index.html', admin = administrator)

@app.route('/changeuser.html',methods = ['GET','POST'])
def changeuser():
    return render_template('/changeuser.html', admin = administrator)

@app.route('/experiment_dashboard.html',methods = ['GET','POST'])
def experiment_dashboard():
    # experiments = SQL_query(username) #more pseudocode
    return render_template('/experiment_dashboard.html', admin = administrator) # , experiments = experiments

@app.route('/experiment_search.html', methods = ['GET','POST'])
def experiment_search():
    # return render_template('/experiment_search.html', admin = administrator)
    if request.method == "GET":
        return render_template('/experiment_search.html', admin = administrator) 
        # this one brings up the search interface, and experiment_search.html will post to itself when the Search button is clicked
    else:
        x = request.form
        formData = sorted(zip(x,[request.form[k] for k in x]))
        print formData
        result = compileToSQL(formData)
        # print querySQL(result)
        try:
            if querySQL(result):
        # print querySQL(str(compileToSQL(formData)))
                return render_template('/experiment_dashboard.html', admin = administrator, experiments = querySQL(str(compileToSQL(formData)))) #experiments = compileToSQL(sorted(zip(x,[request.form[k] for k in x])))) # , experiments = experiments
            else:
                return render_template('error.html', admin = administrator, destination = "experiment_search.html")
        except:
            return render_template('error.html', admin = administrator, destination = "experiment_search.html")

@app.route('/protocols_main.html', methods = ['GET', 'POST'])
def protocols_main():
    """
    What if we pickle a dictionary(the nlp parser outputs a list where each element is one step)? 
    It'll turn into a string which we can store in the database, then we can unpack it and make it into a list we can sort.
    Keys can be (cluster, step number) tuples, and values can be the actual text.

    Each step could be a draggable element which can be moved from one container (cluster) to another.

    Deleting one step or merging it into another will be tricky. We need something to read the final order in sequence and generate a new list.

    Inserting protocol:

    The protocols page (PROTOCOL_TEXT) will have a TEXT BOX for users to paste the protocol into, then 
    Option 1) feed the TEXT BOX contents to the NLP PARSER to split them up into active steps
    Option 2) if the stuff is already in the right format (active, numbered steps), just run a sentence split on it

    This brings users to another view/page (PROTOCOL_EDIT) - a sortable/draggle jquery UI list with a bunch of containers. 
    This lets them EDIT, REORDER and PACKAGE STEPS INTO DIFFERENT CLUSTERS.
    They'll probably have to choose a protocol ID at this point.

    Once they're satisfied with the content/ordering/clustering of the steps, hitting a SAVE button READS the new arrangement and INSERTS the protocol's new order into a table.

    Editing protocol:
    Head directly to PROTOCOL_EDIT and have it display stuff from the database, since we should have all the data required



    """
    if request.method == "GET":
        return render_template('protocols_intro.html', admin = administrator)
    else:
        if request.form["Input"]:
            return render_template('protocols_main.html', admin = administrator, output = request.form["Input"])
        else:
            return render_template('error.html', admin = administrator, destination = 'protocols_main.html')

@socketio.on('protocolUpdate', namespace='/test')
def hold_down(message): #message is one the built-in events that flask-socketIO has. A named custom event might work better - we want to control and log. 
    print message['data']

###################
#Form data to SQL #
###################
"""
We're gonna get form data from searches/edits/adding of experiments/protocols/stations/users/readers etc.

Translation to SQL will hopefully happen here.
"""

def compileInOrder(data): #data is a list of (input name, input value) tuples. Input value strings are utf-8 encoded and might need decoding, I think.
    """
    We want to translate form data from the search form into an SQL command.
    The first line should be "SELECT * FROM destination", so we can put that somewhere else.
    The rest of it will be "WHERE filter1 == value1 AND filter2 == value2 AND..."
    Then "ORDER BY order1 [desc], order2 [desc]"

    Do we want to blur out the 'is/is not option' for 'sort by' queries? Then just have options asc/desc. Lemme figure out how to do that.
    """
    queryStore = []
    for i in range(0,len(data),4): #4 because currently we have (action, filter, is/is not, value) for 4 columns
        searchRow = data[i:i+4] #right now, searchRow is a smaller list of (input name, input value) tuples that makes up a query. 
        queryStore.append(join(searchRow))
    return sorted(queryStore) #queryStore is gonna need to be reorganized so that all the parameters for the SELECT come first, then all the parameters for ORDER BY

def join(row):
    """
    a row will look like this: [('0action', u'select'), ('0filter', u'userID'), ('0is_or_is_not', u'is'), ('0values', u'Fill stuff in here!')]

    Rework this to prevent SQL injection!
    """
    result = []
    for tup in row:
        add = tup[1]
        if "Default" in add:
            if result[0] == "select":
                result.pop()
                result.append("is not null")
            elif result[0] == "sort":
                result.append("desc")
        # if 'values' in tup[0]:
        #     add = checkInt(tup[1]) #wait, why do we need this? just have the user type in apostrophes themselves.
        else:
            result.append(add)
    return " ".join(result)




def compileToSQL(data, destination = "experiments"): #destination is the target table, data is the form input
    """
    We need to parse 'order by' or 'sort' differently - we need it to ignore the '=' since we just want ORDER BY x DESC
        Ignore the =/!= symbols, or parse them to flip asc and desc if necessary?

    We need:
    "WHERE user_id = >2"                -> "WHERE user_id >2" 
    "WHERE user_id != >2"               -> "WHERE user_id <2" 
    "WHERE user_id = between 2 and 3    -> "WHERE user_id between 2 and 3"

    Should we have 2 boxes for values and more options for is/is not? How much more effort do we want to place on the users? 
        If we can teach them to use syntax it'll be fine.

        Or we can literally edit the values of the form to be = , != , < , <= , > , >= , between , not between so we don't even need SQL parsing

    So a form like (action), (filter), (modifier), (value1), (value2)
        Then modifier would have between and equals, really. 
        Between 4 and Null -> greater than 4
        Between Null and 4 -> smaller than 4
        Between 4 and 5 -> between 4 and 5
        Between Null and Null -> select all

    Oh crap, an SQL query needs strings in quotes. So we need to search for "WHERE status = 'complete' AND..."

    Just have users type in quotes themselves?

    """

    data = compileInOrder(data)
    result = ["select * from " + destination + " where"]
    store = ["order by"]
    for row in data:
        if row[0:6] == "select": # select where A = x and B > y and C < z...
            #this is probably where we want to escape sql command symbols
            text = row[7:].replace('&', '').replace('and','').replace('|','').replace('or','').replace(';', '')
            if "between" in row:
                result.append(text.replace(" = ", " ").replace(" != ", " not "))
            elif ">" in row or "<" in row:
                result.append(text.replace(" = >", " >").replace(" != >", " <").replace(" = <", " <").replace(" != <", " >"))
            else:
                result.append(text)
        elif row[0:4] == "sort": # order by A [asc/desc], B [asc/desc]...
            store.append(row[5:].replace(" = ", " ").replace(" != ", " "))
    if len(result)>1:
        for i in range(len(result)):
            if i >= 2:
                result[i] = "and " + result[i]
    else:
        result = ["select * from " + destination]
    if len(store)>1:
        for j in range(len(store)):
            if j >= 2:
                store[j] = ", " + store[j]
    else:
        store = []
    return " ".join([" ".join(result)," ".join(store)])
 

###################
#  Data Handling  #
###################

"""
database_info.txt is a text file with username, password, host and database. Edit as necessary to connect to your database!
"""

def editSQL(instruction, values): # both instruction and values are tuples
    """    
    instruction will be something like:

    ("insert into person "
        "(id,first_name) "
        "values (%s,%s)")

    values will be something like ("1","Jim")
    """
    with open('database_info.txt') as f:
        datalist = f.read().split(',')
    datalist = [k.replace(" ","") for k in datalist]
    cnx = mysql.connector.connect(user = datalist[0], password = datalist[1], host = datalist[2], database = datalist[3])
    cursor = cnx.cursor()
    try:
        cursor.execute(instruction, values)
        print [k for k in cursor]
        cursor.execute("commit") #this line is important if you actually want to make a permanent change to the database!
        cursor.close()
        cnx.close()
        return True
    except: #if the SQL edit fails for some reason, call it off and return False
        print "Error."
        cursor.close()
        cnx.close()
        return False      

def querySQL(instruction): #outputs data in dictionary format
    with open('database_info.txt') as f:
        datalist = f.read().split(',')
    datalist = [k.replace(" ","") for k in datalist]
    cnx = mysql.connector.connect(user = datalist[0], password = datalist[1], host = datalist[2], database = datalist[3])
    cursor = cnx.cursor(dictionary=True)
    try:
        cursor.execute(instruction)
        # print [row for row in cursor]
        result = [row for row in cursor]
        cursor.execute('commit')
        cursor.close()
        cnx.close()
        return result
    except: #if the SQL edit fails for some reason, call it off and return False
        cursor.close()
        cnx.close()
        return False          

def deleteSQL(table, column, value):
    with open('database_info.txt') as f:
        datalist = f.read().split(',')
    datalist = [k.replace(" ","") for k in datalist]
    cnx = mysql.connector.connect(user = datalist[0], password = datalist[1], host = datalist[2], database = datalist[3])
    cursor = cnx.cursor()
    instruction = "delete from " + table + " where " + column + " = %(value)s"
    data = {'value': value}
    cursor.execute(instruction,data)
    cursor.execute('commit')
    cursor.close()
    cnx.close()

# data = querySQL("select * from experiments where duration < 370000 order by user_id")
# print data

# data = querySQL("select * from experiments where user_id >2")
# print data

# editSQL("insert into actor (actor_id, first_name, last_name) values (%s,%s,%s)",(1234,'johnnie','smith'))
# editSQL("delete from actor where actor_id is %d", (1234))

# querySQL("delete from actor where actor_id = %s", %1234)
# querySQL("insert into actor (actor_id, first_name, last_name) values (%s,%s,%s)" %(1234,"johnnie","smith"))

# deleteSQL('actor', 'actor_id', 1234)

if __name__ == '__main__':
    socketio.run(app, debug=True)

"""
Switch debug to False before actual implementation!
"""


###################
#   Unused Code   #
###################

# def SQL_query(search_conditions): 
# #for now, search conditions should be a dictionary with {filter:value} - something like {username:"100731", duration:(3600,7200), status: "complete"}
# #later on we'll actually have a database to query, hopefully
#     result = []
#     with open('database.txt','r') as f:
#         for k in f.read():
#             if meets_criteria(k,search_conditions):
#                 result.append(k)
#     return result

# def meets_criteria(entry, conditions):
#     pass

# We might be able to convert a bigInt into a datetime object - then we might be able to use duration and other stuff
# def bigIntToTime(bigInt): #we store start/end times as the number of hundredths-of-a-second (bigInt) since a predetermined point in time (the epoch).
#     days = int(bigInt/(24 * 3600 * 100.0)) #each day has 24 hours, each hour has 3600 seconds, each second has 100 hundredths
#     bigInt -= days * (24 * 3600 * 100.0)
#     hours = int(bigInt/(3600 * 100.0))
#     bigInt -= hours * (3600 * 100.0)
#     minutes = int(bigInt/(60 * 100.0))
#     bigInt -= minutes * (60 * 100.0)
#     seconds = int(bigInt/(100.0))
#     bigInt -= seconds * 100.0
#     hundreths = int(bigInt)
#     return "{0}d, {1:02}h {2:02}m {3:02}.{4:02}s".format(days,hours,minutes,seconds,hundreths)

# print bigIntToTime(68391758,0)


# class Experiment(object):
#     """I'm thinking maybe timeStart and timeEnd might be datetime objects? We can probably convert from whatever the RFID reader gives us"""
#     def __init__(self,user,experimentID,protocol,timeStart,duration=0,status="In Progress"):
#         self.user = user
#         self.experimentID = experimentID
#         self.protocol = protocol
#         self.timeStart = timeStart
#         self.duration = int(duration)
#         self.status = status
#     def integer_to_time(self):
#         timeInt = self.duration
#         hours = int(timeInt/3600.0)
#         timeInt -= hours * 3600
#         minutes = int(timeInt/60.0)
#         timeInt -= minutes * 60
#         seconds = int(timeInt)
#         return "{0:02}:{1:02}:{2:02}".format(hours,minutes,seconds)
#     def data(self):
#         return vars(self)
#     def data_with_proper_time(self):
#         result = vars(self)
#         result.duration = self.integer_to_time()
#         return result

# a = Experiment("0183503","MPI-001373-503(1)","MPI-001373 - Preparation of X","160608-10:07:02")
# b = Experiment(5,6,7,8)
# experiments = [a,b]
# a.status = "complete"
# a.duration += 100
# print a.data()
# print b.data()

# if we can get request.form to work the way we need it, socketio might not be needed - just query the database on post to experiment_search.
# @socketio.on('search_experiment', namespace='/test')
# def search_experiments(message): #message is one the built-in events that flask-socketIO has. A named custom event might work better - we want to control and log. 
    # session['receive_count'] = session.get('receive_count', 0) + 1
    # print "message: ", message['data']
    # print query_SQL("select * from person where first_name is not null")
    # emit('my response',
    #      {'data': message['data'], 'count': session['receive_count']})

# def checkInt(text):
#     """
#     If the form input is only integers, leaves it as-is. Otherwise, wraps everything up in quotes.

#     Doesn't support the 'like' operator.
#     """
#     if "desc" in text or "asc" in text:
#         return text
#     count = 0
#     for c in text:
#         try:
#             if c == '<' or c == '>' or int(c):
#                 pass
#             else:
#                 count +=1
#         except:
#             count += 1
#     if count == 0:
#         return text
#     else:
#         # print count
#         return "'" + text + "'"