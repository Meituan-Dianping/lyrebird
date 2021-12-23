import axios from 'axios'

export const getConfig = () => {
  return axios({
    url: '/api/conf'
  })
}
