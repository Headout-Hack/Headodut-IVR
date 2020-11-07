from flask import Flask,request
from twilio.twiml.voice_response import VoiceResponse,Gather
import speech_recognition as sr
import urllib.request
import random    
import math

r = sr.Recognizer()

orderAudio = ""

en  = {
    'message1':'Thank you for your order. Press 1 to confirm, press 2 to speak up again',
    'message2':'Welcome to the Medicine Ordering System.',
    'message3':'Please speak up your order after the beep, and press star button when you are done with the order.',
    'message4':'Thank you for the order',
    'message5':'Thank you for confirmation of the order',
    'message6':'Please provide the 6 digit address code so that we can ship the medicines to your home',
    'message7':'Thank you for providing the address code',
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
        orderAudio = getAudio(args['RecordingUrl'])
        response.say(en['message1'])
        gather = Gather(num_digits=1, action='/gatherChoice')
        response.append(gather)
        return str(response)
    else:

        response.say(
           en['message2']
        )
        response.say(
           en['message3']
        )
        response.record(
            action= 'http://dca2ec14f8d8.ngrok.io/answer',
            method='GET',
            finish_on_key='*',
            transcribe=True,
            play_beep=True
        )
        response.say()
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
            response.say(en['message5'])
            response.say(en['message6'])
            gather = Gather(num_digits=6, action='/gatherAddressCode')
            response.append(gather)
            return str(response)
        else:
            response.redirect('/answer')
    else:
        response.redirect('/answer')
    return str(response)

@app.route('/gatherAddressCode',methods=['POST','GET'])
def gatherAddressCode():
    response = VoiceResponse()
    if 'Digits' in request.values:
        addressCode = request.values['Digits']
        orderId = generateOrderId()
        response.say(en['message7'])
        response.say(en['message8'])
        response.say(en['message9']+str(orderId))     
        print(addressCode,orderId,orderAudio)
        response.say(en['message10'])
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