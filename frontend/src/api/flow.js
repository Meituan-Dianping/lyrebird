import axios from 'axios'


export const getFlowDetail = (flowId, isDecode=false) => {
  return axios({
    url: '/api/flow/' + flowId
  })
}

export const getFlowList = () => {
  return axios({
    url: '/api/flow'
  })
}

export const searchFlowList = (selectedFilter) => {
  return axios({
    url: '/api/flow/search',
    method: 'POST',
    data: { selectedFilter }
  })
}

export const deleteAllFlow = () => {
  return axios({
    url: '/api/flow',
    method: 'DELETE',
    data: { ids: null }
  })
}

export const saveSelectedFlow = (ids) => {
  return axios({
    url: '/api/flow/save',
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
