# api.py

from flask import Flask, request, jsonify

# ADDED THESE MODULES
import hotqueue
import redis
import jobs
import os
import pandas as pd
import json, statistics
from datetime import datetime
from jobs import add_job, get_job_by_id
import matplotlib.pyplot as plt

from jobs import rd, q, add_job, get_job_by_id, jdb, img_db
app = Flask(__name__)

def current_time():
    now = datetime.now()
    return now.strftime('%d/%m/%Y %H:%M:%S')

@app.route('/jobs', methods=['POST', 'GET'])
def jobs_api():
    """
    API route for creating a new job to do some analysis. This route accepts a JSON payload
    describing the job to be created.
    """
    if request.method == 'POST':  
        try:
            job = request.get_json(force=True)
        except Exception as e:
            return json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})
    
        return json.dumps(add_job(job['column 1'], job['column 2'], job['row start'], job['row end']), indent=2) + '\n'

    elif request.method == 'GET':
        redis_dict = {}
        for key in jdb.keys():
            redis_dict[str(key)] = {}
            redis_dict[str(key)]['datetime'] = jdb.hget(key, 'datetime')
            redis_dict[str(key)]['status'] = jdb.hget(key, 'status')
        return json.dumps(redis_dict, indent=4) + '\n' + """
  To submit a job, do the following:
  curl localhost:5000/jobs -X POST -d '{"column one":<col1>, "column 2":<col2>, "row start":<rowS>, "row end":<rowE>}' -H "Content-Type: application/json"
"""

@app.route('/jobs/<job_uuid>', methods=['GET'])
def get_job_result(job_uuid: str):
    """
    API route for checking on the status of a submitted job
    """
    return json.dumps(get_job_by_id(job_uuid), indent=2) + '\n'

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
a values\n~/create/<sr>/<rr>/<t>/<lm>/<bo>/<rem>/<sr1>/<hr>/<sl> -- creates a row of data and saves it to the \
database\n~/update/<row>/<col>/<new_val> -- Updates an existing datapoint with a new val\
ue\n~/delete -- deletes everything from the database\n~/graph/<columnOne>/<columnTwo> -- graphs two data columns and exports an image"


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
        for item in data_json.keys():
            rd.set(item,json.dumps(data_json[item]))
        return '---- Data Uploaded Successfully to Redis ----\n'

@app.route('/getInfo', methods=['GET'])
def get_dataset_info():
    colKeys = []
    for key in rd.keys():
        colKeys.append(key.decode('utf-8'))
    return f"Columns in Dataset:\n  {colKeys}\n"

@app.route('/calcAvg/<col>', methods=['GET'])
def calc_col_avg(col):
    avg = 0.0
    total = 0.0
    for key in rd.keys():
        if key.decode('utf-8') == col:
            colList  = json.loads(rd.get(key).decode('utf-8'))
            for i in colList:
                total = total + float(colList[i])
            avg = total/len(colList)
    return f'The average of {col} is {avg}\n'


@app.route('/getInfo/column/<col>', methods=['GET'])
def get_col_info(col):
    colList  = {}
    for key in rd.keys():
        if key.decode('utf-8') == col:
            colList  = json.loads(rd.get(key).decode('utf-8'))
    return f"{col} column in Dataset:\n  {colList}\n"

@app.route('/getInfo/all', methods=['GET'])
def get_all_info():
    allList = []
    for key in rd.keys():
        allList.append(rd.get(key))
    return f"{list(allList)}\n"

@app.route('/getInfo/row/<row>',methods=['GET'])
def get_row_info(row):
    rowList = []
    for key in rd.keys():
        rowList.append(json.loads(rd.get(key).decode('utf-8')).get(row))
    return f"{list(rowList)}\n"

@app.route('/getInfo/<col>/highest', methods=['GET'])
def get_col_highest(col):
    max = 0
    for key in rd.keys():
         if key.decode('utf-8') == col:
             colList  = json.loads(rd.get(key).decode('utf-8'))
             for i in range(len(colList)):
                 if float(colList.get(str(i))) >= max:
                     max  = float(colList.get(str(i)))
    return f"The highest data in {col} values is {max}\n"

@app.route('/getInfo/<col>/lowest', methods=['GET'])
def get_col_lowest(col):
      min = 0
      for key in rd.keys():
         if key.decode('utf-8') == col:
             colList  = json.loads(rd.get(key).decode('utf-8'))
             for i in range(len(colList)):
                 if float(colList.get(str(i))) <= min:
                     min  = float(colList.get(str(i)))
      return f"The lowest data in {col} values is {min}\n"


@app.route('/getInfo/<row>/<col>', methods=['GET'])
def get_data_value(row, col):
    for key in rd.keys():
        if key.decode('utf-8') == col:
            colList  = json.loads(rd.get(key).decode('utf-8'))
            return f"The value in {row} row {col} column is {colList.get(row)}\n"

@app.route('/getLoc/<col>/<value>', methods=['GET'])
def get_value_position(col, value):
    position = []
    for key in rd.keys():
        if key.decode('utf-8') == col:
            colList  = json.loads(rd.get(key).decode('utf-8'))
            for i in range(len(colList)):
                if float(value) == colList.get(str(i)):
                    position.append(i)
    return f"The position content {value} value are {list(position)}\n"


@app.route('/calcVar/<col>', methods=['GET'])
def cal_col_var(col):
    colData = []
    for key in rd.keys():
        if key.decode('utf-8') == col:
            colList = json.loads(rd.get(key).decode('utf-8'))
            for i in colList:
                colData.append(float(colList[i]))
    return f'The variance of {col} is {statistics.variance(colData)}\n'

@app.route('/create/<sr>/<rr>/<t>/<lm>/<bo>/<rem>/<sr1>/<hr>/<sl>', methods=['POST'])
def create_new_row(sr:float,rr:float,t:float,lm:float,bo:float,rem:float,sr1:float,hr:float,sl:float):
    """
    add a new row fo dataset to the redis
    """
    newRow = {"sr":sr,"rr":rr,"t":t,"lm":lm,"bo":bo,"rem":rem,"sr1":sr1,"hr":hr,"sl":sl}
    for key in rd.keys():
      for item in newRow.keys():
        if key.decode('utf-8') == item:
            rd.set(item,json.dumps(newRow))
    return f'The new row of data has been created\n'

@app.route('/update/<row>/<col>/<new_val>', methods=['PUT'])
def update_data(row,col,new_val):
    """
    change the value of 1 specific variable
    """
    for key in rd.keys():
        if key.decode('utf-8') == col:
            colList = json.loads(rd.get(key).decode('utf-8'))
            for item in colList:
                if item == str(row):
                    colList[row] = new_val
                    rd.set(key, json.dumps(colList))
    return f'The new variable in location {row} row {col} column has been up to date\n'

@app.route('/delete', methods=['DELETE'])
def delete_data():
    """
    delete all keys in the redis
    """
    for key in rd.keys():
        rd.delete(key)
    return f'All data for in the dataset has been deleted.\n'

@app.route('/graph/<columnOne>/<columnTwo>', methods=['GET'])
def graphs(columnOne,columnTwo):
    """
    Creates a graph of data points based on the parameters provided.

    -> Returns an image to the directory.
    """
    x_vals = []
    y_vals1 = []
    y_vals2 = []

    for key in rd.keys():
        i=0
        if (key.decode('utf-8') == columnOne): 
            colList  = json.loads(rd.get(key).decode('utf-8'))
            for val in colList:
                x_vals.append(i)
                i=i+1
                y_vals1.append(colList.get(val))

        if (key.decode('utf-8') == columnTwo):
            colList  = json.loads(rd.get(key).decode('utf-8'))
            for val in colList:
                y_vals2.append(colList.get(val))

    plt.xlabel("Rows")
    plt.title("Data comparison between "+columnOne+" and "+columnTwo)
    plt.ylabel("Data Points")
    plt.plot(x_vals, y_vals1, 'b--')
    plt.plot(x_vals, y_vals2, 'b--')
    plt.savefig('/output_image.png')
    return("Graph output saved to local directory: '/output_image.png'\n")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
