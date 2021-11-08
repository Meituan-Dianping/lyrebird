import * as api from '@/api'
import { bus } from '@/eventbus'

export default {
  state: {
    checkers: [],
    focusChecker: null,
    focusCheckerDetail: null,
    focusCheckerPanel:'activated'
  },
  mutations: {
    setCheckers (state, checkers) {
      state.checkers = checkers
    },
    setFocusChecker (state, focusChecker) {
      state.focusChecker = focusChecker
      if (state.checkers.length) {
        state.focusCheckerPanel = state.checkers[0].key
      }
      for (const checker_groups of state.checkers) {
          for (const script_group of checker_groups.script_group) {
              for (const checker of script_group.scripts) {
                  if (state.focusChecker === checker.name) {
                      checker.selected = true
                  } else {
                      checker.selected = false
                  }
              }
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
