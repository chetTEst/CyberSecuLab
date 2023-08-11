from config import path, JOBE_SERVER_URL, X_API_KEY
from urllib.error import HTTPError
import json
import http.client
import base64
import uuid



class JobeRun:
    def __init__(self, api_key, jobe_server):
        self.API_KEY = api_key
        self.JOBE_SERVER = jobe_server

    def http_request(self, method, resource, data, headers):
        '''Send a request to Jobe with given HTTP method to given resource on
           the currently configured Jobe server and given data and headers.
           Return the connection object. '''
        if self.API_KEY:
            headers["X-API-KEY"] = self.API_KEY
        connect = http.client.HTTPSConnection(self.JOBE_SERVER)
        connect.request(method, resource, data, headers)
        return connect

    def run_test(self, language, code, filename):
        '''Execute the given code in the given language.
           Return the result object.'''
        runspec = {
            'language_id': language,
            'sourcefilename': filename,
            'sourcecode': code,
        }

        resource = '/jobe/index.php/restapi/runs/'
        data = json.dumps({'run_spec': runspec})
        return self.do_http('POST', resource, data)

    def do_http(self, method, resource, data=None):
        '''Send the given HTTP request to Jobe, return json-decoded result as
           a dictionary (or the empty dictionary if a 204 response is given).
        '''
        result = {}
        headers = {"Content-type": "application/json; charset=utf-8",
                   "Accept": "application/json"}
        try:
            connect = self.http_request(method, resource, data, headers)
            response = connect.getresponse()
            if method == 'PUT':
                return response.status
            if method == 'DELETE':
                print('DELETE: ', response.status)
                return response.status
            if response.status != 204:
                content = response.read().decode('utf8')
                if content:
                    result = json.loads(content)
            connect.close()
        except (HTTPError, ValueError) as e:
            print("\n***************** HTTP ERROR ******************\n")
            if response:
                print(' Response:', response.status, response.reason, content)
            else:
                print(e)
        return result

    def display_result(self, ro):
        '''Display the given result object'''
        if not isinstance(ro, dict) or 'outcome' not in ro:
            print("Bad result object", ro)
            return

        outcomes = {
            0: 'Successful run',
            11: 'Compile error',
            12: 'Runtime error',
            13: 'Time limit exceeded',
            15: 'Successful run',
            17: 'Memory limit exceeded',
            19: 'Illegal system call',
            20: 'Internal error, please report',
            21: 'Server overload'}

        code = ro['outcome']
        print("{}".format(outcomes[code]))
        print()
        if ro['cmpinfo']:
            print("Compiler output:")
            print(ro['cmpinfo'])
            print()
        else:
            if ro['stdout']:
                print("Output:")
                print(ro['stdout'])
            else:
                print("No output")
            if ro['stderr']:
                print()
                print("Error output:")
                print(ro['stderr'])

    def upload_file(self, file_path):
        '''Upload a file to Jobe Server using PUT, fallback to POST if needed.
           Return the file identifier.'''
        with open(file_path, "rb") as file:
            # Encoding the file content to base64
            file_content = base64.b64encode(file.read()).decode('utf-8')

        # Try uploading using PUT first
        unique_file_id = str(uuid.uuid4())  # Generate a unique file ID
        resource_put = f'/jobe/index.php/restapi/files/{unique_file_id}'
        data = json.dumps({'file_contents': file_content})
        result = self.do_http('PUT', resource_put, data)
        if result == 204:
            return unique_file_id
        return result.get('file_id', None)


class JobeRunExtended(JobeRun):

    def execute_sql(self, db_file_path, sql_query):
        # 1. Upload the SQLite3 DB file to Jobe server
        db_file_id = self.upload_file(db_file_path)

        # 2. Create the Python code to execute the SQL query on the uploaded DB
        python_code = f"""
import sqlite3

# Load the database
conn = sqlite3.connect('/home/jobe/files/{db_file_id}')  # Assuming the uploaded file retains its original extension on Jobe server
cursor = conn.cursor()

# Execute the query
cursor.execute(\"\"\"{sql_query}\"\"\")
results = cursor.fetchall()

# Close the connection
conn.close()

# Print the results
for row in results:
    print(row)
"""

        # 3. Run the generated Python code on the Jobe server
        result_obj = self.run_test('python3', python_code, 'execute_sql.py')
        #self.display_result(result_obj)
        # Extract and return the result
        # Assuming stdout contains the result rows printed line by line
        return result_obj.get('stdout', '').splitlines()


