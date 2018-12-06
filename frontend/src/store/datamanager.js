import * as api from '@/api' 

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
