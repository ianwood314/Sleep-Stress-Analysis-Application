# api.py

from flask import Flask, request, jsonify
import pandas as pd
import json, statistics
from datetime import datetime
from jobs import rd, q, add_job, get_job_by_id

app = Flask(__name__)

def current_time():
    now = datetime.now()
    return now.strftime('%d/%m/%Y %H:%M:%S')

@app.route('/jobs', methods=['POST'])
def jobs_api():
    """
    API route for creating a new job to do some analysis. This route accepts a JSON payload   
    describing the job to be created.
    """
     
    try:
        job = request.get_json(force=True)
    except Exception as e:
        return True, json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})
    return json.dumps(add_job(job['start'], job['end']))

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
    data = pd.read_csv('./src/SaYoPillow-2.csv')
    data_json = data.to_json(orient='columns')
    data_json = json.loads(data_json)
    
    if request.method == 'GET':    
        return jsonify(data_json)
    elif request.method == 'POST':
        rd.flushdb()
        rd.set('data', json.dumps(data_json))
        return '---- Data Uploaded Successfully to Redis ----\n'

@app.route('/getInfo', methods=['GET'])
def get_dataset_info():
    return f"Columns in Dataset:\n  {' '.join(list(data.columns))}\n"

@app.route('/calcAvg/<col>', methods=['GET'])
def calc_col_avg(col):
    jobpayload = {'jobpayload': {
                    'jobtype': 'calcAvg',
                    'input': col
                    }
                 }
    add_job(jobpayload, current_time(), "NA")
    return 'idk king'

@app.route('/getInfo/column/<col>', methods=['GET'])
def get_col_info(col):
      return f"{col} column in Dataset:\n  {''.join(list(data[col]))}\n"

@app.route('/getInfo/all', methods=['GET'])
def get_all_info():
    # data.iat[0,0]
    return f"{data}\n"

@app.route('/getInfo/row/<row>',methods=['GET'])
def get_row_info(row):
    row = int(row)
    return f"{data.iloc[row]}\n"

@app.route('/getInfo/<col>/highest', methods=['GET'])
def get_col_highest(col):
      max = 0
      for i in range(len(data[col])):
            if data[col].iloc[i] >= max:
                  max  = data[col].iloc[i]
      return f"The highest data in {col} values is {max}\n"

@app.route('/getInfo/<col>/lowest', methods=['GET'])
def get_col_lowest(col):
      min = 0
      for i in range(len(data[col])):
            if data[col].iloc[i] <= min:
                  min  = data[col].iloc[i]
      return f"The lowest data in {col} values is {min}\n"

@app.route('/getInfo/<row>/<col>', methods=['GET'])
def get_data_value(row, col):
    row = int(row)
    return f"The value in {row} row {col} column is {data[col].iloc[row]}\n"

@app.route('/getLoc/<col>/<value>', methods=['GET'])
def get_value_position(col, value):
    position = []
    value = float(value)
    for i in range(len(data[col])):
        if(value == data[col].iloc[i]):
            position.append(i)
    return f"The position content {value} value are {list(position)}\n"

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
