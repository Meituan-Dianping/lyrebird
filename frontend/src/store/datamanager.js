import Vue from 'vue'
import * as api from '../api'
import { bus } from '@/eventbus'
import jsonpath from 'jsonpath'
import { stringify } from 'lossless-json'

export default {
  state: {
    title: 'Mock Data',
    treeSearchStr: '',
    treeData: [],
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
    undisplayedKey: ['children', 'type', 'parent_id', 'abs_parent_path', 'parent', 'link'],
    undeletableKey: ['id', 'rule', 'name', 'label', 'category', 'super_by'],
    uneditableKey: ['id', 'rule', 'super_by'],
    stickyTopKey: ['id', 'rule', 'super_id', 'name', 'label', 'super_by'],
    displayCopyKey: ['id'],
    treeUndeletableId: [],
    temporaryMockDataList: [],
    tempGroupId: 'tmp_group',
    focusedLeaf: {},
    isCurrentVersionV1: true
  },
  mutations: {
    setTitle (state, title) {
      state.title = title
    },
    setTreeSearchStr (state, treeSearchStr) {
      state.treeSearchStr = treeSearchStr
    },
    setTreeData (state, treeData) {
      state.treeData = treeData
    },
    setFocusedLeaf (state, focusedLeaf) {
      state.focusedLeaf = focusedLeaf
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
      if (!state.groupListOpenNode.includes(groupId)) {
        state.groupListOpenNode.push(groupId);
      }
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
    setIsCurrentVersionV1 (state, isCurrentVersionV1) { 
      state.isCurrentVersionV1 = isCurrentVersionV1
    }
  },
  actions: {
    saveTreeView ({ }, payload) { 
      api.saveTreeView(payload)
        .then(response => {
        })
        .catch(error => {
          bus.$emit('msg.error', 'Save treeview failed: ' + error.data.message)
        })
    },
    getTreeView ({ commit }) { 
      api.getTreeView()
        .then(response => {
          commit('setTreeData', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Get treeview failed: ' + error.data.message)
        })
    },
    saveTreeViewOpenNodes ({ }, payload) { 
      api.saveTreeViewOpenNodes(payload)
        .then(response => {
        })
        .catch(error => {
          bus.$emit('msg.error', 'Save treeview openNodes failed: ' + error.data.message)
        })
    },
    getTreeViewOpenNodes ({ commit }) { 
      api.getTreeViewOpenNodes()
        .then(response => {
          commit('setGroupListOpenNode', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Get treeview openNodes failed: ' + error.data.message)
        })
    },
    loadDataMap ({ state, commit, dispatch }, options = {}) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          commit('setIsLoading', true)
          if (!state.isCurrentVersionV1) { 
            api.getMockDataByOpenNodes({ 'reset': options.reset, 'openNodes': state.groupListOpenNode })
            .then(response => { 
              commit('setTreeData', [response.data.data])
              commit('setIsLoading', false)
              dispatch('getTreeViewOpenNodes')
            })
            .catch(error => {
                commit('setIsLoading', false)
                bus.$emit('msg.error', 'Load data failed: ' + error.data.message)
            })
            return
          }
          commit('setGroupListOpenNode', [])
          if (state.isLoadTreeAsync) {
            api.getGroupMap({labels: state.dataListSelectedLabel})
              .then(response => {
                commit('setTreeData', [response.data.data])
                commit('concatTreeUndeletableId', response.data.data.id)
                api.getGroupChildren(response.data.data.id)
                  .then(r => {
                    state.treeData[0].children = []
                    state.treeData[0].children.push(...r.data.data)
                    commit('addGroupListOpenNode', response.data.data.id)
                    commit('setIsLoading', false)
                  })
                  .catch(error => {
                    bus.$emit('msg.error', 'Load group ' + state.treeData[0].name + ' children error: ' + error)
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
                commit('setTreeData', [response.data.data])
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
      api.updateData(stringify(payload))
        .then(response => {
          state.focusedLeaf.name = payload.name
          dispatch('loadDataDetail', payload)
          bus.$emit('msg.success', 'Data ' + payload.name + ' update!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Data ' + payload.name + ' update error: ' + error.data.message)
        })
    },
    createGroup ({ state, dispatch }, { groupName, parentId }) {
      if (groupName) {
        api.createGroup(groupName, parentId)
          .then(response => {
            dispatch('getTreeView')
            if (!state.isCurrentVersionV1) { 
              dispatch('loadDataMap')
            }
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
          if (!state.isCurrentVersionV1) { 
            dispatch('loadDataMap')
          }
          state.focusedLeaf.name = payload.name
          commit('setFocusNodeInfo', response.data.message)
          dispatch('getParentAbsPath', response.data.message)
          dispatch('loadGroupDetail', payload)
          bus.$emit('msg.success', 'Group ' + payload.name + ' update!')
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
          dispatch('getParentAbsPath', response.data.data)
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
    pasteGroupOrData ({ state, commit, dispatch }, payload) {
      bus.$emit('msg.loading', `Pasting ${payload.type} ${payload.name} ...`)
      api.pasteGroupOrData(payload.id)
        .then(response => {
          commit('addGroupListOpenNode', payload.id)
          dispatch('loadDataMap')
        })
        .catch(error => {
          bus.$emit('msg.error', payload.type + ' ' + payload.name + ' paste error: ' + error.data.message)
        })
    },
    duplicateGroupOrData ({ state, commit, dispatch }, payload) {
      bus.$emit('msg.loading', 'Duplicating group ' + payload.data.name + ' ...')
      api.duplicateGroupOrData(payload.data.id)
        .then(response => {
          api.getGroupChildren(payload.data.parent_id)
            .then(_response => {
              payload.targetTreeNode.children = _response.data.data
              commit('addGroupListOpenNode', payload.data.parent_id)
            })
            .catch(error => {
              bus.$emit('msg.error', 'Load group ' + payload.data.name + ' children error: ' + error.data)
            })
          bus.$emit('msg.destroy')
          bus.$emit('msg.info', response.data.message)
        })
        .catch(error => {
          bus.$emit('msg.error', payload.data.type + ' ' + payload.data.name + ' duplicate error: ' + error.data.message)
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
    deleteByQuery ({ state, commit, dispatch }, { data, groups}) {
      const idsToDelete = [...data, ...groups]
      bus.$emit('msg.loading', 'Deleting ' + idsToDelete.length + ' items ...')
      api.deleteByQuery(data, groups)
        .then(_ => {
          dispatch('loadDataMap')
          commit('setFocusNodeInfo', {})
          commit('setDeleteNode', [])
          commit('setSelectedNode', new Set())
          if (state.pasteTarget && idsToDelete.indexOf(state.pasteTarget.id)) {
            commit('setPasteTarget', null)
          }
          bus.$emit('msg.destroy')
          bus.$emit('msg.success', 'Delete ' + idsToDelete.length + ' items success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Delete error: ' + error.data.message)
        })
    },
    // Temp mock
    loadTempMockData ({ state, commit }) {
      api.getGroupDetail(state.tempGroupId)
        .then(response => {
          commit('setTemporaryMockDataList', [response.data.data])
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load Temporary mock data error: ' + error.data.message)
        })
    },
    createTempMockData ({ state, dispatch }, payload ) {
      api.createData(state.tempGroupId, payload)
        .then(_ => {
          dispatch('loadTempMockData')
          bus.$emit('msg.success', 'Save temporary mock data success!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Save temporary mock error: ' + error.data.message)
        })
    },
    deleteTempMockData ({ state, dispatch }, payload) {
      api.deleteTempMockDataByQuery([payload.id], state.tempGroupId)
        .then(_ => {
          dispatch('loadTempMockData')
          bus.$emit('msg.success', `Delete temporary mock data ${payload.name} success!`)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Delete temporary mock data error: ' + error.data.message)
        })
    },
    getParentAbsPath ({ state }, data) {
      const paths = jsonpath.paths(state.treeData, `$..[?(@.id=='${data.id}')]`)
      let namePath = '';
      let namePathList = []
      let obj = state.treeData;
      if (paths.length == 0) { 
        return
      }
      for (let i = 1; i < paths[0].length; i++) {
        obj = obj[paths[0][i]];
        if (obj.name) {
          namePath += obj.name;
          namePathList.push(obj.name)
          if (i < paths[0].length - 1) {
            namePath += '/';
          }
        }
      }
      data.abs_parent_path = namePath
      data.abs_parent_path_list = namePathList
    },
    getIsCurrentVersionV1 ({ state, commit }) {
      api.getConfig().then(response => {
        if (response.data.hasOwnProperty('datamanager.v2.enable')) {
          commit('setIsCurrentVersionV1', !response.data['datamanager.v2.enable'])
        }
      })
      return true;
    }
  }
}
