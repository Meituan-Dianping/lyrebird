Vue.config.devtools = true;

iview.lang('en-US');

const store = new Vuex.Store({
  state: {
    showDataButtons : false,
    searchStr: '',
    selectedIds: []
  },
  mutations: {
    showDataButtons: function(state, val){
      state.showDataButtons = val
    },
    search: function(state, val){
      state.searchStr = val
    },
    addSelectedId: function(state, val){
      state.selectedIds.push(val)
    },
    clearSelectedId: function(state){
      state.selectedIds = []
    },
    updateSelectedId: function(state, val){
      state.selectedIds = val
    },
    deleteSelectedId: function(state, val){
      index = state.selectedIds.indexOf(val)
      if(index<0){
        return
      }
      state.selectedIds.splice(index, 1)
    }
  },
  getters: {
  }
})


const app = new Vue({
    el: '#app',
    store,
    data: {
    },
    components: {
      'inspector': httpVueLoader('static/vue/inspector.vue')
    }
})
