import * as api from '@/api'
import { bus } from '@/eventbus'

export default {
  state: {
    checkers: [],
    focusChecker: null,
    focusCheckerDetail: null,
    focusCheckerPanel: 0,
    checkerSearchStr: ''
  },
  mutations: {
    setCheckers (state, checkers) {
      state.checkers = checkers
    },
    setFocusChecker (state, focusChecker) {
      state.focusChecker = focusChecker
    },
    setFocusCheckerPanel (state, focusCheckerPanel) {
      state.focusCheckerPanel = focusCheckerPanel
    },
    setFocusCheckerDetail (state, focusCheckerDetail) {
      state.focusCheckerDetail = focusCheckerDetail
    },
    setCheckerSearchStr (state, checkerSearchStr) {
      state.checkerSearchStr = checkerSearchStr
    }
  },
  actions: {
    loadCheckers ({ state, commit }) {
      api.getCheckers({searchStr: state.checkerSearchStr})
        .then(response => {
          commit('setCheckers', response.data.data)
        })
    },
    loadCheckerDetail ({ commit }, checkerId) {
      api.getCheckerDetail(checkerId)
        .then(response => {
          commit('setFocusCheckerDetail', response.data.data)
        })
        .catch(error => console.log(error))
    },
    saveCheckerDetail ({ state }) {
      api.saveCheckerDetail(state.focusChecker.name, state.focusCheckerDetail)
        .then(_ => {
          bus.$emit('msg.success', 'Checker ' + state.focusChecker.name + ' saved!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Save checker failed: ' + error.data.message)
        })
    },
    updateCheckerStatus ({ }, checker) {
      api.updateCheckerStatus(checker.name, checker.activated)
        .catch(error => console.log(error))
    }
  }
}
