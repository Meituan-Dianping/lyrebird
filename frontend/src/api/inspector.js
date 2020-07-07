import axios from 'axios'

export const getFlowDiffMode = () => {
  return axios({
    url: '/api/diffmode'
  })
}

export const setFLowDiffMode = (diffmode) => {
  return axios({
    url: '/api/diffmode',
    data: { diffmode },
    method: 'PUT'
  })
}
