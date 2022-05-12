# api.py

from flask import Flask, request, jsonify
import pandas as pd
import json, statistics, 
from datetime import datetime
from jobs import add_job, get_job_by_id

app = Flask(__name__)
redis_ip = os.environ.get('REDIS_IP')
rd = redis.Redis(host=redis_ip, port=6379, db=0)
jdb = redis.Redis(host=redis_ip, port=6379, db=2, decode_responses=True)

def current_time():
    now = datetime.now()
    return now.strftime('%d/%m/%Y %H:%M:%S')

@app.route('/jobs', methods=['POST', 'GET'])
def jobs_api():
      """
      API route for creating a new job to do some analysis. This route accepts a JSON pay\
load
      describing the job to be created.
      """
      if request.method == 'POST':
          try:
              job = request.get_json(force=True)
          except Exception as e:
              return json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format\
(e)})
          return json.dumps(add_job(job['row'], job['col'], job['start'], job['end']), in\
dent=2) + '\n'

      elif request.method == 'GET':
          redis_dict = {}
          for key in jdb.keys():
              redis_dict[str(key)] = {}
              redis_dict[str(key)]['datetime'] = jdb.hget(key, 'datetime')
              redis_dict[str(key)]['status'] = jdb.hget(key, 'status')
          return json.dumps(redis_dict, indent=4) + '\n' + """
  To submit a job, do the following:
  curl localhost:5034/jobs -X POST -d '{"jobtype":<job>, "variable":<key>}' -H "Content-T\
ype: application/json"
"""


@app.route('/test', methods=['GET'])
def hello_world():
    return 'Hello World\n'

@app.route('/getInfo/routes', methods=['GET'])
def get_routes_info():
    return f"~jobs -- creating a new job to do some analysis\n~uploadData -- do\
wnload data from the csv file\n~getInfo -- return column names\n~getInfo/all --\
 return whole dataset\n~getInfo/row/<row> -- return data for specific row\n~get\
Info/column/<col> -- return data for specific column\n~getInfo/<col>/highest --\
 return highest values in specific column\n~getInfo/<col>/lowest -- return lowe\
st value in specific column\n~getInfo/<row>/<col> -- return value in specific r\
ow and column\n~getLoc/<col>/<value> -- return the postions of specific value i\
n the dataset\n~calcVar/column -- calculate the variance of specific column dat\
a values\n"


@app.route('/uploadData', methods=['GET','POST'])
def upload_dataset():
    global data
    data = pd.read_csv('SaYoPillow-2.csv')
    data_json = data.to_json(orient='columns')
    data_json = json.loads(data_json)

    if request.method == 'GET':
        start = request.args.get('start', 0)
        try:
            start = int(start)
            for key in rd.scan_iter():
                d = rd.hgetall(key)
                d = {key.decode('utf-8'): d[key].decode('utf-8') for key in d.keys()}
                data.append(d)
        except ValueError:
            return ' -- Invalid start parameter. Please ensure the start parameter is an \
integer --\n'
        return f"{type(data_json)}\n"
    elif request.method == 'POST':
        rd.flushdb()
        for item in data_json.keys():
            rd.set(item,json.dumps(data_json[item]))
        return '---- Data Uploaded Successfully ----\n'


@app.route('/getInfo', methods=['GET'])
def get_dataset_info():
    colKeys = []
    for key in rd.keys():
        colKeys.append(key.decode('utf-8'))
    return json.dumps(list(set(colKeys)), indent=2) + '\n'

@app.route('/calcAvg/<col>', methods=['GET'])
def calc_col_avg(col):
    avg = 0.0
    total = 0.0
    for key in rd.keys():
        if key.decode('utf-8') == col:
            colList  = json.loads(rd.get(key).decode('utf-8'))
            jobpayload = {'jobpayload': {
                    'jobtype': 'calcAvg',
                    'col': key.decode('utf-8')
                         }
            }
            jobs.add_job(jobpayload, current_time(), "NA")
            for i in colList:
                total = total + float(i)
            avg = total/len(colList)
    key = f'The average of {col} is {avg}\n'
    return json.dumps(rd.hgetall(key), indent=2)

@app.route('/getInfo/column/<col>', methods=['GET'])
def get_col_info(col):
    colList  = []
    for key in rd.keys():
        if key.decode('utf-8') == col:
            colList  = json.loads(rd.get(key).decode('utf-8'))
    return json.dumps(list(set(colList)), indent=2) + '\n'


@app.route('/getInfo/all', methods=['GET'])
def get_all_info():
    allList = {}
    for key in rd.keys():
        allList[key.decode('utf-8')]=json.loads(rd.get(key).decode('utf-8'))
    return json.dumps(allList, indent=2) + '\n'

@app.route('/getInfo/row/<row>',methods=['GET'])
def get_row_info(row):
    rowList = []
    for key in rd.keys():
        rowList.append(json.loads(rd.get(key).decode('utf-8')).get(row))
    return json.dumps(list(set(rowList)), indent=2) + '\n'

@app.route('/getInfo/<col>/highest', methods=['GET'])
def get_col_highest(col):
    max = 0
    for key in rd.keys():
         if key.decode('utf-8') == col:
             colList  = json.loads(rd.get(key).decode('utf-8'))
             for i in range(len(colList)):
                 if float(colList.get(str(i))) >= max:
                     max  = float(colList.get(str(i)))
    key = "The highest data in {col} values is {max}\n"
    return json.dumps(rd.hgetall(key), indent=2)

@app.route('/getInfo/<col>/lowest', methods=['GET'])
def get_col_lowest(col):
      min = 0
      for key in rd.keys():
         if key.decode('utf-8') == col:
             colList  = json.loads(rd.get(key).decode('utf-8'))
             for i in range(len(colList)):
                 if float(colList.get(str(i))) <= min:
                     min  = float(colList.get(str(i)))
      key = f"The lowest data in {col} values is {min}\n"
      return json.dumps(rd.hgetall(key), indent=2)



@app.route('/getInfo/<row>/<col>', methods=['GET'])
def get_data_value(row, col):
    for key in rd.keys():
        if key.decode('utf-8') == col:
            locList  = json.loads(rd.get(key).decode('utf-8'))
            return json.dumps(list(set(locList)), indent=2)

@app.route('/getLoc/<col>/<value>', methods=['GET'])
def get_value_position(col, value):
    position = []
    for key in rd.keys():
        if key.decode('utf-8') == col:
            colList  = json.loads(rd.get(key).decode('utf-8'))
            for i in range(len(colList)):
                if float(value) == colList.get(str(i)):
                    position.append(i)
    return json.dumps(list(set(position)), indent=2)

@app.route('/calcVar/<col>', methods=['GET'])
def cal_col_var(col):
    '''
    jobpayload = {'jobpayload': {
                    'jobtype': 'calcVar',
                    'column': col
                    }
                 }
    jobs.add_job(jobpayload, current_time(), "NA")
    '''
    return f'The variance of {col} is {statistics.variance(data[col])}\n'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    
'''
ROUTE IDEAS

/get<dataset>
-Retrieves specifc collumn of data for users can see. (all in column)

/get<dataset><specific index>
-Retrieves a specifc dataset at index (column, row)

/get<specific index>
-Retrieves whole row of data at specific index

/get<dataset>highest
-Retrieves highest data point in a dataset column

/get<dataset>lowest
-Retrieves lowest data point in dataset column

/get<dataset>average
-Calculates average in dataset column

/get<dataset>mean
-Gets most common dataset column value

/getInfo
-Returns column names, sizes, types, and other information points about the dataset

/set<location>
-Changes a data point at set location. (Checks for correct position, datatype matches entered type)

/set<dataset>
-Takes an input of a data column (can be json or something else) and replaces the dataset with the new column. (Need to check for proper size, type and location)

/set<user>
-Takes an input of user (or timestamp, whatever we're calling the rows) and replaces all data in that row. (Check size and data types match)

/replaceAll<value><new value>
-Finds all instances of <value> and replaces them with <new value>

/getRuntime [might not need this, could be cool tho]
-Returns Runtime for each job requested. 

/getErrors
-Returns logging errors


Should we have a system of plotting using matplotlib? It would look very nice
for data analysis.
(EX- /plot<dataColumn1><dataColumn2> -> returns a image graph)






'''
