import Vue from 'vue'
import * as api from '../api'
import { bus } from '@/eventbus'
import { breadthFirstSearch } from 'tree-helper'

export default {
  state: {
    groupList: [],
    jsonPath: null,
    conflictInfo: null,
    isLoadConflictInfo: false,
    groupListOpenNode: new Set(),
    dataDetail: {},
    dataDetailFocuedTab: 'info',
    groupDetail: {},
    focusNodeInfo: {},
    pasteTarget: null,
    importSnapshotParentNode: {},
    snapshotName: '',
    labels: [],
    isLoading: false,
    dataListSelectedLabel: [],
    isLabelDisplay: true
  },
  mutations: {
    setGroupList (state, groupList) {
      state.groupList = groupList
    },
    setJsonPath (state, jsonPath) {
      state.jsonPath = jsonPath
    },
    setConflictInfo (state, conflictInfo) {
      state.conflictInfo = conflictInfo
    },
    clearConflictInfo (state) {
      state.conflictInfo = null
    },
    setIsLoadConflictInfo (state, isLoadConflictInfo) {
      state.isLoadConflictInfo = isLoadConflictInfo
    },
    addGroupListOpenNode (state, groupId) {
      state.groupListOpenNode.add(groupId)
      breadthFirstSearch(state.groupList, node => {
        if (node.id === groupId) {
          node.open = true
          // `return false` is used to break loop, no related to search result
          return false
        }
      })
    },
    deleteGroupListOpenNode (state, groupId) {
      state.groupListOpenNode.delete(groupId)
      breadthFirstSearch(state.groupList, node => {
        if (node.id === groupId) {
          node.open = false
          // `return false` is used to break loop, no related to search result
          return false
        }
      })
    },
    setDataDetail (state, dataDetail) {
      state.dataDetail = dataDetail
    },
    setDataDetailFocuedTab (state, dataDetailFocuedTab) {
      state.dataDetailFocuedTab = dataDetailFocuedTab
    },
    setGroupDetail (state, groupDetail) {
      state.groupDetail = groupDetail
    },
    setGroupDetailItem (state, groupDetailItem) {
      Vue.set(state.groupDetail, groupDetailItem.key, groupDetailItem.value)
    },
    deleteGroupDetailItem (state, key) {
      Vue.delete(state.groupDetail, key)
    },
    setFocusNodeInfo (state, focusNodeInfo) {
      state.focusNodeInfo = focusNodeInfo
    },
    setFocusNodeInfoByGroupInfo (state, groupInfo) {
      breadthFirstSearch(state.groupList, node => {
        if (node.id === groupInfo.id) {
          state.focusNodeInfo = node
          // `return false` is used to break loop, no related to search result
          return false
        }
      })
    },
    setPasteTarget (state, pasteTarget) {
      state.pasteTarget = pasteTarget
    },
    setImportSnapshotParentNode (state, importSnapshotParentNode) {
      state.importSnapshotParentNode = importSnapshotParentNode
    },
    setSnapshotName (state, snapshotName) {
      state.snapshotName = snapshotName
    },
    setLabels (state, labels) {
      state.labels = labels
    },
    setIsLoading (state, isLoading) {
      state.isLoading = isLoading
    },
    setDataListSelectedLabel (state, dataListSelectedLabel) {
      state.dataListSelectedLabel = dataListSelectedLabel
    },
    setIsLabelDisplay (state, isLabelDisplay) {
      state.isLabelDisplay = isLabelDisplay
    }
  },
  actions: {
    loadDataMap ({ state, commit }) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          commit('setIsLoading', true)
          api.getGroupMap({labels: state.dataListSelectedLabel})
            .then(response => {
              breadthFirstSearch([response.data.data], node => {
                if (!node.parent_id) {
                  commit('addGroupListOpenNode', node.id)
                }
                if (state.groupListOpenNode.has(node.id)) {
                  node.open = true
                } else {
                  node.open = false
                }
              })
              commit('setGroupList', [response.data.data])
              commit('setIsLoading', false)
            })
            .catch(error => {
              commit('setIsLoading', false)
              bus.$emit('msg.error', 'Load data failed: ' + error.data.message)
            })
          resolve()
        }, 1)
      })
    },
    loadDataLabel ({ commit }) {
      api.getLabels()
        .then(response => {
          commit('setLabels', response.data.labels)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load data label failed: ' + error.data.message)
        })
    },
    loadGroupDetail ({ commit }, payload) {
      api.getGroupDetail(payload.id)
        .then(response => {
          commit('setGroupDetail', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load group ' + payload.name + ' error: ' + error.data.message)
        })
    },
    saveDataDetail ({ dispatch }, payload) {
      api.updateData(payload)
        .then(response => {
          dispatch('loadDataMap')
          dispatch('loadDataDetail', payload)
          bus.$emit('msg.success', 'Data ' + payload.name + ' update!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Data ' + payload.name + ' update error: ' + error.data.message)
        })
    },
    createGroup ({ dispatch }, { groupName, parentId }) {
      if (groupName) {
        api.createGroup(groupName, parentId)
          .then(response => {
            dispatch('loadDataMap')
            bus.$emit('msg.success', 'Group ' + groupName + ' created!')
          })
          .catch(error => {
            bus.$emit('msg.error', 'Group ' + groupName + ' created error: ' + error.data.message)
          })
      } else {
        bus.$emit('msg.error', 'Create group ' + groupName + ' error: ' + 'Group name is required!')
      }
    },
    saveGroupDetail ({ state, commit, dispatch }, payload) {
      api.updateGroup(payload.id, payload)
        .then(response => {
          dispatch('loadDataMap')
          dispatch('loadDataLabel')
          dispatch('loadGroupDetail', payload)
          bus.$emit('msg.success', 'Group ' + payload.name + ' update!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Group ' + payload.name + ' update error: ' + error.data.message)
        })
    },
    deleteGroup ({ state, commit, dispatch }, payload) {
      bus.$emit('msg.loading', 'Deleting group ' + payload.name + ' ...')
      api.deleteGroup(payload.id)
        .then(response => {
          dispatch('loadDataMap')
          commit('deleteGroupListOpenNode', payload.id)
          commit('setFocusNodeInfo', {})
          if (state.pasteTarget && payload.id === state.pasteTarget.id) {
            commit('setPasteTarget', null)
          }
          bus.$emit('msg.destroy')
          bus.$emit('msg.success', 'Delete group ' + payload.name + ' success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Delete group ' + payload.name + ' error: ' + error.data.message)
        })
    },
    createData ({ dispatch }, { dataName, parentId }) {
      if (dataName) {
        api.createData(parentId, {
          name: dataName
        })
          .then(response => {
            dispatch('loadDataMap')
            bus.$emit('msg.success', 'Data ' + dataName + ' created!')
          })
          .catch(error => {
            bus.$emit('msg.error', 'Data ' + dataName + ' created error: ' + error.data.message)
          })
      } else {
        bus.$emit('msg.error', 'Create data ' + dataName + ' error: ' + 'Data name is required!')
      }
    },
    loadDataDetail ({ commit, dispatch }, payload) {
      api.getDataDetail(payload.id)
        .then(response => {
          commit('setDataDetail', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load data ' + payload.name + ' error: ' + error.data.message)
        })
    },
    deleteData ({ state, commit, dispatch }, payload) {
      bus.$emit('msg.loading', 'Deleting data ' + payload.name + ' ...')
      api.deleteData(payload.id)
        .then(response => {
          dispatch('loadDataMap', payload.id)
          commit('setFocusNodeInfo', {})
          if (state.pasteTarget && payload.id === state.pasteTarget.id) {
            commit('setPasteTarget', null)
          }
          bus.$emit('msg.destroy')
          bus.$emit('msg.success', 'Delete Data ' + payload.name + ' success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Delete data ' + payload.name + ' error: ' + error.data.message)
        })
    },
    loadConflict ({ commit }, payload) {
      commit('setIsLoadConflictInfo', true)
      commit('clearConflictInfo')
      api.getConflict(payload.id)
        .then(response => {
          commit('setConflictInfo', response.data.data)
          commit('setIsLoadConflictInfo', false)
          if (response.data.data.length === 0) {
            bus.$emit('msg.success', 'Group ' + payload.name + ' has no conflict')
          } else if (response.data.data.length > 0) {
            bus.$emit('msg.error', 'Group ' + payload.name + ' has ' + response.data.data.length + ' conflicts')
          }
        })
        .catch(error => {
          commit('setIsLoadConflictInfo', false)
          bus.$emit('msg.error', 'Get group ' + payload.name + ' conflicts error: ' + error.data.message)
        })
    },
    cutGroupOrData ({ commit }, payload) {
      api.cutGroupOrData(payload.id)
        .then(response => {
          commit('setPasteTarget', payload)
          bus.$emit('msg.success', payload.type + ' ' + payload.name + ' is waiting for paste')
        })
        .catch(error => {
          bus.$emit('msg.error', payload.type + ' ' + payload.name + ' cut error: ' + error.data.message)
        })
    },
    copyGroupOrData ({ commit }, payload) {
      api.copyGroupOrData(payload.id)
        .then(response => {
          commit('setPasteTarget', payload)
          bus.$emit('msg.success', payload.type + ' ' + payload.name + ' is waiting for paste')
        })
        .catch(error => {
          bus.$emit('msg.error', payload.type + ' ' + payload.name + ' copy error: ' + error.data.message)
        })
    },
    pasteGroupOrData ({ commit, dispatch }, payload) {
      api.pasteGroupOrData(payload.id)
        .then(response => {
          commit('addGroupListOpenNode', payload.id)
          dispatch('loadDataMap')
          bus.$emit('msg.success', payload.type + ' ' + payload.name + ' paste success')
        })
        .catch(error => {
          bus.$emit('msg.error', payload.type + ' ' + payload.name + ' paste error: ' + error.data.message)
        })
    },
    duplicateGroupOrData ({ commit, dispatch }, payload) {
      api.duplicateGroupOrData(payload.id)
        .then(response => {
          console.log('duplicateGroupOrData', response);
          commit('addGroupListOpenNode', payload.parent_id)
          commit('addGroupListOpenNode', response.data.id)
          dispatch('loadDataMap')
        })
        .catch(error => {
          bus.$emit('msg.error', payload.type + ' ' + payload.name + ' duplicate error: ' + error.data.message)
        })
    },
    importSnapshot ({ state, dispatch }) {
      api.importSnapshot(state.importSnapshotParentNode.id, state.snapshotName)
        .then(response => {
          dispatch('loadDataMap')
          bus.$emit('msg.success', 'Import snapshot ' + state.snapshotName + ' success!')
        })
        .catch(error => {
          dispatch('loadDataMap')
          bus.$emit('msg.error', 'Import snapshot ' + state.snapshotName + ' error: ' + error.data.message)
        })
    },
    loadSnapshotName ({ commit }) {
      bus.$emit('msg.loading', 'Loading snapshot ...')
      api.getSnapShotDetail()
        .then((res) => {
          commit('setSnapshotName', res.data.data.name)
        })
        .catch((err) => { 
          bus.$emit('msg.error', 'Load snapshot information error: ' + err.data.message)
        })
    },
    loadIsLabelDisplay ({ commit }) {
      api.getLyrebirdConfig()
        .then(response => {
          if (response.data.hasOwnProperty('mock.data.isLabelDisplay')) {
            commit('setIsLabelDisplay', response.data['mock.data.isLabelDisplay'])
          }
        })
    }
  }
}
