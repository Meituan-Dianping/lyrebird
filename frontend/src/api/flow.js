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
