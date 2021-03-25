import axios from 'axios'

export const getStatusBarList = () => {
  let url = '/api/statusbar'
  return axios({
    url,
  })
}

export const getStatusBarDetail = statusItemId => {
  let url = '/api/statusbar/' + statusItemId
  return axios({
    url,
  })
}

export const makeRequest = url => {
  return axios({
    url
  })
}
