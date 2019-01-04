import axios from 'axios'

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
    url: '/api/flow/'+flowId
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
export const getGroups = () =>{
  return axios({
    url: '/api/mock'
  })
}

export const createGroup = (name) => {
  return axios({
    url: '/api/mock',
    method: 'POST',
    data: {name:name}
  })
}

export const updateGroup = (name) => {
  return axios({
    url: '/api/mock',
    method: 'PUT',
    data: {name:name}
  })
}

export const deleteGroup = (groupId) => {
  return axios({
    url: '/api/mock/'+groupId,
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
export const getDataList = (groupId) =>{
  return axios({
    url: '/api/mock/' + groupId
  })
}

export const createData = (groupId, name) => {
  return axios({
    url: '/api/mock/'+groupId+'/data',
    data:{name:name},
    method: 'POST'
  })
}

export const deleteData = (groupId, ids) => {
  return axios({
    url:'/api/mock/'+groupId+'/data',
    data:{ids:ids},
    method:'DELETE'
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
export const getDataDetail = (groupId, dataId) =>{
  return axios({
    url: '/api/mock/' + groupId + '/data/' + dataId
  })
}

export const updateDataDetail = (groupName, dataName, dataDetail) =>{
  return axios({
    url: '/api/mock/' + groupName + '/data/' + dataName,
    method: 'PUT',
    data: dataDetail
  })
}

/**
Get activated data group ID
*/
export const getActivatedGroup = () =>{
  return axios({
    url: '/api/mock/activated'
  })
}

/**
Activate data group by ID
*/
export const activateGroup = (groupId) =>{
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
