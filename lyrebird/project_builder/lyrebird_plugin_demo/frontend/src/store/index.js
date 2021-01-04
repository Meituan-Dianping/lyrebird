import Vue from 'vue'
import Vuex from 'vuex'
import * as apis from '@/apis'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    requestList: []
  },
  mutations: {
    setRequestList(state, requestList) {
      state.requestList = requestList
    }
  },
  actions: {
    resetRequestReset(context) {
      apis.resetRequestReset().then(response => {
        if (response.data.code !== 1000) {
          console.error('resetRequestReset failed', response.data)
          return
        }
      })
    },
    reloadReqestList(context) {
      apis
        .loadRequestList()
        .then(response => {
          if (response.data.code !== 1000) {
            console.error('reloadReqestList failed', response.data)
            return
          }
          let requestList = response.data.requestList
          context.commit('setRequestList', requestList)
        })
        .catch(error => {
          console.error('reloadReqestList failed', error)
        })
    }
  },
  modules: {}
})
