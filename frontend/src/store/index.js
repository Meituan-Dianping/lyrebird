import Vue from 'vue'
import Vuex from 'vuex'
import {getMenu} from '@/api/main'
import inspector from './inspector'
import dataManager from './datamanager'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    inspector,
    dataManager
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
