import Vue from 'vue'
import Vuex from 'vuex'
import {getMenu, getStatus} from '@/api/index'
import inspector from '@/store/inspector'
import dataManager from '@/store/datamanager'
import plugin from '@/store/plugin'


Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    inspector,
    dataManager,
    plugin
  },
  state: {
    menu: null,
    status: null
  },
  mutations: {
    setMenu(state, menu){
      state.menu = menu
    },
    setStatus(state, status){
      state.status = status
    }
  },
  actions: {
    loadMenu({commit}){
      getMenu().then(response=>{
        commit('setMenu', response.data.menu)
      })
    },
    loadStatus({commit}){
      getStatus().then(response=>{
        commit('setStatus', response.data)
      })
    }
  }
})
