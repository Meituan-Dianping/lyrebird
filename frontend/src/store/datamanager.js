import Vue from 'vue'
import * as api from '../api'
import { bus } from '@/eventbus'

export default {
  state: {
    title: 'Mock Data',
    searchStr: '',
    groupList: [],
    jsonPath: null,
    conflictInfo: null,
    isLoadConflictInfo: false,
    groupListOpenNode: [],
    dataDetail: {},
    dataDetailFocuedTab: 'info',
    groupDetail: {},
    focusNodeInfo: {},
    pasteTarget: null,
    createType: 'group',
    isShownCreateDialog: false,
    isShownDuplicateDialog: false,
    isShownDeleteDialog: false,
    importSnapshotParentNode: {},
    snapshotName: '',
    labels: [],
    isLoading: false,
    isSelectableStatus: false,
    selectedLeaf: [],
    selectedNode: new Set(),
    deleteDialogSource: 'single',
    deleteNode: [],
    dataListSelectedLabel: [],
    isLabelDisplay: true,
    isReloadTreeWhenUpdate: false,
    undisplayedKey: ['children', 'type', 'parent_id'],
    undeletableKey: ['id', 'rule', 'name', 'label', 'category'],
    uneditableKey: ['id', 'rule'],
    stickyTopKey: ['id', 'rule', 'super_id', 'name', 'label'],
    displayCopyKey: ['id']
  },
  mutations: {
    setTitle (state, title) {
      state.title = title
    },
    setSearchStr (state, searchStr) {
      state.searchStr = searchStr
    },
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
    setGroupListOpenNode (state, groupListOpenNode) {
      state.groupListOpenNode = groupListOpenNode
    },
    addGroupListOpenNode (state, groupId) {
      state.groupListOpenNode.push(groupId)
    },
    deleteGroupListOpenNode (state, groupId) {
      let openNodeSet = new Set(state.groupListOpenNode)
      openNodeSet.delete(groupId)
      state.groupListOpenNode = Array.from(openNodeSet)
    },
    setSelectedNode (state, selectedNode) {
      state.selectedNode = selectedNode
    },
    addSelectedNode (state, node) {
      state.selectedNode.add(node)
    },
    deleteSelectedNode (state, node) {
      state.selectedNode.delete(node)
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
    setPasteTarget (state, pasteTarget) {
      state.pasteTarget = pasteTarget
    },
    setCreateType (state, createType) {
      state.createType = createType
    },
    setIsShownCreateDialog (state, isShownCreateDialog) {
      state.isShownCreateDialog = isShownCreateDialog
    },
    setIsShownDuplicateDialog (state, isShownDuplicateDialog) {
      state.isShownDuplicateDialog = isShownDuplicateDialog
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
    setIsSelectableStatus (state, isSelectableStatus) {
      state.isSelectableStatus = isSelectableStatus
    },
    setSelectedLeaf (state, selectedLeaf) {
      state.selectedLeaf = selectedLeaf
    },
    setIsShownDeleteDialog (state, isShownDeleteDialog) {
      state.isShownDeleteDialog = isShownDeleteDialog
    },
    setDeleteDialogSource (state, deleteDialogSource) {
      state.deleteDialogSource = deleteDialogSource
    },
    setDeleteNode (state, deleteNode) {
      state.deleteNode = deleteNode
    },
    setDataListSelectedLabel (state, dataListSelectedLabel) {
      state.dataListSelectedLabel = dataListSelectedLabel
    },
    setIsLabelDisplay (state, isLabelDisplay) {
      state.isLabelDisplay = isLabelDisplay
    },
    setUndisplayedKey (state, undisplayedKey) {
      state.undisplayedKey = undisplayedKey
    },
    setIsReloadTreeWhenUpdate (state, isReloadTreeWhenUpdate) {
      state.isReloadTreeWhenUpdate = isReloadTreeWhenUpdate
    },
    concatUndisplayedKey (state, undisplayedKey) {
      state.undisplayedKey = state.undisplayedKey.concat(undisplayedKey)
    },
    setUneditableKey (state, uneditableKey) {
      state.uneditableKey = uneditableKey
    },
    concatUneditableKey (state, uneditableKey) {
      state.uneditableKey = state.uneditableKey.concat(uneditableKey)
    },
    setUndeletableKey (state, undeletableKey) {
      state.undeletableKey = undeletableKey
    },
    concatUndeletableKey (state, undeletableKey) {
      state.undeletableKey = state.undeletableKey.concat(undeletableKey)
    },
    setStickyTopKey (state, stickyTopKey) {
      state.stickyTopKey = stickyTopKey
    },
    concatStickyTopKey (state, stickyTopKey) {
      state.stickyTopKey = state.stickyTopKey.concat(stickyTopKey)
    }
  },
  actions: {
    loadDataMap ({ state, commit }) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          commit('setIsLoading', true)
          api.getGroupMap({labels: state.dataListSelectedLabel})
            .then(response => {
              commit('addGroupListOpenNode', response.data.data.id)
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
    saveDataDetail ({ state, commit, dispatch }, payload) {
      api.updateData(payload)
        .then(response => {
          dispatch('loadDataDetail', payload)
          if (state.isReloadTreeWhenUpdate) {
            dispatch('loadDataMap')
            commit('setIsReloadTreeWhenUpdate', false)
          }
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
      bus.$emit('msg.loading', `Pasting ${payload.type} ${payload.name} ...`)
      api.pasteGroupOrData(payload.id)
        .then(response => {
          commit('addGroupListOpenNode', payload.id)
          dispatch('loadDataMap')
          bus.$emit('msg.destroy')
          bus.$emit('msg.success', payload.type + ' ' + payload.name + ' paste success')
        })
        .catch(error => {
          bus.$emit('msg.error', payload.type + ' ' + payload.name + ' paste error: ' + error.data.message)
        })
    },
    duplicateGroupOrData ({ commit, dispatch }, payload) {
      bus.$emit('msg.loading', 'Duplicating group ' + payload.name + ' ...')
      api.duplicateGroupOrData(payload.id)
        .then(response => {
          commit('addGroupListOpenNode', payload.parent_id)
          commit('addGroupListOpenNode', response.data.id)
          dispatch('loadDataMap')
          bus.$emit('msg.destroy')
          bus.$emit('msg.info', response.data.message)
        })
        .catch(error => {
          bus.$emit('msg.error', payload.type + ' ' + payload.name + ' duplicate error: ' + error.data.message)
        })
    },
    importSnapshot ({ state, commit, dispatch }, snapshotId) {
      api.importSnapshot(state.importSnapshotParentNode.id, state.snapshotName, snapshotId)
        .then(response => {
          commit('setImportGroupId', response.data.group_id)
          dispatch('loadDataMap')
          bus.$emit('msg.success', 'Import snapshot ' + state.snapshotName + ' success!')
        })
        .catch(error => {
          dispatch('loadDataMap')
          bus.$emit('msg.error', 'Import snapshot ' + state.snapshotName + ' error: ' + error.data.message)
        })
    },
    loadSnapshotDetail ({ commit }, snapshotId) {
      bus.$emit('msg.loading', 'Loading snapshot ...')
      api.getSnapShotDetail(snapshotId)
        .then((res) => {
          commit('setSnapshotName', res.data.data.name)
        })
        .catch((err) => { 
          bus.$emit('msg.error', 'Load snapshot information error: ' + err.data.message)
        })
    },
    deleteByQuery ({ state, commit }, payload) {
      bus.$emit('msg.loading', 'Deleting ' + payload.length + ' items ...')
      api.deleteByQuery(payload)
        .then(_ => {
          commit('setFocusNodeInfo', {})
          commit('setDeleteNode', [])
          commit('setSelectedNode', new Set())
          if (state.pasteTarget && payload.indexOf(state.pasteTarget.id)) {
            commit('setPasteTarget', null)
          }
          bus.$emit('msg.destroy')
          bus.$emit('msg.success', 'Delete ' + payload.length + ' items success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Delete error: ' + error.data.message)
        })
    }
  }
}
