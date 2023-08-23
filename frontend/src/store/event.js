import * as api from '@/api'
import { bus } from '@/eventbus'


export default {
  state: {
    channelNames: [],
    channelFilters: [],
    events: [],
    selectedEventId: null,
    selectedEvent: null,
    eventDetail: '',
    page: null,
    eventSearchStr: '',
    eventFilePath: '',
    eventFileSizeThreshold: '',
    eventFileSize: '',
    eventFileOversized: false
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
    setSelectedEvent (state, selectedEvent) {
      state.selectedEvent = selectedEvent
    },
    setEventDetail (state, eventDetail) {
      state.eventDetail = eventDetail
    },
    setPage (state, page) {
      state.page = page
    },
    setEventSearchStr (state, val) {
      state.eventSearchStr = val
    },
    setEventFilePath (state, val) {
      state.eventFilePath = val
    },
    setEventFileSizeThreshold (state, val) {
      state.eventFileSizeThreshold = val
    },
    setEventFileSize (state, val) {
      state.eventFileSize = val
    },
    setEventFileOversized (state, val) {
      state.eventFileOversized = val
    }
  },
  actions: {
    loadChannelNames ({ commit, dispatch }) {
      api.getDefaultChannelNames()
        .then(response => {
          commit('setChannelNames', response.data.data)
          commit('setChannelFilters', response.data.selected)
          dispatch('updateChannelFilters', response.data.selected)
        })
    },
    loadEvents ({ state, commit }, options = {}) {
      let eventId = options.eventId ? options.eventId : state.selectedEventId
      api.getEvent({ 
        channelFilters: state.channelFilters, 
        eventId, 
        page: options.page,
        searchStr: state.eventSearchStr
       }).then(response => {
        if (response.data.code !== 1000) {
          return
        }
        if (response.data.channel.toString() !== state.channelFilters.toString()) {
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
            bus.$emit('eventListScroll', eventIndex / events.length)
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
      api.updateChannelFilters(filters)
    },
    showNotice ({ dispatch }) {
      dispatch('updateChannelFilters', ['notice'])
    },
    showAll ({ commit, dispatch }) {
      api.getDefaultChannelNames()
        .then(response => {
          let channel = response.data.data
          dispatch('updateChannelFilters', channel)
          commit('setChannelNames', channel)
        })
    },
    exportSnapshotFromEvent ({ state }) {
      bus.$emit('msg.info', 'Exporting snapshot...')
      if (state.selectedEvent.channel != 'snapshot') {
        bus.$emit('msg.destroy')
        bus.$emit('msg.error', 'Please select a snapshot!')
      }
      const eventObj = JSON.parse(state.selectedEvent.content)
      console.log(eventObj);
      api.exportSnapshotFromEvent(eventObj)
        .then(response => {
          bus.$emit('msg.destroy')
          bus.$emit('msg.success', 'Snapshot export! ID: ' + response.data.group_id)
        })
        .catch(error => {
          bus.$emit('msg.destroy')
          bus.$emit('msg.error', 'Snapshot export failed: ' + error.data.message)
        })

    },
    clearEvents ({ commit }) {
      api.deleteEvents()
      .then(response => {
        bus.$emit('msg.success', `Clear events success!`)
        commit('setEvents', [])
      }).catch(error => {
        bus.$emit('msg.error', 'Clear events error: ' + error.data.message)
      })
    }
  }
}
