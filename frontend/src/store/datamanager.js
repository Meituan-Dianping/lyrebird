import * as api from '../api'
import { bus } from '@/eventbus'
import {breadthFirstSearch} from 'tree-helper'

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
    groupListOpenNode: new Set(['1c43e48a-3d5f-4989-877a-654a5194d823','9cfe9830-bf85-4db5-95d4-9b020a785aec','0c845846-fd58-4d25-99c8-f1953ac467c7','cf92e8ab-be9d-4e53-afbe-a44d622b641f']),
    dataDetail: {},
    groupDetail: {},
    focusNodeInfo: {},
    copyTarget: null
  },
  mutations: {
    setGroupList(state, groupList) {
      state.groupList = groupList
    },
    setCurrentDataGroup(state, dataGroup) {
      state.currentDataGroup = dataGroup
    },
    setDataList(state, dataList) {
      state.dataList = dataList
    },
    setFoucsData(state, dataId) {
      state.foucsData = dataId
    },
    setSelectedData(state, data) {
      state.selectedData = data
    },
    clearSelectedData(state) {
      state.selectedData = []
    },
    setRule(state, rule) {
      state.editorCache.rule = rule
    },
    setReq(state, req) {
      state.editorCache.req = req
    },
    setReqBody(state, reqBody) {
      state.editorCache.reqBody = reqBody
    },
    setResp(state, resp) {
      state.editorCache.resp = resp
    },
    setRespBody(state, respBody) {
      state.editorCache.respBody = respBody
    },
    setCreateGroupModal(state, payload) {
      state.createGroupModal = payload
    },
    setCreateGroupModalSelectedData(state, dataIdList) {
      state.createGroupModal.selectedDataIdList = dataIdList
    },
    setJsonPath(state, jsonPath) {
      state.jsonPath = jsonPath
    },
    setConflictInfo(state, conflictInfo) {
      state.conflictInfo = conflictInfo
    },
    clearConflictInfo(state) {
      state.conflictInfo = null
    },
    addGroupListOpenNode(state, groupId) {
      state.groupListOpenNode.add(groupId)
    },
    deleteGroupListOpenNode(state, groupId) {
      state.groupListOpenNode.delete(groupId)
    },
    setDataDetail(state, dataDetail) {
      state.dataDetail = dataDetail
    },
    setGroupDetail(state, groupDetail) {
      state.groupDetail = groupDetail
    },
    setFocusNodeInfo(state, focusNodeInfo) {
      state.focusNodeInfo = focusNodeInfo
    },
    setCopyTarget(state, copyTarget) {
      state.copyTarget = copyTarget
    }
  },
  actions: {
    loadDataMap({ state, commit }) {
      api.getGroupMap()
      .then(response => {
        breadthFirstSearch(response.data.data.children, node => {
          if (node && node.type === 'data') {
            node.droppable = false
          }
          if (state.groupListOpenNode.has(node.id)) {
            node.open = true
          } else {
            node.open = false
          }
        })
        commit('setGroupList', response.data.data.children)
      })
    },
    loadGroupDetail({ commit }, payload) {
      api.getGroupDetail(payload.id)
        .then(response => {
          commit('setGroupDetail', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load group ' + payload.name + ' error: ' + error)
        })
    },
    saveDataDetail({ state, dispatch }, dataDetail) {
      let groupName = state.currentDataGroup
      let dataName = state.foucsData
      api.updateDataDetail(groupName, dataName, dataDetail)
        .then(response => {
          dispatch('loadDataDetail', { groupId: groupName, dataId: dataName })
        })
        .catch(error => {
          console.log('Update detail failed', error)
        })
    },
    createGroup({ dispatch }, { groupName, parentId, source }) {
      api.createGroup(groupName, parentId, source)
        .then(response => {
          dispatch('loadDataMap')
          bus.$emit('msg.success', 'Group ' + groupName+' created!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Group ' + groupName + ' created error: ' + error)
        })
    },
    updateDataGroup({ state, commit, dispatch }, { groupId, groupName, parentGroupId }) {
      api.updateGroup(groupId, groupName, parentGroupId)
        .then(response => {
          const groupId = response.data.group_id
          for (const group of state.groupList) {
            if (groupId === group.id) {
              group.name = groupName
              group.parent = parentGroupId
              break
            }
          }
          commit('setCurrentDataGroup', groupId)
          dispatch('loadDataMap', groupId)
        })
    },
    deleteGroup({ state, commit, dispatch }, payload) {
      api.deleteGroup(payload.id).then(response => {
        dispatch('loadDataMap')
        commit('deleteGroupListOpenNode', payload.id)
        commit('setFocusNodeInfo', {})
        if (state.copyTarget && payload.id === state.copyTarget.id) {
          commit('setCopyTarget', null)
        }
        bus.$emit('msg.success', 'Delete Group ' + payload.name)
      })
      .catch(error => {
        bus.$emit('msg.error', 'Delete group ' + payload.name + ' error: ' + error)
      })
    },
    createData({ dispatch }, { dataName, parentId, source }) {
      api.createData(parentId, {
        name: dataName,
        source: source
      })
        .then(response => {
          dispatch('loadDataMap')
          bus.$emit('msg.success', 'Group ' + dataName+' created!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Group ' + dataName + ' created error: ' + error)
        })
    },
    loadDataDetail({ commit }, payload) {
      api.getDataDetail(payload.id)
        .then(response => {
          commit('setDataDetail', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load data ' + payload.name + ' error: ' + error)
        })
    },
    deleteData({ state, commit, dispatch }, payload) {
      api.deleteData(payload.id).then(response => {
        dispatch('loadDataMap', payload.id)
        commit('setFocusNodeInfo', {})
        if (state.copyTarget && payload.id === state.copyTarget.id) {
          commit('setCopyTarget', null)
        }
        bus.$emit('msg.success', 'Delete Data ' + payload.name)
      })
      .catch(error => {
        bus.$emit('msg.error', 'Delete data ' + payload.name + ' error: ' + error)
      })
    },
    loadConflict({ commit }, payload) {
      api.getConflict(payload.id).then(response => {
        commit('setConflictInfo', response.data.data)
        if (response.data.data.length === 0) {
          bus.$emit('msg.success', 'Group ' + payload.name+' has no conflict')
        } else if (response.data.data.length > 0) {
          bus.$emit('msg.error', 'Group ' + payload.name + ' has ' + response.data.data.length + ' conflicts')
        }
      })
      .catch(error => {
        bus.$emit('msg.error', 'Get group ' + payload.name + ' conflicts error: ' + error)
      })
    }
  }
}
