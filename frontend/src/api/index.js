import axios from 'axios'
export * from '@/api/search.js'
export * from '@/api/activate.js'
export * from '@/api/flow.js'
export * from '@/api/datamanager.js'
export * from '@/api/checker.js'
export * from '@/api/notice.js'


const successHandler = (response) => {
  if (!response.data.hasOwnProperty('code')) {
    return Promise.reject(response)
  }
  if (response.data.code !== 1000) {
    return Promise.reject(response)
  }
  return response
}

const errorHandler = (error) => {
  return Promise.reject(error)
}

axios.interceptors.response.use(successHandler, errorHandler)


export const getMenu = () => {
  return axios({
    url: '/api/menu'
  })
}

//------Lyrebird status--------
/**
    Get lyrebird status
    {
        code: 1000,
        message: 'success',
        ip: '',
        mock.port: 9090,
        proxy.port: 4272
    }
    */

export const getStatus = () => {
  return axios({
    url: '/api/status'
  })
}

//------Lyrebird manifest--------
/**
    Get lyrebird manifest
*/

export const getManifest = () => {
  return axios({
    url: '/api/manifest'
  })
}


/**
    Get data list by data group name
    {
        "conf": {
            "filters": [
            {
                "contents": [
                "/fe"
                ],
                "response": "fe_c07ba164-bbd4-4f02-bd54-7d78a078a09d"
            }
            ],
            "parent": null
        },
        "data": [
            [
            "fe_c07ba164-bbd4-4f02-bd54-7d78a078a09d",
            "data/Test/fe_c07ba164-bbd4-4f02-bd54-7d78a078a09d"
            ]
        ]
    }
    */
export const getDataList = (groupId) => {
  return axios({
    url: '/api/mock/' + groupId
  })
}


export const getConflict = (dataId) => {
  return axios({
    url: '/api/conflict/id/' + dataId
  })
}


