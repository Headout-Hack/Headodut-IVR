from flask import Flask,request
from twilio.twiml.voice_response import VoiceResponse,Gather
import speech_recognition as sr
import urllib.request
import random    
import firebase_admin
from firebase_admin import credentials,firestore
import math

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
    'message10':'Thank you for shopping with us. We hope to see you again, GoodBye.'
}

app = Flask(__name__)

@app.route('/',methods=['GET'])
def hello():
    return "Hello world"



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
            action= 'http://2e8d390ba5e3.ngrok.io/answer',
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
                action= 'http://2e8d390ba5e3.ngrok.io/gatherAddressCode',
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
        for order in orders:
            orderSplit = order.split("of")
            toAdd = dict()
            toAdd["itemName"] = orderSplit[1]
            toAdd["itemQty"] = orderSplit[0]
            orderDetails.append(toAdd)
        orderJson = {
            "orderAddress":orderAddress,
            "orderDetails":orderDetails,
            "orderId":orderId,
            "orderPhoneNo":request.values['From'],
             "orderProcessed":False
        }
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