import axios from 'axios'

export const getGroupMap = (options) => {
  let url = '/api/group'
  if (options.labels && options.labels.length > 0) {
    const labelIds = []
    for (const label of options.labels) {
      labelIds.push(label.id)
    }
    url += '/label/' + labelIds.join('+')
  }
  return axios({
    url
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

export const duplicateGroupOrData = (id) => {
  return axios({
    url: '/api/duplicate/' + id,
    method: 'PUT'
  })
}

export const getConflict = (dataId) => {
  return axios({
    url: '/api/conflict/id/' + dataId
  })
}

export const getLabels = () => {
  return axios({
    url: '/api/label'
  })
}

export const createLabels = (label) => {
  return axios({
    url: '/api/label',
    method: 'POST',
    data: { label }
  })
}

export const updateLabel = (label) => {
  return axios({
    url: '/api/label',
    method: 'PUT',
    data: { label }
  })
}

export const deleteLabel = (id) => {
  return axios({
    url: '/api/label',
    method: 'DELETE',
    data: { id }
  })
}

export const getQrcodeImg = (link) => {
  return axios({
    url: '/api/qrcode',
    method: 'POST',
    data: { link }
  })
}

export const importSnapshot = (parentId, snapshotName, snapshotId) => {
  return axios({
    url: '/api/snapshot/import',
    method: 'POST',
    data: { parentId, snapshotName, snapshotId }
  })
}

export const getSnapShotDetail = (id) => {
  return axios({
    url: '/api/snapshot/' + id
  })
}

export const deleteByQuery = (ids) => {
  const query = {
    id: ids
  }
  return axios({
    url: '/api/group',
    method: 'DELETE',
    data: { query }
  })
}

export const getRenderedData = (data) => {
  return axios({
    url: '/api/render',
    method: 'PUT',
    data: {'data': data, 'tojson': true}
  })
}
