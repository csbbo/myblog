import requests
import json

headers = {
    'X-Bmob-Application-Id':'5679707a258fbfdab9d636ca5b5a56ad',
    'X-Bmob-REST-API-Key':'d93e4e50342b1abd5095eb25d1150550',
    'Content-Type':'application/json'
}

def requestSmsCode(phone):
    url = 'https://api.bmob.cn/1/requestSmsCode'
    data = {
        'mobilePhoneNumber':phone
    }
    r = requests.post(url,headers=headers,data=json.dumps(data))
    sms = json.loads(r.text)
    smsId = sms.get('smsId')
    return smsId

def verifySmsCode(phone,checkNum):
    url = 'https://api.bmob.cn/1/verifySmsCode/'+checkNum
    data = {
        'mobilePhoneNumber':phone
    }
    r = requests.post(url,headers=headers,data=json.dumps(data))
    sms = json.loads(r.text)
    msg = sms.get('msg')
    return msg
