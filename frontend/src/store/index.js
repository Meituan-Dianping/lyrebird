import Vue from 'vue'
import Vuex from 'vuex'
import {getMenu} from '@/api/index'
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
  },
  mutations: {
    setMenu(state, menu){
      state.menu = menu
    }
  },
  actions: {
    loadMenu({commit}){
      getMenu().then(response=>{
        commit('setMenu', response.data.menu)
      })
    }
  }
})
