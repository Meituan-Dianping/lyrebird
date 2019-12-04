import axios from 'axios'


export const getEvent = (options) => {
    let url = '/api/event'
    if (options && options.hasOwnProperty('channelFilters') && options.channelFilters.length > 0) {
        url += '/' + options.channelFilters.join('+')
    }
    if (options && options.hasOwnProperty('eventId') && options.eventId) {
        url += '/id/' + options.eventId
    }
    if (options && options.hasOwnProperty('page') && options.page) {
        url += '/page/' + options.page
    }
    return axios({
        url
    })
}

export const getChannelNames = () => {
    return axios({
        url: '/api/channel'
    })
}
