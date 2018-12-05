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
    addSelectedId: function (state, val) {
      state.selectedIds.push(val)
    },
    clearSelectedId: function (state) {
      state.selectedIds = []
    },
    updateSelectedId: function (state, val) {
      state.selectedIds = val
    },
    deleteSelectedId: function (state, val) {
      index = state.selectedIds.indexOf(val)
      if (index < 0) {
        return
      }
      state.selectedIds.splice(index, 1)
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

