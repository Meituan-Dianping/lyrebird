import axios from 'axios'

export const getMenu = () => {
  return axios({
    url: '/api/menu'
  })
}
