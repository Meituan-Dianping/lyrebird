export const readablizeBytes = (bytes) => {
    if(bytes===0){
        return '0 B'
    }
    var s = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
    var e = Math.floor(Math.log(bytes)/Math.log(1024));
    return (bytes/Math.pow(1024, Math.floor(e))).toFixed(1)+" "+s[e];
}