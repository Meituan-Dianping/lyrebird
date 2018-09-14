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
        activatedGroup: null,
        groupList:[],
        currentDataGroup: null,
        dataList:[],
        foucsData: null,
        dataDetail: null,
        selectedData: []
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
        },
        setFoucsData(state, dataName){
            state.foucsData = dataName
        },
        setActivitedGroup(state, groupName){
            state.activatedGroup = groupName
        },
        deleteSelectedData(state, dataName){
            index = state.selectedData.indexOf(dataName)
            if (index < 0) {
                return
            }
            state.selectedData.splice(index, 1)
        },
        addSelectedData(state, dataName){
            state.selectedData.push(dataName)
        },
        clearSelectedData(state){
            state.selectedData = []
        },
        selectAllData(state){
            state.selectedData = []
            for (const dataItem of state.dataList) {
                state.selectedData.push(dataItem.name)
            }
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
                commit('setDataList', response.data)
                commit('clearSelectedData')
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
        getActivatedGroup({commit}){
            api.getActivatedGroup()
            .then(response=>{
                commit('setActivitedGroup', response.data.name)
            })
            .catch(error=>console.log(error))
        },
        activateCurrentGroup({dispatch, state}){
            api.activateGroup(state.currentDataGroup)
            .then(response=>{
                dispatch('getActivatedGroup')
            })
            .catch(error=>console.log(error))
        },
        saveDataDetail({state, dispatch}, dataDetail){
            groupName = state.currentDataGroup
            dataName = state.foucsData
            api.updateDataDetail(groupName, dataName, dataDetail)
            .then(response=>{
                dispatch('loadDataDetail', {groupName:groupName, dataName:dataName})
            })
            .catch(error=>console.log(error))
        }
    }
}

const store = new Vuex.Store({
    modules:{
        inspector: inspector,
        dataManager: dataManager
    }
})