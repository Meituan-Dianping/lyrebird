import axios from 'axios'

const PREFIX = '/plugins/demo/api'

export const loadRequestList = () => {
  return axios({
    url: PREFIX + '/list'
  })
}

export const mock = uri => {
  return axios({
    url: PREFIX + '/mock',
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
