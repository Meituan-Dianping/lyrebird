import axios from 'axios'

const addChannelFilters = (url, options) => {
  if (options.channelFilters && options.channelFilters.length > 0) {
    url += '/' + options.channelFilters.join('+')
  }
  return url
}

const addEventId = (url, options) => {
  if (options.eventId) {
    url += '/id/' + options.eventId
  }
  return url
}

const addPage = (url, options) => {
  if (options.page) {
    url += '/page/' + options.page
  }
  return url
}

const addSearchStr = (url, options) => {
  if (options.searchStr && options.searchStr.trim()) {
    var searchStr = options.searchStr.trim().split(/\s+/).join('+')
    url += '/search?q=' + encodeURIComponent(searchStr)
  }
  return url
}

export const getEvent = (options) => {
  let url = '/api/event'
  if (options) {
    url = addChannelFilters(url, options)
    url = addEventId(url, options)
    url = addPage(url, options)
    url = addSearchStr(url, options)
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

export const getDefaultChannelNames = () => {
  return axios({
    url: '/api/channel/default'
  })
}

export const updateChannelFilters = (filters) => {
  return axios({
    url: '/api/channel',
    method: 'POST',
    data: {filters}
  })
}

export const deleteEvents = () => {
  return axios({
    url: '/api/event',
    method: 'DELETE'
  })
}

export const exportSnapshotFromEvent = (data) => {
  return axios({
    url: '/api/snapshot/import',
    method: 'PUT',
    data
  })
}

export const eventFileInfo = () => {
  return axios({
    url: '/api/event/fileinfo',
    method: 'GET'
  })
}
