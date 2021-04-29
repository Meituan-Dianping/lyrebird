import * as api from '../api'
import { bus } from '../eventbus'

export default {
  state: {
    statusBarList: null,
    statusBarDetail: null
  },
  mutations: {
    setStatusBarList(state, statusBarList) {
      state.statusBarList = statusBarList
    },
    setStatusBarDetail(state, statusBarDetail) {
      state.statusBarDetail = statusBarDetail
    }
  },
  actions: {
    loadStatusBarList(context) {
      api
        .getStatusBarList()
        .then(response => {
          if (response.data.code === 1000) {
            context.commit('setStatusBarList', response.data.data)
          } else {
            bus.$emit('msg.error', 'loadStatusBar failed')
          }
        })
        .catch(error => {
          bus.$emit('msg.error', 'loadStatusBar failed ' + error.data.message)
        })
    },
    loadStatusBarDetail({ commit }, statusItemId) {
      commit('setStatusBarDetail', [{
        id: "",
        src: "Loading",
        type: "TextMenuItem"
      }])
      api.getStatusBarDetail(statusItemId)
        .then(response => {
          if (response.data.code === 1000) {
            commit('setStatusBarDetail', response.data.data)
          } else {
            bus.$emit('msg.error', 'loadStatusBarDetail failed')
          }
        })
        .catch(error => {
          bus.$emit(
            'msg.error',
            'loadStatusBarDetail failed ' + error.data.message
          )
        })
    }
  }
}
