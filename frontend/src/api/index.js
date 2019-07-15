import axios from 'axios'
export * from '@/api/search.js'
export * from '@/api/activate.js'


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

//-------Flow----------------

export const getFlowDetail = (flowId) => {
  return axios({
    url: '/api/flow/' + flowId
  })
}

//------Mock data manager------
/**
Get group name list
return:
[
    'GroupNameA',
    'GroupNameB'
]
*/
export const getGroups = () => {
  return axios({
    url: '/api/group'
  })
}

export const getGroupMap = () => {
  return axios({
    url: '/api/group'
  })
}

export const getGroupDetail = (groupId) => {
  return axios({
    url: '/api/data/' + groupId
  })
}

export const createGroup = (name, parentId, source) => {
  return axios({
    url: '/api/group',
    method: 'POST',
    data: { name: name, source: source, parent_id: parentId }
  })
}

export const deleteGroup = (groupId) => {
  return axios({
    url: '/api/group/' + groupId,
    method: 'DELETE'
  })
}

export const getDataDetail = (dataId) => {
  return axios({
    url: '/api/data/' + dataId
  })
}

export const createData = (parentId, data) => {
  return axios({
    url: '/api/data',
    method: 'POST',
    data: { data: data, parent_id: parentId }
  })
}

export const deleteData = (dataId) => {
  return axios({
    url: '/api/data/' + dataId,
    method: 'DELETE'
  })
}

export const updateGroup = (id, name, parent) => {
  return axios({
    url: '/api/mock',
    method: 'PUT',
    data: { id, name, parent }
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


//------Notice manager------
/**
Get notification list
return:
{
  'noticeList': [],
  'notRemindList': []
}
*/
export const getNoticeList = () => {
  return axios({
    url: '/api/notice'
  })
}

//------Notice manager------
/**
Delete notification by key
*/
export const deleteNotice = (key) => {
  return axios({
    url: '/api/notice',
    data: { key },
    method: 'DELETE'
  })
}

//------Notice manager------
/**
Change notification status by key
return:
*/
export const updateNoticeStatus = (key, status) => {
  return axios({
    url: '/api/notice',
    data: { key, status },
    method: 'PUT'
  })
}

export const updateDataDetail = (groupName, dataName, dataDetail) => {
  return axios({
    url: '/api/mock/' + groupName + '/data/' + dataName,
    method: 'PUT',
    data: dataDetail
  })
}

export const getConflict = (dataId) => {
  return axios({
    url: '/api/conflict/id/' + dataId
  })
}

//------Checker manager------
/**
Get checkers list
*/
export const getCheckers = () => {
  return axios({
    url: '/api/checker'
  })
}

//------Checker manager------
/**
Get checkers content
*/
export const getCheckerDetail = (checkerId) => {
  return axios({
    url: '/api/checker/' + checkerId
  })
}

//------Checker manager------
/**
Change checkers activate status by checker_id
*/
export const updateCheckerStatus = (checkerId, status) => {
  return axios({
    url: '/api/checker/' + checkerId,
    method: 'PUT',
    data: { status }
  })
}
