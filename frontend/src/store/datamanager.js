import * as api from '../api'
import { bus } from '@/eventbus'
import { breadthFirstSearch } from 'tree-helper'

export default {
  state: {
    groupList: [],
    currentDataGroup: null,
    dataList: [],
    foucsData: null,
    selectedData: [],
    editorCache: {
      rule: '',
      req: '',
      reqBody: '',
      resp: '',
      respBody: ''
    },
    createGroupModal: {
      parentGroupId: null,
      parentDataList: [],
      selectedDataIdList: []
    },
    jsonPath: null,
    conflictInfo: null,
    isLoadConflictInfo: false,
    groupListOpenNode: new Set(),
    dataDetail: {},
    groupDetail: {},
    focusNodeInfo: {},
    copyTarget: null
  },
  mutations: {
    setGroupList (state, groupList) {
      state.groupList = groupList
    },
    setCurrentDataGroup (state, dataGroup) {
      state.currentDataGroup = dataGroup
    },
    setDataList (state, dataList) {
      state.dataList = dataList
    },
    setFoucsData (state, dataId) {
      state.foucsData = dataId
    },
    setSelectedData (state, data) {
      state.selectedData = data
    },
    clearSelectedData (state) {
      state.selectedData = []
    },
    setRule (state, rule) {
      state.editorCache.rule = rule
    },
    setReq (state, req) {
      state.editorCache.req = req
    },
    setReqBody (state, reqBody) {
      state.editorCache.reqBody = reqBody
    },
    setResp (state, resp) {
      state.editorCache.resp = resp
    },
    setRespBody (state, respBody) {
      state.editorCache.respBody = respBody
    },
    setCreateGroupModal (state, payload) {
      state.createGroupModal = payload
    },
    setCreateGroupModalSelectedData (state, dataIdList) {
      state.createGroupModal.selectedDataIdList = dataIdList
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
    },
    deleteGroupListOpenNode (state, groupId) {
      state.groupListOpenNode.delete(groupId)
    },
    setDataDetail (state, dataDetail) {
      state.dataDetail = dataDetail
    },
    setGroupDetail (state, groupDetail) {
      state.groupDetail = groupDetail
    },
    setGroupDetailItem (state, groupDetailItem) {
      state.groupDetail[groupDetailItem.key] = groupDetailItem.value
    },
    deleteGroupDetailItem (state, key) {
      // trigger object groupDetail's set method 
      state.groupDetail[key] = ''
      delete state.groupDetail[key]
    },
    setFocusNodeInfo (state, focusNodeInfo) {
      state.focusNodeInfo = focusNodeInfo
    },
    setCopyTarget (state, copyTarget) {
      state.copyTarget = copyTarget
    }
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
    saveDataDetail ({ state, dispatch }, dataDetail) {
      api.updateData(dataDetail)
        .then(response => {
          dispatch('loadDataDetail', dataDetail)
        })
        .catch(error => {
          console.log('Update detail failed', error)
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
      bus.$emit('msg.info', 'Updating group ' + payload.name + ' ...')
      api.updateGroup(payload.id, payload)
        .then(response => {
          dispatch('loadDataMap')
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
          if (state.copyTarget && payload.id === state.copyTarget.id) {
            commit('setCopyTarget', null)
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
          if (state.copyTarget && payload.id === state.copyTarget.id) {
            commit('setCopyTarget', null)
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
      api.getConflict(payload.id).then(response => {
        commit('setConflictInfo', response.data.data)
        commit('setIsLoadConflictInfo', false)
        if (response.data.data.length === 0) {
          bus.$emit('msg.success', 'Group ' + payload.name + ' has no conflict')
        } else if (response.data.data.length > 0) {
          bus.$emit('msg.error', 'Group ' + payload.name + ' has ' + response.data.data.length + ' conflicts')
        }
      })
        .catch(error => {
          bus.$emit('msg.error', 'Get group ' + payload.name + ' conflicts error: ' + error.data.message)
        })
    },
    copyGroupOrData ({ commit }, payload) {
      api.copyGroupOrData(payload.id)
        .then(response => {
          commit('setCopyTarget', payload)
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
    }
  }
}
