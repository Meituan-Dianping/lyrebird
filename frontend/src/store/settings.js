import * as api from '@/api'
import { bus } from '@/eventbus'

var configCommitMap = [
  {'name': 'mock.mode', 'commit': 'setDiffMode'},
  {'name': 'mock.data.showLabel', 'commit': 'setIsLabelDisplay'},
  {'name': 'mock.data.tree.asynchronous', 'commit': 'setIsTreeLoadAsync'},
  {'name': 'mock.data.shownConfig', 'commit': 'setIsDisplayConfiguration'},
  {'name': 'mock.request.keep_origin_data', 'commit': 'setIsRequestKeepOriginData'},
  {'name': 'mock.request.ssr.mock_in_body', 'commit': 'setIsSsrMockInBody'},
  {'name': 'mock.data.tree.undeletableId', 'commit': 'concatTreeUndeletableId'},
  {'name': 'mock.data.detail.stickyTopKey', 'commit': 'concatStickyTopKey'},
  {'name': 'mock.data.detail.undeletableKey', 'commit': 'concatUndeletableKey'},
  {'name': 'mock.data.detail.undisplayedKey', 'commit': 'concatUndisplayedKey'},
  {'name': 'mock.data.detail.uneditableKey', 'commit': 'concatUneditableKey'},
  {'name': 'inspector.filters', 'commit': 'setFlowFilters'},
  {'name': 'inspector.default_filter', 'commit': 'setSelectedFlowFilter'},
  {'name': 'mock.data.list.title', 'commit': 'setTitle'},
  {'name': 'env.ip', 'commit': 'setIpList'}
]

var configPreLoad = [
  {'name': 'mock.data.tree.preload', 'commit': 'loadDataMap'},
  {'name': '', 'commit': 'loadFlowList'},
]

export default {
  state: {
    config: {},
    initialized: false,
    preLoadFuncSet: new Set(),
    focusSettingPanel: '',
    settingsList: [],
    settingsCurrentDetail: {},
  },
  mutations: {
    setConfig (state, config) {
      state.config = config
    },
    setInitialized (state, initialized) {
      state.initialized = initialized
    },
    addPreLoadFuncSet(state, preLoadFunc) {
      state.preLoadFuncSet.add(preLoadFunc)
    },
    deletePreLoadFuncSet (state, preLoadFunc) {
      state.preLoadFuncSet.delete(preLoadFunc)
    },
    setSettingsList(state, data) {
      state.settingsList = data
    },
    setSettingsCurrentDetail(state, data) {
      state.settingsCurrentDetail = data
    },
    setFocusSettingPanel(state, data) {
      state.focusSettingPanel = data
    },
  },
  actions: {
    loadConfig({ state, commit, dispatch }) {
      api.getConfig()
        .then(response => {
          commit('setConfig', response.data)
          for (const config of configCommitMap) {
            if (response.data.hasOwnProperty(config.name)) {
              commit(config.commit, response.data[config.name], { root: true })
            }
          }
          // preload
          if (!state.initialized) {
            for (const config of configPreLoad) {
              if (!config.name || (response.data.hasOwnProperty(config.name) && response.data[config.name])) {
                commit('addPreLoadFuncSet', config.commit, { root: true })
                dispatch(config.commit, { root: true })
              }
            }
            commit('setInitialized', true)
          }
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load config failed ' + error.data.message)
        })
    },
    updateConfigByKey({ dispatch }, data) {
      api.updateConfigByKey(data)
        .then(_ => {
          dispatch('loadConfig')
          bus.$emit('msg.success', `Update config success!`)
        })
        .catch(error => {
          bus.$emit('msg.error', `Update config failed ${error.data.message}`)
        })
    },
    commitAndupdateConfigByKey({ dispatch, commit }, { command, isShowMessage, val }) {
      let updateConfig = {}
      for (const config of configCommitMap) {
        if (config.commit == command) {
          updateConfig[config.name] = val
          commit(command, val)
          break
        }
      }
      api.updateConfigByKey(updateConfig)
        .then(_ => {
          dispatch('loadConfig')
          if (isShowMessage) {
            bus.$emit('msg.success', `Update config success!`)
          }
        })
        .catch(error => {
          bus.$emit('msg.error', `Update config failed ${error.data.message}`)
        })
    },
    loadSettingsList({ state, commit, dispatch }) {
      api.getSettingModelList()
        .then(response => {
          commit('setSettingsList', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load config failed ' + error.data.message)
        })
    },
    loadSettingsForm({ state, commit, dispatch }, payload) {
      api.getSettingsForm(payload)
        .then(response => {
          commit('setSettingsCurrentDetail', response.data.data)
        })
        .catch(error => {
          bus.$emit('msg.error', 'Load config failed ' + error.data.message)
        })
    },
    saveSettingsForm({ state, commit, dispatch }, { formName, formData }) {
      api.setSettingsForm(formName, formData)
        .then(response => {
          dispatch('loadSettingsForm', formName)
          bus.$emit('msg.success', 'Data ' + formName + ' update!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Data ' + formName + ' update error: ' + error.data.message)
        })
    },
    restoreSettingsForm({ state, commit, dispatch }, payload) {
      api.restoreSettingsForm(payload)
        .then(response => {
          dispatch('loadSettingsForm', payload)
          bus.$emit('msg.success', 'Data ' + payload + ' update!')
        })
        .catch(error => {
          bus.$emit('msg.error', 'Data ' + payload + ' update error: ' + error.data.message)
        })
    },
  },
}
