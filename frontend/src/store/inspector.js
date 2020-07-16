import * as api from '@/api'
import { bus } from '@/eventbus'

export default {
  state: {
    activatedGroup: {},
    itemSeleted: false,
    searchStr: '',
    selectedIds: [],
    focusedFlow: null,
    focusedFlowDetail: null,
    currentFlowList: [],
    recordMode: ''
  },
  mutations: {
    setActivitedGroup (state, group) {
      state.activatedGroup = group
    },
    itemSeleted (state, val) {
      state.itemSeleted = val
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
    setCurrentFlowList (state, currentFlowList) {
      state.currentFlowList = currentFlowList
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
          for (const flow of response.data) {
            if (state.selectedIds.includes(flow.id)) {
              flow['_checked'] = true
            }
          }
          commit('setCurrentFlowList', response.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load flow list error: ' + error.data.message)
        })
    },
    loadRecordMode ({ commit, state }) {
      api.getRecordMode()
        .then(response => {
          commit('setRecordMode', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load record mode error: ' + error.data.message)
        })
    },
    saveRecordMode ({ state }) {
      api.setRecordMode(state.recordMode)
        .catch(error => {
          bus.$emit('msg.error', 'Change record mode error: ' + error.data.message)
        })
    },
    clearFlows () {
      api.deleteAllFlow()
        .then(response => {
          bus.$emit('msg.success', 'Clear flow success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Clear flow error: ' + error.data.message)
        })
    },
    saveSelectedFlow ({ state }) {
      api.saveSelectedFlow(state.selectedIds)
        .then(response => {
          bus.$emit('msg.success', state.selectedIds.length + ' flow saved!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Save flow error: ' + error.data.message)
        })
    },
    deleteSelectedFlow ({ state, commit }) {
      api.deleteSelectedFlow(state.selectedIds)
        .then(response => {
          let selectedIdLength = state.selectedIds.length
          commit('clearSelectedId')
          bus.$emit('msg.success', selectedIdLength + ' flow deleted!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Delete flow error: ' + error.data.message)
        })
    }
  }
}
