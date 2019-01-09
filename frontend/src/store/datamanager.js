import * as api from '../api' 

export default {
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
        },
        createGroupModal: {
            parentGroupId: null,
            parentDataList: [],
            selectedDataIdList: []
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
        setSelectedData(state, data){
            state.selectedData = data
        },
        clearSelectedData(state){
            state.selectedData = []
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
        },
        setCreateGroupModal(state, payload){
            state.createGroupModal = payload
        },
        setCreateGroupModalSelectedData(state, dataIdList){
            state.createGroupModal.selectedDataIdList = dataIdList
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
        loadDataListForNewGroupForm({commit}, groupId){
            api.getDataList(groupId)
            .then(response=>{
                commit('setCreateGroupModal', {
                    parentGroupId: groupId,
                    parentDataList: response.data.data_list
                })
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
            const groupName = state.currentDataGroup
            const dataName = state.foucsData
            api.updateDataDetail(groupName, dataName, dataDetail)
            .then(response=>{
                dispatch('loadDataDetail', {groupName:groupName, dataName:dataName})
            })
            .catch(error=>{
                console.log(error)
            })
        },
        newDataGroup({state, commit, dispatch}, {groupName, parentGroupId}){
            api.createGroup(groupName, parentGroupId)
            .then(response=>{
                const groupId = response.data.group_id
                state.groupList.push({
                    id:groupId,
                    name:groupName,
                    parent:parentGroupId
                })
                commit('setCurrentDataGroup', groupId)
                dispatch('loadDataList', groupId)
            })
            .catch(error=>{
                console.error('Create group failed');
            })
        },
        updateDataGroup({state, commit, dispatch}, {groupId, groupName, parentGroupId}){
            api.updateGroup(groupId, groupName, parentGroupId)
            .then(response=>{
                const groupId = response.data.group_id
                for (const group of state.groupList) {
                    if(groupId===group.id){
                        group.name = groupName
                        group.parent = parentGroupId
                        break
                    }
                }
                commit('setCurrentDataGroup', groupId)
                dispatch('loadDataList', groupId)
            })
        },
        deleteDataGroup({commit, dispatch}, groupId){
            api.deleteGroup(groupId)
            .then(response=>{
                commit('setCurrentDataGroup', null)
                dispatch('loadGroupList')
            })
        },
        newData({dispatch}, {groupId, name}){
            api.createData(groupId, name)
            .then(response=>{
                dispatch('loadDataList', groupId)
            })
        },
        deleteData({state, dispatch}, groupId){
            let ids = []
            for(const data of state.selectedData){
                ids.push(data.id)
            }
            api.deleteData(groupId, ids).then(response=>{
                dispatch('loadDataList', groupId)
            })
        }
    }
  }
