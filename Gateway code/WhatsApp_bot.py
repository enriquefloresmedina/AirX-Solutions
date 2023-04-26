try:
  import urequests as requests
except:
  import requests


def send_message(phone_number, message, api_key):

  #set your host URL
  request_URL = "https://api.callmebot.com/whatsapp.php?phone=" + str(phone_number) + "&text=" + str(message) + "&apikey=" + str(api_key)

  #make the request
  response = requests.get(request_URL)
  #check if it was successful
  if response.status_code == 200:
    print('Success!')
  else:
    print('Error')
    print(response.text)