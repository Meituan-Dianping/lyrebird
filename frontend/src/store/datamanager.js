import * as api from '../api'
import { bus } from '@/eventbus'
import {breadthFirstSearch} from 'tree-helper'

export default {
  state: {
    groupList: [],
    currentDataGroup: null,
    dataList: [],
    foucsData: null,
    dataDetail: null,
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
    focusNode: null,
    focusNodeDetail: {
      information: {}
    },
    unshowInfoKey: ['request', 'response', 'children'],
    conflictInfo: null,
    groupListOpenNode: new Set()
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
    setDataDetail(state, dataDetail) {
      state.dataDetail = dataDetail
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
    setFocusNode(state, focusNode) {
      state.focusNode = focusNode
    },
    setFocusNodeDetail(state, dataDetail) {
      if (dataDetail.type !== 'group') {
        state.focusNodeDetail = {
          information : {},
          request: {
            code: dataDetail.request.code,
            headers: dataDetail.request.headers
          },
          requestData: dataDetail.request.data,
          response: {
            code: dataDetail.response.code,
            headers: dataDetail.response.headers
          },
          responseData: dataDetail.response.data
        }
      }
      else {
        state.focusNodeDetail = {
          information : {}
        }
      }
      for (const key in dataDetail) {
        if (state.unshowInfoKey.indexOf(key) === -1 && key.substring(0,1) !== '_') {
          state.focusNodeDetail.information[key] = dataDetail[key]
        }
      }
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
    loadDataDetail({ commit }, payload) {
      commit('setFocusNode', payload.id)
      api.getDataDetail(payload.id)
        .then(response => {
          if (response.data.hasOwnProperty('code') && response.data.code != 1000) {
            console.log('Load detail Failed', response.data)
          } else {
            commit('setDataDetail', response.data.data)
            commit('setFocusNodeDetail', response.data.data)
          }
        })
        .catch(error => {
          console.log('Load detail failed', error)
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
    newDataGroup({ state, commit, dispatch }, { groupName, parentGroupId }) {
      api.createGroup(groupName, parentGroupId)
        .then(response => {
          const groupId = response.data.group_id
          state.groupList.push({
            id: groupId,
            name: groupName,
            parent: parentGroupId
          })
          commit('setCurrentDataGroup', groupId)
          dispatch('loadDataMap', groupId)
        })
        .catch(error => {
          console.error('Create group failed')
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
    deleteGroup({ commit, dispatch }, payload) {
      api.deleteGroup(payload.id).then(response => {
        dispatch('loadDataMap')
        commit('deleteGroupListOpenNode', payload.id)
        commit('setFocusNode', null)
        bus.$emit('msg.success', 'Delete Group ' + payload.name)
      })
      .catch(error => {
        bus.$emit('msg.error', 'Delete group ' + payload.name + ' error: ' + error)
      })
    },
    newData({ dispatch }, { groupId, name }) {
      api.createData(groupId, name)
        .then(response => {
          dispatch('loadDataMap', groupId)
        })
    },
    deleteData({ commit, dispatch }, payload) {
      api.deleteData(payload.id).then(response => {
        dispatch('loadDataMap', payload.id)
        commit('setFocusNode', null)
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
