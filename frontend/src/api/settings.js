import axios from 'axios'

export const getConfig = () => {
  return axios({
    url: '/api/conf'
  })
}

export const updateConfigByKey = (data) => {
  return axios({
    url: '/api/conf',
    data,
    method: 'PATCH'
  })
}
