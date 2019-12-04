import axios from 'axios'


export const getEvent = (options) => {
    let url = '/api/event'
    if (!options) {
        return axios({ url })
    }

    if (options.channelFilters && options.channelFilters.length > 0) {
        url += '/' + options.channelFilters.join('+')
    }
    if (options.eventId) {
        url += '/id/' + options.eventId
    }
    if (options.page) {
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
