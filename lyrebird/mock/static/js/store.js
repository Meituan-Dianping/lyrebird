const inspector = {
    state:{
        activatedGroupId: null,        
        showDataButtons: false,
        searchStr: '',
        selectedIds: []
    },
    mutations:{
        setActivitedGroupId(state, groupId){
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
    actions:{
        loadActivatedGroup({commit}){
            api.getActivatedGroup()
            .then(response=>{
                commit('setActivitedGroupId', response.data.id)
            })
            .catch(error=>console.log(error))
        },
        activateGroup({dispatch}, groupId){
            api.activateGroup(groupId)
            .then(response=>{
                dispatch('loadActivatedGroup')
            })
            .catch(error=>console.log(error))
        },
    }
}

const dataManager = {
    state:{
        groupList:[],
        currentDataGroup: null,
        dataList:[],
        foucsData: null,
        dataDetail: null,
        selectedData: [],
        editorCache: {
            rule: '',
            req: '',
            reqBody: '',
            resp: '',
            respBody: ''
        }
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
        setFoucsData(state, dataId){
            state.foucsData = dataId
        },
        deleteSelectedData(state, dataId){
            index = state.selectedData.indexOf(dataId)
            if (index < 0) {
                return
            }
            state.selectedData.splice(index, 1)
        },
        addSelectedData(state, dataId){
            state.selectedData.push(dataId)
        },
        clearSelectedData(state){
            state.selectedData = []
        },
        selectAllData(state){
            state.selectedData = []
            for (const dataItem of state.dataList) {
                state.selectedData.push(dataItem.id)
            }
        },
        setRule(state, rule){
            state.editorCache.rule = rule
        },
        setReq(state, req){
            state.editorCache.req = req
        },
        setReqBody(state, reqBody){
            state.editorCache.reqBody = reqBody
        },
        setResp(state, resp){
            state.editorCache.resp = resp
        },
        setRespBody(state, respBody){
            state.editorCache.respBody = respBody
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
        loadDataList({commit}, groupId){
            api.getDataList(groupId)
            .then(response=>{
                commit('setDataList', response.data.data_list)
                commit('clearSelectedData')
            })
            .catch(error=>console.log(error))
        },
        loadDataDetail({commit}, payload){
            api.getDataDetail(payload.groupId, payload.dataId)
            .then(response=>{
                console.log(response.data);
                commit('setDataDetail', response.data)
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