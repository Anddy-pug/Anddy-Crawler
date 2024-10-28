const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');
const main = async () => {
    const response1 = await axios.post('https://api.capsolver.com/createTask', {
        clientKey: "CAP-A7ADCF2D1287325A2694749A705384A2",
        task: {
            type: "ReCaptchaV2TaskProxyLess",
            websiteURL: "https://pump.fun",
            websiteKey: "6LcmKsYpAAAAABAANpgK3LDxDlxfDCoPQUYm3NZI",
            pageAction:"createCoin",  
            isInvisible: false
        }
    });
    await new Promise(resolve => setTimeout(resolve, 5000)); // Delay for 1 second
    console.log("------------------------");
    const response2 = await axios.post('https://api.capsolver.com/getTaskResult', {
        clientKey: "CAP-A7ADCF2D1287325A2694749A705384A2",
        taskId: response1.data.taskId
    });
    console.log("------------------------",);
    const response3 = await axios.post('https://api.capsolver.com/createTask', {
        clientKey: "CAP-A7ADCF2D1287325A2694749A705384A2",
        task: {
            type: "ReCaptchaV2TaskProxyLess",
            websiteURL: "https://pump.fun",
            websiteKey: "6LcmKsYpAAAAABAANpgK3LDxDlxfDCoPQUYm3NZI",
            pageAction:"getVanityKey",
            isInvisible: false
        }
    });
    await new Promise(resolve => setTimeout(resolve, 5000)); // Delay for 1 second
    console.log("------------------------");
    const response4 = await axios.post('https://api.capsolver.com/getTaskResult', {
        clientKey: "CAP-A7ADCF2D1287325A2694749A705384A2",  
        taskId: response3.data.taskId
    });
    console.log("------------------------");
    console.log("------------------------");
    // console.log(response2.data.status, response2.data.solution.gRecaptchaResponse);
    // console.log(response4.data.status,  response4.data.solution.gRecaptchaResponse);
    const response5 = await axios.post('https://frontend-api.pump.fun/coins/create', {
        captchaToken:response2.data.solution.gRecaptchaResponse,
        description:"test1",
        image:"https://ipfs.io/ipfs/QmT6hrxgmzrMJV2L1jGyeeQb8PJHM3ixJFUCQi3mVwZ8kB",
        metadataUri:"https://ipfs.io/ipfs/QmRVef1pzY64PMHNWeAvSLHx5GrssBv56d47GyjPCUqVLa",
       name:"test1",
       showName:true,
       telegram:"",
       ticker:"test1",
       twitter:"",
       vanityKeyCaptchaToken:response4.data.solution.gRecaptchaResponse,
       website:""
    });
    console.log(response5);
}
main();
