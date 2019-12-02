import Vue from 'vue'
import Vuex from 'vuex'
import * as api from '@/api'
import inspector from '@/store/inspector'
import dataManager from '@/store/datamanager'
import plugin from '@/store/plugin'
import notice from '@/store/notice'
import checker from '@/store/checker'
import event from '@/store/event'


Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    inspector,
    dataManager,
    plugin,
    notice,
    checker,
    event
  },
  state: {
    menu: null,
    status: null,
    manifest: null,
    activeName: null
  },
  mutations: {
    setMenu (state, menu) {
      state.menu = menu
    },
    setStatus (state, status) {
      state.status = status
    },
    setManifest (state, manifest) {
      state.manifest = manifest
    },
    setActiveName (state, activeName) {
      state.activeName = activeName
    }
  },
  actions: {
    loadMenu ({ commit }) {
      api.getMenu().then(response => {
        commit('setMenu', response.data.menu)
      })
    },
    loadStatus ({ commit }) {
      api.getStatus().then(response => {
        commit('setStatus', response.data)
      })
    },
    loadManifest ({ commit }) {
      api.getManifest().then(response => {
        commit('setManifest', response.data.manifest)
      })
    }
  }
})
