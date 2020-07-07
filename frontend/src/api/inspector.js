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
