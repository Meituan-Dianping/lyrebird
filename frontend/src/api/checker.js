import axios from 'axios'

//------Checker manager------
/**
Get checkers list
*/
export const getCheckers = () => {
  return axios({
    url: '/api/checker'
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
export const saveCheckerDetail = (checkerId, data) => {
  return axios({
    url: '/api/checker/' + checkerId,
    method: 'POST',
    data: { data }
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
