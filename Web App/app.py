import urllib.request
import json
import os
import ssl
from flask import Flask, request


app = Flask(__name__)

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

# Request data goes hereD
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
data = {
  "input_data": {
      "input_string": ["Hello, my name is John"],
      "parameters":{   
              "max_new_tokens": 96,
              "do_sample": True
      }
  }
}

body = str.encode(json.dumps(data))

url = '<REPLACE-WITH-REST-ENDPOINT>'
# Replace this with the primary/secondary key or AMLToken for the endpoint
api_key = '<REPLACE-WITH-API-KEY>'
if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")

# The azureml-model-deployment header will force the request to go to a specific deployment.
# Remove this header to have the request observe the endpoint traffic rules
headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'llama-2-7b-9' }


@app.route('/', methods=['GET', 'POST'])
def landing_page():
    if request.method == "POST":
        try:
            input_string = request.form.get("input_string")
            data = {
                "input_data": {
                    "input_string": [input_string],
                    "parameters":{   
                            "max_new_tokens": 96,
                            "do_sample": True
                    }
                }
            }
            body = str.encode(json.dumps(data))
            req = urllib.request.Request(url, body, headers)
            response = urllib.request.urlopen(req)

            result = response.read()
            result = json.loads(result)
            return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Generate Text</title>
            </head>
            <body>     
                <form action = "/" method = "post">
                <p>Enter Text:</p>
                <p><input type = "text" name = "input_string" value="{}"/></p>
                <p><input type = "submit" value = "submit" /></p>
                </form>
                <p>The generated text is:</p>
                <p>{}.</p>
            </body>
            </html>""".format(input_string, str(result[0]['0']))
        
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            # Print the headers - they include the request ID and the timestamp, which are useful for debugging the failure
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))
    else:
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Generate Text</title>
        </head>
        <body>     
            <form action = "/" method = "post">
            <p>Enter Text:</p>
            <p><input type = "text" name = "input_string" /></p>
            <p><input type = "submit" value = "submit" /></p>
            </form>     
        </body>
        </html>"""
    
if __name__ == '__main__':
    app.run()