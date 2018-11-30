import Vue from 'vue'
import Vuex from 'vuex'
import {getMenu} from '@/api/main'

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
  }
})
