import * as api from '../api'

export default {
  state: {
    groupDetailDisplayKey: '',
    importGroupId: ''
  },
  mutations: {
    setGroupDetailDisplayKey (state, groupDetailDisplayKey) {
      state.groupDetailDisplayKey = groupDetailDisplayKey
    },
    clearGroupDetailDisplayKey (state) {
      state.groupDetailDisplayKey = ''
    },
    setImportGroupId (state, importGroupId) {
      state.importGroupId = importGroupId
    },
    clearImportGroupId (state) {
      state.importGroupId = ''
    }
  },
  actions: {
    initSnapshotInfo ({ commit }, payload) {
      if (payload.groupId) {
        commit('setImportGroupId', payload.groupId)
      }
      if (payload.displayKey) {
        commit('setGroupDetailDisplayKey', payload.displayKey)
      }
    }
  }
}
