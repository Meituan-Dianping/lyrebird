import Vue from 'vue'
import Vuex from 'vuex'
import * as apis from '@/apis'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    lastRequestURL: null,
    requestCount: 0
  },
  mutations: {
    setRequestCount (state, count) {
      state.requestCount = count
    },
    setLastRequestURL (state, url) {
      state.lastRequestURL = url
    }
  },
  actions: {
    reloadReqestCount (context) {
      apis.loadRequestCount().then(response => {
        if (response.data.code !== 1000) {
          console.error('Load request count failed', response.data)
          return
        }
        let count = response.data.count
        let url = response.data.last_request
        context.commit('setRequestCount', count)
        context.commit('setLastRequestURL', url)
      }).catch(error => {
        console.error('Load request count failed', error)
      })
    },
    resetRequestCount (context) {
      apis.resetRequestCount().then(response => {
        if (response.data.code !== 1000) {
          console.error('Reset failed', response.data)
          return
        }
        context.commit('setRequestCount', 0)
        context.commit('setLastRequestURL', null)
      }).cache(error => {
        console.error('Reset failed', error)
      })
    }
  },
  modules: {
  }
})
