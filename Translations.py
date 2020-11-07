from googletrans import Translator
import json
translator = Translator()
translations  = {
    'message1':'Thank you for your order. Press 1 to confirm, press 2 to speak up again',
    'message2':'Welcome to the Medicine Ordering System.',
    'mesaage3':'Please speak up your order after the beep, and press star button when you are done with the order.',
    'message4':'Thank you for the order',
    'message5':'Thank you for confirmation of the order',
    'message6':'Please provide the 6 digit address code so that we can ship the medicines to your home',
    'message7':'Thank you for providing the address code',
    'message8':'Your order has been processed. Your order will be shipped shortly.',
    'message9':'Your order id is '
}

def saveTranslation(language):
    translated = dict()
    translationKeys = list(translations.keys())
    translationValues = list(translations.values())
    translationsToLanguage = translator.translate(translationValues, dest=language)
    print(translationsToLanguage,type(translationsToLanguage))
    for trans in range(0,len(translationKeys)):
        translated[translationKeys[trans]] = translationsToLanguage[trans].text
    print(translated)
    json_object = json.dumps(translated, indent = 4) 
    filename = language + '.json'
    with open(filename, 'w') as outfile: 
        outfile.write(json_object) 
    return

saveTranslation('hi')