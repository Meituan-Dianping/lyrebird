import axios from 'axios'

const PREFIX = '/plugins/demo/api'

export const loadRequestCount = () => {
    return axios({
        url: PREFIX + '/count'
    })
}

export const resetRequestCount = () => {
    return axios({
        url: PREFIX + '/reset',
        method: 'PUT'
    })
}
