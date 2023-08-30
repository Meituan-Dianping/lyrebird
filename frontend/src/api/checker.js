import axios from 'axios'

const addSearchStr = (url, options) => {
  if (options.searchStr && options.searchStr.trim()) {
    var searchStr = options.searchStr.trim()
    url += '/search?q=' + encodeURIComponent(searchStr)
  }
  return url
}
//------Checker manager------
/**
Get checkers list
*/
export const getCheckers = (options) => {
  let url = '/api/checker'
  if (options) {
    url = addSearchStr(url, options)
  }
  return axios({
    url
  })
}

//------Checker manager------
/**
Get checkers content
*/
export const getCheckerDetail = (checkerId) => {
  return axios({
    url: '/api/checker/' + checkerId
  })
}

//------Checker manager------
/**
Save checkers content
*/
export const saveCheckerDetail = (checkerId, content) => {
  return axios({
    url: '/api/checker/' + checkerId,
    method: 'POST',
    data: { content }
  })
}

//------Checker manager------
/**
Change checkers activate status by checker_id
*/
export const updateCheckerStatus = (checkerId, status) => {
  return axios({
    url: '/api/checker/' + checkerId,
    method: 'PUT',
    data: { status }
  })
}
