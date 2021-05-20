import axios from 'axios'
export * from '@/api/search.js'
export * from '@/api/activate.js'
export * from '@/api/flow.js'
export * from '@/api/datamanager.js'
export * from '@/api/checker.js'
export * from '@/api/notice.js'
export * from '@/api/event.js'
export * from '@/api/bandwidth.js'
export * from '@/api/statusbar.js'
export * from '@/api/inspector.js'
import { bus } from '@/eventbus'


const successHandler = (response) => {
  if (!response.data.hasOwnProperty('code')) {
    return response
  }
  if (response.data.code !== 1000) {
    return Promise.reject(response)
  }
  if (response.data.hasOwnProperty('info')) {
    bus.$emit('msg.info', response.data.info)
  }
  return response
}

const errorHandler = (error) => {
  return Promise.reject(error)
}

axios.interceptors.response.use(successHandler, errorHandler)


//------Lyrebird menu--------
/**
  Get lyrebird selected menu
  {
    code: 1000,
    message: 'success',
    data:{
      menu: [],
      activeMenuItem: '',
      activeName: ''
    }
  }
*/
export const getMenu = () => {
  return axios({
    url: '/api/menu'
  })
}

/**
  Save lyrebird selected menu
*/
export const setActiveMenuItem = (activeMenuItem) => {
  return axios({
    url: '/api/menu',
    data: { activeMenuItem },
    method: 'PUT'
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
