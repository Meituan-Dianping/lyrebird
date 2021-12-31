import * as api from '../api'
import { bus } from '../eventbus'

export default {
  state: {
    statusBottomLeftList: [],
    statusBottomRightList: [],
    statusTopRightList: [],
    statusBarDetail: null
  },
  mutations: {
    setStatusBottomLeftList(state, statusBottomLeftList) {
      state.statusBottomLeftList = statusBottomLeftList
    },
    setStatusBottomRightList(state, statusBottomRightList) {
      state.statusBottomRightList = statusBottomRightList
    },
    setStatusTopRightList(state, statusTopRightList) {
      state.statusTopRightList = statusTopRightList
    },
    setStatusBarDetail(state, statusBarDetail) {
      state.statusBarDetail = statusBarDetail
    }
  },
  actions: {
    loadAllStatusList( { commit } ) {
      api.getAllStatusList()
        .then(response => {
          commit('setStatusBottomLeftList', response.data.bottom_left)
          commit('setStatusBottomRightList', response.data.bottom_right)
          commit('setStatusTopRightList', response.data.top_right)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load status bar list failed: ' + error.data.message)
        })
    },
    loadStatusBarDetail( { commit }, statusItemId) {
      commit('setStatusBarDetail', null)
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
            'Load status bar' + statusItemId + ' detail failed: ' + error.data.message
          )
        })
    }
  }
}
