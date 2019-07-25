import axios from 'axios'

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

export const updateGroup = (id, name, parent) => {
    return axios({
        url: '/api/mock',
        method: 'PUT',
        data: { id, name, parent }
    })
}

export const updateData = (data) => {
    return axios({
        url: '/api/data',
        method: 'PUT',
        data
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
