import * as api from '@/api' 

export default {
  state: {
    activatedGroupId: null,
    showDataButtons: false,
    searchStr: '',
    selectedIds: []
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
    }
  },
  actions: {
    loadActivatedGroup({
      commit
    }) {
      api.getActivatedGroup()
        .then(response => {
          commit('setActivitedGroupId', response.data.id)
        })
        .catch(error => console.log(error))
    },
    activateGroup({
      dispatch
    }, groupId) {
      api.activateGroup(groupId)
        .then(response => {
          dispatch('loadActivatedGroup')
        })
        .catch(error => console.log(error))
    },
  }
}

