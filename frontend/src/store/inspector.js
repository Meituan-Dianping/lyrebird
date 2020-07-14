import * as api from '@/api'
import { bus } from '@/eventbus'

export default {
  state: {
    activatedGroup: {},
    showDataButtons: false,
    searchStr: '',
    selectedIds: [],
    focusedFlow: null,
    focusedFlowDetail: null,
    groupTree: null,
    currentFlowList: [],
    originFlowList: [],
    recordMode: ''
  },
  mutations: {
    setActivitedGroup (state, group) {
      state.activatedGroup = group
    },
    showDataButtons (state, val) {
      state.showDataButtons = val
    },
    search (state, val) {
      state.searchStr = val
    },
    setSelectedId (state, val) {
      state.selectedIds = val
    },
    clearSelectedId (state) {
      state.selectedIds = []
    },
    setFocusedFlow (state, flow) {
      state.focusedFlow = flow
    },
    setFocusedFlowDetail (state, flowDetail) {
      state.focusedFlowDetail = flowDetail
    },
    setFlowList (state, currentFlowList) {
      state.currentFlowList = currentFlowList
    },
    setOriginFlowList (state, originFlowList) {
      state.originFlowList = originFlowList
    },
    setRecordMode (state, recordMode) {
      state.recordMode = recordMode
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
    activateGroup ({ dispatch }, payload) {
      api.activateGroup(payload.id)
        .then(response => {
          dispatch('loadActivatedGroup')
          bus.$emit('msg.success', 'Group ' + payload.name + ' activated!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Activate group ' + payload.name + ' error: ' + error.data.message)
        })
    },
    deactivateGroup ({ dispatch }) {
      api.deactivateGroup()
        .then(response => {
          dispatch('loadActivatedGroup')
          bus.$emit('msg.success', 'Deactivate all groups!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Deactivate groups error: ' + error.data.message)
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
    },
    loadFlowList ({ state, commit }) {
      api.getFlowList()
        .then(response => {
          commit('setFlowList', response.data)
          // commit('setOriginFlowList', [])
          let originFlowListTemp = []
          const selectedIds = state.selectedIds
          for (const flow of response.data) {
            if (selectedIds.includes(flow.id)) {
              flow['_checked'] = true
            }
            originFlowListTemp.push(flow)
            commit('setOriginFlowList', originFlowListTemp)
          }
        })
        .catch(error => {
          console.log('error', error)
          bus.$emit('msg.error', 'Inspector: reload failed' + ' error: ' + error.data.message)
        })
    },
    loadRecordMode ({ commit, state }) {
      api.getRecordMode()
        .then(response => {
          commit('setRecordMode', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Switch start/record failed' + 'error:' + error.data.message)
        })
    },
    saveRecordMode ({ commit }, mode) {
      api.setRecordMode(mode)
        .then(response => {
          commit('setRecordMode', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Switch start/record failed' + 'error:' + error.data.message)
        })
    },
    clearFlows () {
      api.deleteAllFlow(null)
        .then(response => {
          bus.$emit('msg.success', 'HTTP flow cleared')
        })
        .catch(error => {
          bus.$emit('msg.error', 'clear failed' + 'error:' + error.data.message)
        })
    },
    saveSelectedFlow ({ state }, group) {
      api.saveSelectedFlow(state.selectedIds, group)
        .then(response => {
          bus.$emit('msg.success', 'HTTP flow saved')
          console.log('POST flow', state.selectedIds, response)
        })
        .catch(error => {
          console.log('error', error);
          bus.$emit('msg.error', 'Save HTTP flow failed' + ' error:' + error.data.message)
        })
    },
    deleteSelectedFlow ({ state, commit }) {
      api.deleteSelectedFlow(state.selectedIds)
        .then(response => {
          console.log('DEL flow', state.selectedIds, response)
          commit('clearSelectedId')
        })
    }
  }
}

