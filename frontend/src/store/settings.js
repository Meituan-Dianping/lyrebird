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
      // api.getSettingModelList()
      //   .then(response => {
      //     commit('setSettingsList', response.data)
      //   })
      //   .catch(error => {
      //     bus.$emit('msg.error', 'Load config failed ' + error.data.message)
      //   })
      let data = [
        {
          'category': '账号相关',
          'scripts': [
            {
              'name': 'account_info',
              'title': '账号信息',
              'notice': '账号信息展示内容',
              'category': '账号相关'
            },
            {
              'name': 'signout',
              'title': '账号登出',
              'notice': '登出账号',
              'category': '账号相关'
            }
          ]
        },
        {
          'category': '代理相关',
          'scripts': [
            {
              'name': 'proxy_white_list',
              'title': '代理白名单配置',
              'notice': '设置Lyrebird代理过程中过滤不进入Lyrebird代理的域名',
              'category': '代理相关'
            }
          ]
        },
        {
          'category': 'Extension相关',
          'scripts': [
            {
              'name': 'extension_lock_update',
              'title': '冻结checker',
              'notice': '锁定本地checker,使得其不受远程仓库更新影响',
              'category': 'Extension相关'
            }
          ]
        }
      ]
      commit('setSettingsList', data)
    },
    loadSettingsForm({ state, commit, dispatch }, payload) {
      // api.getSettingsForm(payload)
      //   .then(response => {
      //     commit('setSettingsCurrentDetail', response.data)
      //   })
      //   .catch(error => {
      //     bus.$emit('msg.error', 'Load config failed ' + error.data.message)
      //   })
      let data = {
        'name': 'proxy_white_list',
        'title': '代理白名单配置',
        'subtitle': '设置Lyrebird代理过程中过滤不进入Lyrebird代理的域名',
        'language': 'cn',
        'submitText': '',
        'configs': [
          {
            'name': 'name1',
            'title': '标题1标题1标题1标题1',
            'subtitle': '这是一段描述',
            'category': 'text',
            'data': 'http://i.meituan.com'
          },
          {
            'name': 'name2',
            'title': '标题2标题2标题2标题2',
            'subtitle': '这是一段描述',
            'category': 'selector',
            'data': 'option1',
            'options': ['option1', 'option2', 'option3']
          },
          {
            'name': 'name3',
            'title': '标题3标题3标题3',
            'subtitle': '这是一段描述',
            'category': 'dict',
            'data': {
              'Key1': 'value1',
              'Key2': 'value2',
              'Key3': 'value3'
            }
          },
          {
            'name': 'name4',
            'title': '标题4标题4标题4',
            'subtitle': '这是一段描述',
            'category': 'list',
            'data': [
              'png',
              'jpeg',
              'json'
            ]
          },
        ]
      }
      commit('setSettingsCurrentDetail', data)
    },
    saveSettingsForm({ state, commit, dispatch }, { formName, formData }) {
      // api.setSettingsForm(payload)
      //   .then(response => {
      //     bus.$emit('msg.success', 'Data ' + payload.name + ' update!')
      //   })
      //   .catch(error => {
      //     bus.$emit('msg.error', 'Data ' + payload.name + ' update error: ' + error.data.message)
      //   })
      // TODO 异步的时候，检测当前panel的name是否还是load的name，如果不是就不再重新加载
      dispatch('loadSettingsForm', formName)
    },
  },
}
