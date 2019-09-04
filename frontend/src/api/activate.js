import axios from 'axios'

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
