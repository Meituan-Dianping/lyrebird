import * as api from '@/api'
import { bus } from '@/eventbus'

export default {
  state: {
    activatedGroup: {},
    searchStr: '',
    selectedFlows: [],
    selectedIds: [],
    focusedFlow: null,
    focusedFlowDetail: null,
    originFlowList: [],
    recordMode: '',
    flowFilters: [],
    selectedFLowFilter: ''
  },
  mutations: {
    setActivitedGroup (state, group) {
      state.activatedGroup = group
    },
    setSearchStr (state, val) {
      state.searchStr = val
    },
    setSelectedId (state, val) {
      state.selectedIds = val
    },
    clearSelectedId (state) {
      state.selectedIds = []
    },
    setSelectedFlows (state, selectedFlows) {
      state.selectedFlows = selectedFlows
    },
    cleaerSelectedFlows (state) {
      state.selectedFlows = []
    },
    addSelectedFlow (state, flow) {
      state.selectedFlows.push(flow)
    },
    setFocusedFlow (state, flow) {
      state.focusedFlow = flow
    },
    clearFocusedFlow (state) {
      state.focusedFlow = null
    },
    setFocusedFlowDetail (state, flowDetail) {
      state.focusedFlowDetail = flowDetail
    },
    clearFocusedFlowDetail (state) {
      state.focusedFlowDetail = null
    },
    setOriginFlowList (state, originFlowList) {
      state.originFlowList = originFlowList
    },
    setRecordMode (state, recordMode) {
      state.recordMode = recordMode
    },
    setFLowFilters (state, flowFilters) {
      state.flowFilters = flowFilters
    },
    setSelectedFLowFilter (state, selectedFLowFilter) {
      state.selectedFLowFilter = selectedFLowFilter
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
          // selected
          for (const flow of response.data) {
            if (state.selectedIds.includes(flow.id)) {
              flow['_checked'] = true
            }
          }
          // highlight
          for (const flow of response.data) {
            if (flow.id === (state.focusedFlow && state.focusedFlow.id)) {
              flow._highlight = true
              break
            }
          }
          commit('setOriginFlowList', response.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load flow list error: ' + error.data.message)
        })
    },
    saveRecordMode ({ state }) {
      api.setRecordMode(state.recordMode)
        .catch(error => {
          bus.$emit('msg.error', 'Change record mode error: ' + error.data.message)
        })
    },
    loadFlowFilters ({ commit }) {
      api.getFlowFilters()
        .then(response => {
          commit('setFLowFilters', response.data.filters)
          if (response.data.selected_filter) {
            commit('setSelectedFLowFilter', response.data.selected_filter.name)
          }
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load flow filters failed: ' + error.data.message)
        })
    },
    saveFLowFilters ({ dispatch }, name) {
      api.setFLowFilter(name)
        .then(_ => {
          dispatch('loadFlowList')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Change flow filter failed: ' + error.data.message)
        })
    },
    clearInspector ({ commit }, clearTypes) {
      if (clearTypes.includes('Real-time')) {
        api.deleteAllFlow()
        .then(response => { 
          commit('clearSelectedId')
          commit('cleaerSelectedFlows')
        }).catch(error => {
          bus.$emit('msg.error', 'Clear flow error: ' + error.data.message)
          return
        })
      }
      if (clearTypes.includes('Advanced')) {
        api.deleteEvents()
        .then(response => {}).catch(error => {
          bus.$emit('msg.error', 'Clear Advanced error: ' + error.data.message)
          return
        })
      }
      bus.$emit('msg.success', `Clear ${clearTypes.toString()} success!`)
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
          if (state.selectedIds.includes(state.focusedFlow && state.focusedFlow.id)) {
            commit('clearFocusedFlow')
          }
          if (state.selectedIds.includes(state.focusedFlowDetail && state.focusedFlowDetail.id)) {
            commit('clearFocusedFlowDetail')
          }
          commit('clearSelectedId')
          commit('cleaerSelectedFlows')
          bus.$emit('msg.success', selectedIdLength + ' flow deleted!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Delete flow error: ' + error.data.message)
        })
    }
  }
}
