export default {
    namespaced: true,
    state: {
        src: null
    },
    mutations: {
        setSrc(state, src){
            state.src = src
        }
    }
}