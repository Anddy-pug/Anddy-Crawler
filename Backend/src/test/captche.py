import requests
import time

def main():
    # Create the first ReCaptcha task
    response1 = requests.post('https://api.capsolver.com/createTask', json={
        "clientKey": "CAP-A7ADCF2D1287325A2694749A705384A2",
        "task": {
            "type": "ReCaptchaV2TaskProxyLess",
            "websiteURL": "https://pump.fun",
            "websiteKey": "6LcmKsYpAAAAABAANpgK3LDxDlxfDCoPQUYm3NZI",
            "isInvisible": False
        }
    })
    response1_data = response1.json()
    
    # Wait for 5 seconds
    time.sleep(5)
    
    print("------------------------")
    
    # Get the result for the first task
    response2 = requests.post('https://api.capsolver.com/getTaskResult', json={
        "clientKey": "CAP-A7ADCF2D1287325A2694749A705384A2",
        "taskId": response1_data['taskId']
    })
    response2_data = response2.json()
    
    print("------------------------")
    
    # Create the second ReCaptcha task
    response3 = requests.post('https://api.capsolver.com/createTask', json={
        "clientKey": "CAP-A7ADCF2D1287325A2694749A705384A2",
        "task": {
            "type": "ReCaptchaV2TaskProxyLess",
            "websiteURL": "https://pump.fun",
            "websiteKey": "6LcmKsYpAAAAABAANpgK3LDxDlxfDCoPQUYm3NZI",
            "isInvisible": False
        }
    })
    response3_data = response3.json()
    
    # Wait for 5 seconds
    time.sleep(5)
    
    print("------------------------")
    
    # Get the result for the second task
    response4 = requests.post('https://api.capsolver.com/getTaskResult', json={
        "clientKey": "CAP-A7ADCF2D1287325A2694749A705384A2",
        "taskId": response3_data['taskId']
    })
    response4_data = response4.json()
    
    print("------------------------")
    print("------------------------")
    
    # Print the status and ReCaptcha solutions from both tasks
    print(response2_data['status'], response2['data']['solution']['gRecaptchaResponse'])
    print(response4_data['status'], response4['data']['solution']['gRecaptchaResponse'])
    
    # Submit the form to create a new coin on Pump.fun
    response5 = requests.post('https://frontend-api.pump.fun/coins/create', json={
        "captchaToken": response2_data['solution']['gRecaptchaResponse'],
        "description": "test1",
        "image": "https://ipfs.io/ipfs/QmT6hrxgmzrMJV2L1jGyeeQb8PJHM3ixJFUCQi3mVwZ8kB",
        "metadataUri": "https://ipfs.io/ipfs/QmRVef1pzY64PMHNWeAvSLHx5GrssBv56d47GyjPCUqVLa",
        "name": "test1",
        "showName": True,
        "telegram": "",
        "ticker": "test1",
        "twitter": "",
        "vanityKeyCaptchaToken": response4_data['solution']['gRecaptchaResponse'],
        "website": ""
    })
    
    print(response5.json())

if __name__ == "__main__":
    main()
