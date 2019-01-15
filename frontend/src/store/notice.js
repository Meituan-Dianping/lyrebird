export default {
  state: {
    noticeList: [],
  },
  mutations: {
    addNotice(state, notice) {
      let newNotice = [notice]
      state.noticeList = newNotice.concat(state.noticeList)
    }
  },
  actions: {
    deleteNotice({state}, noticeId) {
      let l = state.noticeList.length
      for (let i=0; i<l; i++){
        if (state.noticeList[i].id === noticeId){
          state.noticeList.splice(i,1)
          break
        }
      }
    }
  }
}

