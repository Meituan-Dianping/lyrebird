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
  console.log(requestData)
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
  let dataStrList = []
  if(!dataType){
    bus.$emit('msg.warrning', 'Generate curl param -d failed: Unknown ContentType')
  }else if(dataType == 'application/json'){
    dataStrList.push(`-d \'${JSON.stringify(data)}\'`)
  }else if(dataType == 'application/x-www-form-urlencoded'){
    for(let key in data){
      dataStrList.push(`-d \"${key}=${data[key]}\"`)
    }
  }else{
    bus.$emit('msg.error', `Generate curl param -d failed: ${dataType} ContentType not support`)
  }
  return dataStrList
}
