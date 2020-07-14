import axios from 'axios'


export const getFlowDetail = (flowId) => {
  return axios({
    url: '/api/flow/' + flowId
  })
}

export const getFlowList = () => {
  return axios({
    url: '/api/flow'
  })
}

export const deleteAllFlow = (ids) => {
  return axios({
    url: '/api/flow',
    method: 'DELETE',
    data: { ids }
  })
}

export const saveSelectedFlow = (ids, group) => {
  return axios({
    url: '/api/flow',
    method: 'POST',
    data: { ids }
  })
}

export const deleteSelectedFlow = (ids) => {
  return axios({
    url: '/api/flow',
    method: 'DELETE',
    data: { ids }
  })
}
