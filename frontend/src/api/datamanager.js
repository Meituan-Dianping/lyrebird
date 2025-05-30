import axios from 'axios'
import { stringify } from 'lossless-json'

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

// V2 getGroupMap
export const getMockDataByOpenNodes = (options) => { 
  return axios({
    url: '/api/search/group?search_str=',
    method: 'POST',
    data: { 'open_nodes': options.openNodes, 'reset': options.reset }
  })
}

export const getGroupDetail = (groupId) => {
  return axios({
    url: '/api/group/' + groupId
  })
}

export const getGroupChildren = (groupId) => {
  return axios({
    url: '/api/group/' + groupId + '?childrenOnly=true'
  })
}

export const createGroup = (name, parentId) => {
  return axios({
    url: '/api/group',
    method: 'POST',
    headers: {
      'Content-Type': 'text/plain'
    },
    data: stringify({ name, 'parent_id': parentId })
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
    headers: {
      'Content-Type': 'text/plain'
    },
    data: stringify({ id, data })
  })
}

export const updateByQuery = (ids, data, tab) => {
  const query = {
    id: ids,
    tab
  }
  return axios({
    url: '/api/group',
    method: 'PUT',
    data: { query, data }
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
    headers: {
      'Content-Type': 'text/plain'
    },
    data: stringify({ data, 'parent_id': parentId })
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
    headers: {
      'Content-Type': 'text/plain'
    },
    data: stringify(data)
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

export const deleteTempMockDataByQuery = (ids, parentId) => {
  const query = {
    id: ids,
    'parent_id': parentId
  }
  return axios({
    url: '/api/group',
    method: 'DELETE',
    data: { query }
  })
}

export const deleteByQuery = (dataIds, groupIds) => {
  const query = {
    'data': dataIds,
    'groups': groupIds
  }
  return axios({
    url: '/api/group',
    method: 'DELETE',
    data: { query }
  })
}

export const saveTreeView = (tree) => { 
  return axios({
    url: '/api/tree',
    method: 'POST',
    data: { tree }
  })
}

export const getTreeView = () => { 
  return axios({
    url: '/api/tree',
    method: 'GET'
  })
}

export const saveTreeViewOpenNodes = (openNodes) => { 
  return axios({
    url: '/api/tree/open-nodes',
    method: 'POST',
    data: { openNodes }
  })
}

export const getTreeViewOpenNodes = () => { 
  return axios({
    url: '/api/tree/open-nodes',
    method: 'GET'
  })
}

