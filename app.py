from flask import Flask,request,jsonify
from twilio.twiml.voice_response import VoiceResponse,Gather
import speech_recognition as sr
import urllib.request
import random    
import firebase_admin
from firebase_admin import credentials,firestore
import math
from twilio.rest import Client
import json 
from geopy.geocoders import Nominatim
import requests
  
f = open('credentials.json',) 
  
data = json.load(f) 

geolocator = Nominatim(user_agent="Headout-App")
account_sid = data['account_sid']
auth_token = data['auth_token']
client = Client(account_sid, auth_token)
r = sr.Recognizer()


cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
orderAudio = ""

en  = {
    'message1':'Thank you for your order. Press 1 to confirm, press 2 to speak up again',
    'message2':'Welcome to the Medicine Ordering System.',
    'message3':'Please speak up your order after the beep, and press star button when you are done with the order.',
    'message4':'Thank you for the order',
    'message5':'Thank you for confirmation of the order',
    'message6':'Please speak your complete address so that we can ship the medicines to your home',
    'message7':'Thank you for providing the address.',
    'message8':'Your order has been processed. Your order will be shipped soon.',
    'message9':'Your order id is ',
    'message10':'The order summary is sent by SMS to your phone. Thank you for shopping with us. We hope to see you again, GoodBye.',
    'message11':'Press 1 for Emergency Medicine Service, Press 2 to get Emergency Contact Numbers',
    'message12': 'Thank you for choosing option 1',
    'message14':'Thank you for choosing option 2',
    'message15':'Please enter your pincode',
    'message16':'Thank you for entering the pincode',
    'message17':'Press 1 for nearby hospitals, Press 2 for nearby Police stations, Press 3 for nearby Fire stations',
    'message18':'Thank you for choosing the option.',
    'message19':'We are messaging the details of nearby',
    'message20':'Please enter your pincode',
    "message21":"The information has been sent to your mobile phone through SMS",
    "message22":"Thank you for using the service, we hope to help you again, GoodBye!",
    "message23":"Welcome to the Emergency Mobile helpline service",
    'message24':"Thank you for providing the pincode."
}

app = Flask(__name__)

@app.route('/',methods=['GET'])
def hello():
    return "Hello world"


@app.route('/sendsms')
def sendSms():
    data = request.args
    body = data.get('body')
    number = data.get('number')
    number = '+'+number
    try:
        message = client.messages.create(
            body=body,
            from_='+12054489824',
            to=number
        )
        print("hello")
        return jsonify({"success":True,"messageId":message.sid})
    except Exception as e:
        return f"An Error Occured: {e}",400

@app.route('/index',methods=['GET','POST'])
def index():
    print("Helllo")
    response = VoiceResponse()
    response.say(en['message23'],voice='Polly.Aditi',language="hi-IN")
    response.say(en['message11'],voice='Polly.Aditi',language="hi-IN")
    gather = Gather(num_digits=1,action='/handleChoice')
    response.append(gather)
    return str(response)

@app.route('/handleChoice',methods=['GET','POST'])
def handleChoice():
    response = VoiceResponse()
    if 'Digits' in request.values:
        choice = int(request.values['Digits'])
        if choice == 1:
            response.say(en['message12'],voice='Polly.Aditi',language="hi-IN")
            response.redirect('/answer')
        elif choice == 2:
            response.say(en['message14'],voice='Polly.Aditi',language="hi-IN")
            response.say(en['message17'],voice='Polly.Aditi',language="hi-IN")
            gather = Gather(num_digits=1,action='/answer2')
            response.append(gather)
            return str(response)
        else:
            response.redirect('/index')
    else:
        response.redirect('/index')
    
    return str(response)

@app.route('/answer2',methods=['GET','POST'])
def answer1():
    response = VoiceResponse()
    if 'Digits' in request.values:
        choice = int(request.values['Digits'])
        response.say(en['message18'],voice='Polly.Aditi',language="hi-IN")
        response.say(en['message20'],voice='Polly.Aditi',language="hi-IN")
        gather = Gather(num_digits=6,action='/answer2_1/'+str(choice))
        response.append(gather)
        return str(response)
    else:
        response.redirect('/index')
        return str(response)

@app.route('/answer2_1/<choice>',methods=['GET','POST'])
def answer2_1(choice):
    response = VoiceResponse()
    choice = int(choice)
    args = request.args
    if 'Digits' in request.values:
        pincode = int(request.values['Digits'])
        phone = request.values['From']
        response.say(en['message24'],voice='Polly.Aditi',language="hi-IN")
        message = ""
        if choice == 1:
            type = "hospital"
            message += "The Hospitals for the pincode "+ str(pincode) + "are "
            for i in range(0,5):
                message += "Hospital "+str((i+1)) +" Phone No : XXXXXXXXXX" + "\n"
            message += "\n Thank you for using the service. \n Regards, \n Team Hackout"
        elif choice == 2:
            type = "police"
            message += "The Police stations for the pincode "+ str(pincode) + "are "
            for i in range(0,5):
                message += "Police Stations "+str((i+1)) +" Phone No : XXXXXXXXXX" + "\n"
            message += "\n Thank you for using the service. \n Regards, \n Team Hackout"
        else:
            type = "Fire station"
            message += "The Fire stations for the pincode "+ str(pincode) + "are "
            for i in range(0,5):
                message += "Fire station "+str((i+1)) +" Phone No : XXXXXXXXXX" + "\n"
            message += "\n Thank you for using the service. \n Regards, \n Team Hackout"

        url = "https://35c680d4bcf6.ngrok.io/sendsms"
        data = {
            "body":message,
            "number":phone
        }
        requests.get(url, params=data) 
        response.say(en['message21'],voice='Polly.Aditi',language="hi-IN")
        response.say(en['message22'],voice='Polly.Aditi',language="hi-IN")
        return str(response)
    else:
        return str(response)


@app.route("/answer", methods=['GET', 'POST'])
def voice():
    response = VoiceResponse()
    args = request.args
    if 'RecordingUrl' in args:
        global orderAudio
        orderAudio = getAudio(args['RecordingUrl'])
        response.say(en['message1'],voice='Polly.Aditi',language="hi-IN")
        gather = Gather(num_digits=1, action='/gatherChoice')
        response.append(gather)
        return str(response)
    else:

        response.say(en['message2'],voice='Polly.Aditi',language="hi-IN",
           
        )
        response.say( en['message3'],voice='Polly.Aditi',language="hi-IN",
          
        )
        response.record(
            action= 'http://35c680d4bcf6.ngrok.io/answer',
            method='GET',
            finish_on_key='*',
            transcribe=True,
            play_beep=True
        )
        response.say(voice='Polly.Aditi',language="hi-IN",)
        print(str(response))
        return str(response)

@app.route('/gatherChoice',methods=['GET','POST'])
def gatherConfirm():
    print(request.args)
    response = VoiceResponse()
    if 'Digits' in request.values:
        confirmation = int(request.values['Digits'])
        print(confirmation)
        if confirmation == 1:
            response.say(en['message5'],voice='Polly.Aditi',language="hi-IN",)
            response.say(en['message6'],voice='Polly.Aditi',language="hi-IN")
            response.record(
                action= 'https://35c680d4bcf6.ngrok.io/gatherAddressCode',
                method='GET',
                finish_on_key='*',
                transcribe=True,
                play_beep=True
            )
        else:
            response.redirect('/answer')
    else:
        response.redirect('/answer')
    return str(response)

@app.route('/gatherAddressCode',methods=['POST','GET'])
def gatherAddressCode():
    global orderAudio
    response = VoiceResponse()
    args = request.args
    if 'RecordingUrl' in args:    
        orderAddress = getAudio(args['RecordingUrl'])
        orderId = generateOrderId()
        response.say(en['message7'],voice='Polly.Aditi',language="hi-IN")
        response.say(en['message8'],voice='Polly.Aditi',language="hi-IN",)
        response.say(en['message9']+str(orderId),voice='Polly.Aditi',language="hi-IN")     
        orderAudio = orderAudio.lower()
        orders = orderAudio.split("and")
        orderDetails = []
        message = ""
        for order in orders:
            orderSplit = order.split("of")
            toAdd = dict()
            if len(orderSplit) > 1:
                toAdd["itemName"] = orderSplit[1]
                toAdd["itemQty"] = orderSplit[0]
                message += orderSplit[1] + " " + orderSplit[0] + "\n"
            orderDetails.append(toAdd)
        message += "\n Your Order Id is "+str(orderId)+"\n Thank you for shopping with us. We hope to see you again!"
        message += "\n Regards, Team Hackout!"
        orderJson = {
            "orderAddress":orderAddress,
            "orderDetails":orderDetails,
            "orderId":orderId,
            "orderPhoneNo":request.values['From'],
             "orderProcessed":False
        }
        url = "https://35c680d4bcf6.ngrok.io/sendsms"
        data = {
            "body":message,
            "number":request.values['From']
        }
        requests.get(url, params=data)
        response.say(en['message10'],voice='Polly.Aditi',language="hi-IN")
         
        #For now hardcoing the vendor id
        vendorId = 2334333
        #Updating in the database
        db.collection('orders').document(str(vendorId)).collection('orders').document(str(orderId)).set(orderJson)
        return str(response)
    else:
        response.redirect('/answer')
    return str(response)

def getAudio(url):
    fileNames = url.split("/")
    fileName = fileNames[-1]
    urllib.request.urlretrieve(url, '/home/learner/Desktop/Headout/Twilio-IVR/Recordings/'+fileName+'.wav')
    file_audio = sr.AudioFile('/home/learner/Desktop/Headout/Twilio-IVR/Recordings/'+fileName+'.wav')

    with file_audio as source:
        audio_text = r.record(source)

    print(type(audio_text))
    orderAudio = r.recognize_google(audio_text) 
    print(orderAudio)
    return orderAudio

def generateOrderId():

    digits = [i for i in range(0, 10)]
    random_str = ""
    for i in range(6):
        index = math.floor(random.random() * 10)
        random_str += str(digits[index])

    return int(random_str)

if __name__ == "__main__":
    app.run(debug=True)