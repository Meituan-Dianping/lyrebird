import Vue from 'vue'
import * as api from '../api'
import { bus } from '@/eventbus'

export default {
  state: {
    title: 'Mock Data',
    treeSearchStr: '',
    groupList: [],
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
    isShownNodeMenu: false,
    shownNodeMenuPosition: null,
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
    isDisplayConfiguration: false,
    isLoadTreeAsync: false,
    isReloadTreeWhenUpdate: false,
    undisplayedKey: ['children', 'type', 'parent_id', 'abs_parent_path', 'parent', 'link'],
    undeletableKey: ['id', 'rule', 'name', 'label', 'category', 'super_by'],
    uneditableKey: ['id', 'rule', 'super_by'],
    stickyTopKey: ['id', 'rule', 'super_id', 'name', 'label', 'super_by'],
    displayCopyKey: ['id'],
    treeUndeletableId: [],
    temporaryMockDataList: [],
    tempGroupId: 'tmp_group',
  },
  mutations: {
    setTitle (state, title) {
      state.title = title
    },
    setTreeSearchStr (state, treeSearchStr) {
      state.treeSearchStr = treeSearchStr
    },
    setGroupList (state, groupList) {
      state.groupList = groupList
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
    setIsShownNodeMenu (state, isShownNodeMenu) {
      state.isShownNodeMenu = isShownNodeMenu
    },
    setShownNodeMenuPosition (state, shownNodeMenuPosition) {
      state.shownNodeMenuPosition = shownNodeMenuPosition
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
    setIsDisplayConfiguration (state, isDisplayConfiguration) {
      state.isDisplayConfiguration = isDisplayConfiguration
    },
    setIsTreeLoadAsync (state, isLoadTreeAsync) {
      state.isLoadTreeAsync = isLoadTreeAsync
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
    },
    concatTreeUndeletableId (state, treeUndeletableId) {
      state.treeUndeletableId = state.treeUndeletableId.concat(treeUndeletableId)
    },
    setTemporaryMockDataList (state, val) {
      state.temporaryMockDataList = val
    },
  },
  actions: {
    loadDataMap ({ state, commit }) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          commit('setIsLoading', true)
          commit('setGroupListOpenNode', [])
          if (state.isLoadTreeAsync) {
            api.getGroupMap({labels: state.dataListSelectedLabel})
              .then(response => {
                commit('setGroupList', [response.data.data])
                commit('concatTreeUndeletableId', response.data.data.id)

                api.getGroupChildren(response.data.data.id)
                  .then(r => {
                    state.groupList[0].children = []
                    state.groupList[0].children.push(...r.data.data)
                    commit('addGroupListOpenNode', response.data.data.id)
                    commit('setIsLoading', false)
                  })
                  .catch(error => {
                    bus.$emit('msg.error', 'Load group ' + state.groupList[0].name + ' children error: ' + error)
                    commit('setIsLoading', false)
                  })

                commit('setIsLoading', false)
              })
              .catch(error => {
                commit('setIsLoading', false)
                bus.$emit('msg.error', 'Load data failed: ' + error.data.message)
              })
          } else {
            api.getGroupMap({labels: state.dataListSelectedLabel})
              .then(response => {
                commit('addGroupListOpenNode', response.data.data.id)
                commit('setGroupList', [response.data.data])
                commit('concatTreeUndeletableId', response.data.data.id)
                commit('setIsLoading', false)
              })
              .catch(error => {
                commit('setIsLoading', false)
                bus.$emit('msg.error', 'Load data failed: ' + error.data.message)
              })
          }
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
      bus.$emit('msg.loading', 'Updating group ' + payload.name + ' ...')
      api.updateGroup(payload.id, payload)
        .then(response => {
          if (state.isReloadTreeWhenUpdate) {
            dispatch('loadDataMap')
            dispatch('loadDataLabel')
            commit('setIsReloadTreeWhenUpdate', false)
          }
          dispatch('loadGroupDetail', payload)
          bus.$emit('msg.destroy')
          if (response.data.message && response.data.message.length > 0) {
            bus.$emit('msg.info', response.data.message)
          } else {
            bus.$emit('msg.success', 'Group ' + payload.name + ' update!')
          }
        })
        .catch(error => {
          bus.$emit('msg.error', 'Group ' + payload.name + ' update error: ' + error.data.message)
        })
    },
    sendGroupDetail ({ state }, payload) {
      bus.$emit('msg.loading', `Sending ${payload.tab} ...`)
      let ids = state.isSelectableStatus ? state.selectedLeaf : [state.groupDetail.id]
      api.updateByQuery(ids, state.groupDetail, payload.tab)
        .then(response => {
          bus.$emit('msg.destroy')
          if (response.data.message && response.data.message.length > 0) {
            bus.$emit('msg.info', response.data.message)
          } else {
            bus.$emit('msg.success', `Group ${payload.tab} send success!`)
          }
        })
        .catch(error => {
          bus.$emit('msg.error', `Group ${payload.tab} send error: ${error.data.message}`)
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
    createData ({ dispatch }, { type, dataName, parentId }) {
      if (dataName) {
        api.createData(parentId, {
          type,
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
    },
    // Temp mock
    loadTempGroup ({ state, commit }) {
      api.getGroupDetail(state.tempGroupId)
        .then(response => {
          commit('setTemporaryMockDataList', [response.data.data])
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load error: ' + error.data.message)
        })
    },
    temporaryMock ({ dispatch }, payload ) {
      api.createData('tmp_group', payload)
        .then(_ => {
          dispatch('loadTempGroup')
          bus.$emit('msg.success', 'Temporary mock!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Temporary mock error: ' + error.data.message)
        })
    },
    notTemporaryMock ({ dispatch }, payload) {
      api.deleteByQuery([payload.id], 'tmp_group')
        .then(_ => {
          dispatch('loadTempGroup')
          bus.$emit('msg.success', 'Not temporary mock!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Not temporary mock error: ' + error.data.message)
        })
    }
  }
}
