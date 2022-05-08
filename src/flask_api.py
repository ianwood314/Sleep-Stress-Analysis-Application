# api.py

from flask import Flask
import pandas as pd
from flask_jsonpify import jsonpify

app = Flask(__name__)

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
      return json.dumps(jobs.add_job(job['start'], job['end']))

@app.route('/test', methods=['GET'])
def hello_world():
    return 'Hello World\n'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

@app.route('/upload-data', methods=['POST'])
def post_dataset():
    data = pd.read_csv ('test_data.csv')
    df_list = data.values.tolist()
    JSONP_data = jsonpify(df_list)
    
    return JSONP_data
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
