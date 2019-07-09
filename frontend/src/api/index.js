import axios from 'axios'

const successHandler = (response) => {
  if (!response.data.hasOwnProperty('code')) {
    return Promise.reject(response)
  }
  if (response.data.code != 1000) {
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

export const getDataMap = () => {
  return axios({
    url: '/api/group'
  })
}

export const createGroup = (name, parent) => {
  return axios({
    url: '/api/mock',
    method: 'POST',
    data: { name, parent }
  })
}

export const updateGroup = (id, name, parent) => {
  return axios({
    url: '/api/mock',
    method: 'PUT',
    data: { id, name, parent }
  })
}

export const deleteGroup = (groupId) => {
  return axios({
    url: '/api/mock/' + groupId,
    method: 'DELETE'
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

export const createData = (groupId, name) => {
  return axios({
    url: '/api/mock/' + groupId + '/data',
    data: { name },
    method: 'POST'
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

//------Notice manager------

export const deleteData = (groupId, ids) => {
  return axios({
    url: '/api/mock/' + groupId + '/data',
    data: { ids },
    method: 'DELETE'
  })
}

/**
Get mock data detail
{
    "request": {
        "data": null,
        "headers": {
        "Accept-Encoding": "gzip, deflate",
        ...
        },
        "method": "POST",
        "url": "http://host"
    },
    "response": {
        "code": 200,
        "data": null,
        "headers": {
        "Cache-Control": "no-cache",
        ...
        }
    }
}
*/
export const getDataDetail = (dataId) => {
  return axios({
    url: '/api/data/' + dataId
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

/**
Get activated data group ID
*/
export const getActivatedGroup = () => {
  return axios({
    url: '/api/mock/activated'
  })
}

/**
Activate data group by ID
*/
export const activateGroup = (groupId) => {
  return axios({
    url: '/api/mock/' + groupId + '/activate',
    method: 'PUT'
  })
}

export const deactivateGroup = () => {
  return axios({
    url: '/api/mock/groups/deactivate',
    method: 'PUT'
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
