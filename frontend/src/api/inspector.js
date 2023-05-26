import axios from 'axios'

export const getFlowFilters = () => {
  return axios({
    url: '/api/flowfilter'
  })
}

export const setFlowFilter = (name) => {
  return axios({
    url: '/api/flowfilter',
    data: { name },
    method: 'PUT'
  })
}

export const getRecordMode = () => {
  return axios({
    url: '/api/mode'
  })
}

export const setRecordMode = (mode) => {
  return axios({
    url: '/api/mode/' + mode,
    method: 'PUT'
  })
}


