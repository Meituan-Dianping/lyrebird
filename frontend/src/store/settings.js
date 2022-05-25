import * as api from '@/api'
import { bus } from '@/eventbus'

var configCommitMap = [
  {'name': 'mock.data.showLabel', 'commit': 'setIsLabelDisplay'},
  {'name': 'mock.data.detail.stickyTopKey', 'commit': 'concatStickyTopKey'},
  {'name': 'mock.data.detail.undeletableKey', 'commit': 'concatUndeletableKey'},
  {'name': 'mock.data.detail.undisplayedKey', 'commit': 'concatUndisplayedKey'},
  {'name': 'mock.data.detail.uneditableKey', 'commit': 'concatUneditableKey'},
  {'name': 'inspector.filters', 'commit': 'setFlowFilters'},
  {'name': 'inspector.default_filter', 'commit': 'setSelectedFlowFilter'},
  {'name': 'mock.data.list.title', 'commit': 'setTitle'},
]

export default {
  state: {
    config: {}
  },
  mutations: {
    setConfig (state, config) {
      state.config = config
    }
  },
  actions: {
    loadConfig({ commit }) {
      api.getConfig()
        .then(response => {
          commit('setConfig', response.data)
          for (const config of configCommitMap) {
            if (response.data.hasOwnProperty(config.name)) {
              commit(config.commit, response.data[config.name], { root: true })
            }
          }
        })
        .catch(error => {
          bus.$emit('msg.error', 'load config failed ' + error.data.message)
        })
    }
  }
}
