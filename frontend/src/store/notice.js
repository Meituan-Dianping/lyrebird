import * as api from '@/api' 

export default {
  state: {
    noticeList: [],
    notRemindList: []
  },
  mutations: {
    setNoticeList(state, noticeList){
      state.noticeList = noticeList
    },
    setNotRemindList(state, notRemindList){
      state.notRemindList = notRemindList
    }
  },
  actions: {
    deleteNotice({state}, noticeKey) {
      let l = state.noticeList.length
      for (let i=0; i<l; i++){
        if (state.noticeList[i].key === noticeKey){
          state.noticeList.splice(i,1)
          break
        }
      }
      api.deleteNotice(noticeKey)
      .catch(error => console.log(error))
    },
    deleteNotRemind({state}, noticeKey) {
      let l = state.notRemindList.length
      for (let i=0; i<l; i++){
        if (state.notRemindList[i].key === noticeKey){
          state.notRemindList.splice(i,1)
          break
        }
      }
      api.deleteNotice(noticeKey)
      .catch(error => console.log(error))
    },
    loadNoticeCenterData({state, commit}){
      api.getNoticeList()
      .then(response=>{
        commit('setNoticeList', response.data.noticeList)
        commit('setNotRemindList', response.data.notRemindList)
      })
      .catch(error => console.log(error))
    },
    updateNoticeStatus({dispatch},{key, status}){
      api.updateNoticeStatus(key, status)
    }
  }
}
