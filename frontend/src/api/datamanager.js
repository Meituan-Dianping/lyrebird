import axios from 'axios'

export const getGroupMap = () => {
  return axios({
    url: '/api/group'
  })
}

export const getGroupDetail = (groupId) => {
  return axios({
    url: '/api/group/' + groupId
  })
}

export const createGroup = (name, parentId) => {
  return axios({
    url: '/api/group',
    method: 'POST',
    data: { name, 'parent_id': parentId }
  })
}

export const deleteGroup = (groupId) => {
  return axios({
    url: '/api/group/' + groupId,
    method: 'DELETE'
  })
}

export const updateGroup = (id, data) => {
  return axios({
    url: '/api/group',
    method: 'PUT',
    data: { id, data }
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
    data: { data, 'parent_id': parentId }
  })
}

export const deleteData = (dataId) => {
  return axios({
    url: '/api/data/' + dataId,
    method: 'DELETE'
  })
}

export const updateData = (data) => {
  return axios({
    url: '/api/data',
    method: 'PUT',
    data
  })
}

export const cutGroupOrData = (id) => {
  return axios({
    url: '/api/cut/' + id,
    method: 'PUT'
  })
}

export const copyGroupOrData = (id) => {
  return axios({
    url: '/api/copy/' + id,
    method: 'PUT'
  })
}

export const pasteGroupOrData = (id) => {
  return axios({
    url: '/api/paste/' + id,
    method: 'PUT'
  })
}

export const getConflict = (dataId) => {
  return axios({
    url: '/api/conflict/id/' + dataId
  })
}

export const getQrcodeImg = (link) => {
  return axios({
    url: '/api/qrcode',
    method: 'POST',
    data: { link }
  })
}

export const importSnapshot = parentNode => {
  return axios({
    url: '/api/snapshot/import',
    method: 'POST',
    data: { parentNode },
  });
}
