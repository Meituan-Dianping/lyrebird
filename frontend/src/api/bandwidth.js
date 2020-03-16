import axios from 'axios'

export const getBandwidth = () => {
    let url = '/api/bandwidth'
    return axios({
        url,
        method: 'GET'
    })
}

export const getBandwidthTemplates = () => {
    let url = '/api/bandwidth_templates'
    return axios({
        url,
        method: 'GET'
    })
}

export const updateBandwidth = templateName => {
    let url = '/api/bandwidth'
    return axios({
        url,
        method: 'PUT',
        data: { templateName }
    })
}
