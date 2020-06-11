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
    groupDetail: {},
    focusNodeInfo: {},
    pasteTarget: null,
    importSnapshotParentNode: {},
    spinDisplay: false,
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
    setPasteTarget (state, pasteTarget) {
      state.pasteTarget = pasteTarget
    },
    setImportSnapshotParentNode (state, importSnapshotParentNode) {
      state.importSnapshotParentNode = importSnapshotParentNode
    },
    setSpinDisplay (state, spinDisplay) {
      state.spinDisplay = spinDisplay
    },
  },
  actions: {
    loadDataMap ({ state, commit }) {
      api.getGroupMap()
        .then(response => {
          breadthFirstSearch([response.data.data], node => {
            if (node.parent_id === null) {
              commit('addGroupListOpenNode', node.id)
            }
            if (state.groupListOpenNode.has(node.id)) {
              node.open = true
            } else {
              node.open = false
            }
          })
          commit('setGroupList', [response.data.data])
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load data failed: ' + error.data.message)
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
          bus.$emit('msg.error', 'Data ' + payload.name + ' update error: ' + error)
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
          dispatch('loadGroupDetail', payload)
          bus.$emit('msg.success', 'Group ' + payload.name + ' update!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Group ' + payload.name + ' update error: ' + error)
        })
    },
    deleteGroup ({ state, commit, dispatch }, payload) {
      bus.$emit('msg.info', 'Deleting group ' + payload.name + ' ...')
      api.deleteGroup(payload.id)
        .then(response => {
          dispatch('loadDataMap')
          commit('deleteGroupListOpenNode', payload.id)
          commit('setFocusNodeInfo', {})
          if (state.pasteTarget && payload.id === state.pasteTarget.id) {
            commit('setPasteTarget', null)
          }
          bus.$emit('msg.success', 'Delete Group ' + payload.name + ' success!')
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
    loadDataDetail ({ commit }, payload) {
      api.getDataDetail(payload.id)
        .then(response => {
          commit('setDataDetail', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load data ' + payload.name + ' error: ' + error.data.message)
        })
    },
    deleteData ({ state, commit, dispatch }, payload) {
      bus.$emit('msg.info', 'Deleting data ' + payload.name + ' ...')
      api.deleteData(payload.id)
        .then(response => {
          dispatch('loadDataMap', payload.id)
          commit('setFocusNodeInfo', {})
          if (state.pasteTarget && payload.id === state.pasteTarget.id) {
            commit('setPasteTarget', null)
          }
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
    importSnapshot ({ commit, dispatch }, parentNode) {
      api
        .importSnapshot(parentNode)
        .then((res) => {
          commit('setSpinDisplay', false)
          dispatch('loadDataMap')
          bus.$emit('msg.success', res.data.message)
        })
        .catch((err) => {
          commit('setSpinDisplay', false)
          dispatch('loadDataMap');
          bus.$emit('msg.error', err.data.message)
        })
    }
  }
}
