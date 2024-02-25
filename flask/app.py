from flask import Flask, render_template, request, jsonify
import requests, json
output = []

app = Flask(__name__)
@app.route('/')
def home():
  return render_template('index.html')

@app.route('/result',methods=['POST'] )
def extract():
  print(request.form.keys())
  print(request.form.values())
  result=list(request.form.values())[0]
  print(result)
  try:
    # response = requests.post('http://localhost:5005/webhooks/rest/webhook',
    #                        json={"sender": "Rasa",
    #                          "message": result})
    payload = json.dumps({"sender": "Rasa","message": result})
    # headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.request("POST",
                                url="http://localhost:5005/webhooks/rest/webhook",
                                # headers=headers,
                                data=payload)
    print(response.status_code)
    print("Bot says, ")
    bot_message = ""
    print(response.json())
    for i in response.json():
      bot_message = i['text']
      print(f"{i['text']}")
    output.extend([("message parker",result),("message stark",bot_message)])
  except Exception as err:
    print(f"Unexpected {err=}, {type(err)=}")
    output.extend([("message parker", result), ("message stark", "We are unable to process your request at the moment. Please try again...")])
  
  print(output)
  return render_template('index.html', result=output)
if __name__ == "__main__":
  app.run(host='nmtuet.ddns.net', port=5000, debug=True)
