import * as api from '../api'
<<<<<<< HEAD
import { bus } from '@/eventbus'
=======
>>>>>>> d79aa5095057397e4c27c19bc678171b4d44c721
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
    conflictInfo : null
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
    }
  },
  actions: {
    loadDataMap({ commit }) {
      api.getDataMap()
      .then(response => {
        breadthFirstSearch(response.data.data.children, node => {
          if (node && node.type === 'data') {
            node.droppable = false
          }
          node.open = false
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
    deleteDataGroup({ commit, dispatch }, groupId) {
      api.deleteGroup(groupId)
        .then(response => {
          commit('setCurrentDataGroup', null)
          dispatch('loadDataMap')
        })
    },
    newData({ dispatch }, { groupId, name }) {
      api.createData(groupId, name)
        .then(response => {
          dispatch('loadDataMap', groupId)
        })
    },
    deleteData({ state, dispatch }, groupId) {
      let ids = []
      for (const data of state.selectedData) {
        ids.push(data.id)
      }
      api.deleteData(groupId, ids).then(response => {
        dispatch('loadDataMap', groupId)
      })
    },
    loadConflict({ commit }, groupId) {
      api.getConflict(groupId).then(response => {
<<<<<<< HEAD
        if (response.data.code === 1000) {
          commit('setConflictInfo', response.data.data)
          console.log('bus', bus);
          bus.$emit('msg.success', 'Get conflict reporter success')
        } else {
          bus.$emit('msg.error', 'Get conflict reporter error: ' + response.message)
        }
=======
        commit('setConflictInfo', response.data.data)
>>>>>>> d79aa5095057397e4c27c19bc678171b4d44c721
      })
    }
  }
}
