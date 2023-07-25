import { bus } from '@/eventbus'

export const readablizeBytes = (bytes) => {
  if(bytes===0){
      return '0 B'
  }
  var s = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  var e = Math.floor(Math.log(bytes)/Math.log(1024));
  return (bytes/Math.pow(1024, Math.floor(e))).toFixed(1)+" "+s[e];
}

export const timestampToTime = (timeStamp) => {
  let dateObj = new Date(timeStamp * 1000)
  let hour = dateObj.getHours()
  let minute = (dateObj.getMinutes() < 10 ? '0'+dateObj.getMinutes() : dateObj.getMinutes())
  let second = (dateObj.getSeconds() < 10 ? '0'+dateObj.getSeconds() : dateObj.getSeconds())
  return hour + ':' + minute + ':' + second
}

export const timestampToDate = (timeStamp) => {
  let dateObj = new Date(timeStamp * 1000)
  let month = dateObj.getMonth()+1
  let date = dateObj.getDate()
  return month + '/' + date
}

export const timestampToDatetime = (timeStamp) => {
  let dateObj = new Date(timeStamp * 1000)
  let month = dateObj.getMonth()+1
  let date = dateObj.getDate()
  let hour = dateObj.getHours()
  let minute = (dateObj.getMinutes() < 10 ? '0'+dateObj.getMinutes() : dateObj.getMinutes())
  let second = (dateObj.getSeconds() < 10 ? '0'+dateObj.getSeconds() : dateObj.getSeconds())
  return month + '/' + date + ' ' + hour + ':' + minute + ':' + second
}

export const generateCurl = (requestData) => {
  let contentType = requestData['headers']['Content-Type'] || ''
  let curl = ['curl ' + generateCurlUrl(requestData['url'])]
  curl = curl.concat(generateCurlMethod(requestData['method']))
  curl = curl.concat(generateCurlHeader(requestData['headers']))
  curl = curl.concat(generateCurlData(requestData['data'], contentType))
  return curl.join(' \\\n  ')
}

function generateCurlUrl (url) {
  return `-g \"${url}\"`
}

function generateCurlMethod (method) {
  return ['-X '+method]
}

function generateCurlHeader (headers) {
  let ignoreKey = [
    'Host',
    'Accept-Encoding'
  ]
  let headerStrList = []
  for(let key in headers){
    if(!ignoreKey.includes(key))
      headerStrList.push(`-H \"${key}:${headers[key]}\"`)
  }
  return headerStrList
}

function generateCurlData (data, dataType) {
  if(typeof data === 'undefined' || !data){
    return []
  }
  let dataStrList = []
  if(!dataType){
    dataStrList.push(`--data-raw \'${generateJsonString(data)}\'`)
  }else if(dataType.includes('application/json')){
    dataStrList.push(`-d \'${generateJsonString(data)}\'`)
  }else if(dataType.includes('application/x-www-form-urlencoded')){
    dataStrList = Object.entries(data).map(([key, value]) => `-d \"${key}=${data[key]}\"`)
  }else{
    bus.$emit('msg.error', `Generate curl param -d failed: ${dataType} ContentType not support`)
  }
  return dataStrList
}

function generateJsonString (data) {
  let res = ''
  if(typeof data === 'string'){
    return data
  }else{
    try{
      res = JSON.stringify(data)
    }catch(e){
      bus.$emit('msg.error', `Generate curl param -d failed: Data type conversion failed`)
    }
  }
  return res
}