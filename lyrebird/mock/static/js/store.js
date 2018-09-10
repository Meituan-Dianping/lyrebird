const inspector = {
    state:{
        showDataButtons: false,
        searchStr: '',
        selectedIds: []
    },
    mutations:{
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
    }
}

const dataManager = {
    state:{
        groupList:[],
        currentDataGroup: null,
        dataList:[],
        foucsMockData: null,
        dataDetail: null
    },
    mutations:{
        setGroupList(state, groupList){
            state.groupList = groupList
        },
        setCurrentDataGroup(state, dataGroup){
            state.currentDataGroup = dataGroup
        },
        setDataList(state, dataList){
            state.dataList = dataList
        },
        setDataDetail(state, dataDetail){
            state.dataDetail = dataDetail
        }
    },
    actions:{
        loadGroupList({commit}){
            api.getGroups()
            .then(response=>{
                commit('setGroupList', response.data)
            })
            .catch(error=>console.log(error))
        },
        loadDataList({commit}, groupName){
            api.getDataList(groupName)
            .then(response=>{
                commit('setDataList', response.data.data)
            })
            .catch(error=>console.log(error))
        },
        loadDataDetail({commit}, payload){
            api.getDataDetail(payload.groupName, payload.dataName)
            .then(response=>{
                commit('setDataDetail', response.data)
            })
            .catch(error=>console.log(error))
        },
        selectGroupChange({commit}, groupName){
            
        }
    }
}

const store = new Vuex.Store({
    modules:{
        inspector: inspector,
        dataManager: dataManager
    }
})