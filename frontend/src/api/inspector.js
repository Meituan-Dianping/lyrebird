import axios from 'axios'

export const getDiffModeStatus = () => {
  return axios({
    url: '/api/diffmode'
  })
}

export const setDiffModeStatus = (status) => {
  return axios({
    url: '/api/diffmode',
    data: { status },
    method: 'PUT'
  })
}

export const getFlowFilters = () => {
  return axios({
    url: '/api/flowfilter'
  })
}

export const setFLowFilter = (name) => {
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


