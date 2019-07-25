import * as api from '@/api'
import { bus } from '@/eventbus'

export default {
  state: {
    activatedGroup: null,
    showDataButtons: false,
    searchStr: '',
    selectedIds: [],
    focusedFlow: null,
    focusedFlowDetail: null,
    groupTree: null
  },
  mutations: {
    setActivitedGroup (state, group) {
      state.activatedGroup = group
    },
    showDataButtons: function (state, val) {
      state.showDataButtons = val
    },
    search: function (state, val) {
      state.searchStr = val
    },
    setSelectedId: function (state, val) {
      state.selectedIds = val
    },
    clearSelectedId: function (state) {
      state.selectedIds = []
    },
    setFocusedFlow (state, flow) {
      state.focusedFlow = flow
    },
    setFocusedFlowDetail (state, flowDetail) {
      state.focusedFlowDetail = flowDetail
    }
  },
  actions: {
    loadActivatedGroup ({ commit }) {
      api.getActivatedGroup()
        .then(response => {
          commit('setActivitedGroup', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load activate Group error: ' + error.data.message)
        })
    },
    activateGroup ({ dispatch }, groupId) {
      api.activateGroup(groupId)
        .then(response => {
          dispatch('loadActivatedGroup')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Activate Group ' + groupId + ' error: ' + error.data.message)
        })
    },
    deactivateGroup ({ dispatch }) {
      api.deactivateGroup()
        .then(response => {
          dispatch('loadActivatedGroup')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Deactivate Group error: ' + error.data.message)
        })
    },
    loadFlowDetail ({ commit }, flowId) {
      api.getFlowDetail(flowId)
        .then(response => {
          commit('setFocusedFlowDetail', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load flow ' + flowId + ' error: ' + error.data.message)
        })
    },
    focusFlow ({ commit, dispatch }, flow) {
      commit('setFocusedFlow', flow)
      dispatch('loadFlowDetail', flow.id)
    }
  }
}
