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

export const getSettingModelList = () => {
  return axios({
    url: '/api/settings/list',
    method: 'GET'
  })
}

export const getSettingsForm = (name) => {
  return axios({
    url: '/api/settings/detail?name='+name,
    method: 'GET'
  })
}

export const setSettingsForm = (name, data) => {
  return axios({
    url: '/api/settings?name='+name,
    data: { data },
    method: 'POST'
  })
}
