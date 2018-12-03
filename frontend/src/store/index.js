import Vue from 'vue'
import Vuex from 'vuex'
import {getMenu} from '@/api/index'
import dataManager from '@/store/datamanager'

Vue.use(Vuex)

export default new Vuex.Store({
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
  },
  modules:{
    dataManager
  }
})
