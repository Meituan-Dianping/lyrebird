import axios from 'axios'

const PREFIX = '/plugins/demo/api'

export const loadRequestList = () => {
  return axios({
    url: PREFIX + '/list'
  })
}

export const remock = uri => {
  return axios({
    url: PREFIX + '/remock',
    method: 'POST',
    data: { uri }
  })
}

export const resetRequestReset = () => {
  return axios({
    url: PREFIX + '/reset',
    method: 'PUT'
  })
}
