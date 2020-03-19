import Vue from 'vue'
import Vuex from 'vuex'
import * as api from '@/api'
import inspector from '@/store/inspector'
import dataManager from '@/store/datamanager'
import plugin from '@/store/plugin'
import notice from '@/store/notice'
import checker from '@/store/checker'
import event from '@/store/event'
import bandwidth from '@/store/bandwidth'
import statusbar from '@/store/statusbar'


Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    inspector,
    dataManager,
    plugin,
    notice,
    checker,
    event,
    bandwidth,
    statusbar
  },
  state: {
    menu: null,
    status: null,
    manifest: null,
    activeName: null,
    activeMenuItem: null
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
    },
    setActiveMenuItem (state, activeMenuItem) {
      state.activeMenuItem = activeMenuItem
    }
  },
  actions: {
    loadMenu ({ commit }) {
      api.getMenu().then(response => {
        commit('setMenu', response.data.menu)
        commit('setActiveMenuItem', response.data.activeMenuItem)
        commit('setActiveName', response.data.activeName)
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
    },
    updateActiveMenuItem ({ commit }, activeMenuItem) {
      api.setActiveMenuItem(activeMenuItem)
        .then(response => {
          commit('setActiveMenuItem', response.data.activeMenuItem)
          commit('setActiveName', response.data.activeName)
        })
        .catch(error => console.log(error))
    },
  }
})
