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
import settings from '@/store/settings'
import snapshot from '@/store/snapshot'
import statusbar from '@/store/statusbar'
import { bus } from '@/eventbus'

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
    settings,
    snapshot,
    statusbar
  },
  state: {
    menu: null,
    status: null,
    manifest: null,
    activeMenuItem: null,
    activeMenuItemIndex: null,
    ipList: [],
    isShownDialogChangeIp: false
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
    setActiveMenuItem (state, activeMenuItem) {
      state.activeMenuItem = activeMenuItem
    },
    setActiveMenuItemIndex (state, activeMenuItemIndex) {
      state.activeMenuItemIndex = activeMenuItemIndex
    },
    setIpList (state, ipList) {
      state.ipList = ipList
    },
    setIsShownDialogChangeIp (state, isShownDialogChangeIp) {
      state.isShownDialogChangeIp = isShownDialogChangeIp
    }
  },
  actions: {
    loadMenu ({ commit }) {
      api.getMenu().then(response => {
        commit('setMenu', response.data.menu)
        commit('setActiveMenuItem', response.data.activeMenuItem)
        commit('setActiveMenuItemIndex', response.data.activeMenuItemIndex)
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
        .then(_ => {
          commit('setActiveMenuItem', activeMenuItem)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load ' + activeMenuItem.title + ' error: ' + error)
        })
    },
  }
})
