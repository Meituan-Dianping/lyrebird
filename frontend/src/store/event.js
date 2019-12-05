import * as api from '@/api'
import { bus } from '@/eventbus'


export default {
  state: {
    channelNames: [],
    channelFilters: ['flow', 'notice', 'page', 'android.crash', 'ios.crash'],
    events: [],
    selectedEventId: null,
    eventDetail: '',
    page: null
  },
  mutations: {
    setChannelNames (state, channelNames) {
      state.channelNames = channelNames
    },
    setChannelFilters (state, filters) {
      state.channelFilters = filters
    },
    setEvents (state, events) {
      state.events = events
    },
    setSelectedEventId (state, eventId) {
      state.selectedEventId = eventId
    },
    setEventDetail (state, eventDetail) {
      state.eventDetail = eventDetail
    },
    setPage (state, page) {
      state.page = page
    }
  },
  actions: {
    loadChannelNames ({ commit }) {
      // Filter out the target channel
      commit('setChannelNames', ['flow', 'notice', 'page', 'android.crash', 'ios.crash'])
    },
    loadEvents ({ state, commit }, options = {}) {
      let eventId = options.eventId ? options.eventId : state.selectedEventId
      api.getEvent({ channelFilters: state.channelFilters, eventId, page: options.page }).then(response => {
        if (response.data.code !== 1000) {
          return
        }
        let events = response.data.events
        if (eventId) {
          let eventIndex = events.findIndex(e => e.event_id === eventId)
          if (eventIndex >= 0) {
            let event = events[eventIndex]
            event._highlight = true
            const prettyJson = JSON.stringify(JSON.parse(event.content), null, 2)
            commit('setEventDetail', prettyJson)
            commit('setSelectedEventId', event.event_id)
            bus.$emit('eventLitScroll', eventIndex / events.length)
          }
        }
        commit('setEvents', events)
        commit('setPage', {
          index: response.data.page, count: response.data.page_count, size: response.data.page_size
        })
      }
      )
    },
    updateChannelFilters ({ commit, dispatch }, filters) {
      commit('setChannelFilters', filters)
      dispatch('loadEvents')
    },
    showNotice ({ dispatch }) {
      dispatch('updateChannelFilters', ['notice'])
    },
    showAll ({ dispatch }) {
      dispatch('updateChannelFilters', ['flow', 'notice', 'page', 'android.crash', 'ios.crash'])
    }
  }
}
