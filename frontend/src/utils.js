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
