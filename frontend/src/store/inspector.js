import * as api from '@/api' 

export default {
  state: {
    activatedGroupId: null,
    showDataButtons: false,
    searchStr: '',
    selectedIds: [],
    groupList: [],
    focusedFlow: null
  },
  mutations: {
    setActivitedGroupId(state, groupId) {
      state.activatedGroupId = groupId
    },
    showDataButtons: function (state, val) {
      state.showDataButtons = val
    },
    search: function (state, val) {
      state.searchStr = val
    },
    setSelectedId: function(state, val) {
      state.selectedIds = val
    },
    clearSelectedId: function (state) {
      state.selectedIds = []
    },
    setFocusedFlow(state, flow){
      state.focusedFlow = flow
    }
  },
  actions: {
    loadActivatedGroup({commit}) {
      api.getActivatedGroup()
        .then(response => {
          commit('setActivitedGroupId', response.data.id)
        })
        .catch(error => console.log(error))
    },
    activateGroup({dispatch}, groupId) {
      api.activateGroup(groupId)
        .then(response => {
          dispatch('loadActivatedGroup')
        })
        .catch(error => console.log(error))
    },
    deactivateGroup({dispatch}){
      api.deactivateGroup()
      .then(response=>{
        dispatch('loadActivatedGroup')
      })
      .catch(error=>{
      })
    },
    iLoadGroupList({state}){
      api.getGroups()
      .then(response=>{
        state.groupList = response.data
      })
      .catch(error=>console.log(error))
    },
    createAndActivateGroup({state, commit, dispatch}, groupName){
      api.createGroup(groupName)
      .then(response=>{
        const groupId = response.data.group_id
        state.groupList.push({
          id: groupId,
          name: groupName,
          parent: null           
        })
        dispatch('activateGroup', groupId)
      })
    }
  }
}

