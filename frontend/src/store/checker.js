import * as api from '@/api'
import { bus } from '@/eventbus'

export default {
  state: {
    checkers: [],
    focusChecker: null,
    focusCheckerDetail: null
  },
  mutations: {
    setCheckers (state, checkers) {
      state.checkers = checkers
    },
    setFocusChecker (state, focusChecker) {
      state.focusChecker = focusChecker
      for (const checker of state.checkers) {
        if (state.focusChecker === checker.name) {
          checker.select = true
        } else {
          checker.select = false
        }
      }
    },
    setFocusCheckerDetail (state, focusCheckerDetail) {
      state.focusCheckerDetail = focusCheckerDetail
    }
  },
  actions: {
    loadCheckers ({ commit }) {
      api.getCheckers()
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
      api.saveCheckerDetail(state.focusChecker, state.focusCheckerDetail)
        .then(_ => {
          bus.$emit('msg.success', 'Checker ' + state.focusChecker + ' saved!')
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
