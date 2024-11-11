<template>
    <div>
      <v-card v-if="settingList.length" class="setting-tab-content" flat>
          <v-list class="setting-list">
            <v-list-group
              :value="true"
              no-action
              sub-group
              class="group-head"
              v-for="setting_group in settingList"
              :key="setting_group.category"
            >
              <template v-slot:activator>
                <v-list-item-content class="group-head-content">
                  <v-list-item-title class=group-head-title>
                    {{setting_group.category}}
                  </v-list-item-title>
                </v-list-item-content>
              </template>
              <template v-for="(setting, index) in setting_group.scripts">
                <v-list-item
                  class="setting-card"
                  active-class="active-setting-card"
                  :key="setting.name"
                  :input-value="isSelected(setting.name)"
                  @click="onClickItem(setting)"
                >
                  <v-list-item-content class="setting-card-content">
                    <v-list-item-title class="setting-card-title">{{setting.title}}</v-list-item-title>
                    <v-list-item-subtitle class="setting-card-subtitle">{{setting.notice}}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-divider 
                :key="index"
                v-if="index !== setting_group.scripts.length-1"
                class="setting-card-divider border">
                </v-divider>
              </template>
            </v-list-group>
          </v-list>
      </v-card>
      <div v-else class="setting-empty">
        <p class="empty-text">No Scripts</p>
      </div>
    </div>
  </template>
  
  <script>

  export default {
    data () {
      return {
        currentPanel: '',
      }
    },
    computed: {
      settingList() {
        return this.$store.state.settings.settingsList
      },
      focusPanel() {
        return this.$store.state.settings.focusCheckerPanel
      }
    },
    watch: {},
    methods: {
      onClickItem(extension) {
        if (this.currentPanel !== extension.name){
          this.$store.commit('setFocusSettingPanel', extension.name)
          this.$store.dispatch('loadSettingsForm', extension.name)
          this.currentPanel = extension.name
        }
      },
      isSelected(name) {
        return this.focusPanel === name
      }
    },
    mounted() {
      this.$store.dispatch('loadSettingsList')
    },
  }
  </script>
  
  <style>
  .setting-tab-content {
    margin-top: 10px;
    overflow-y: auto;
    height: calc(100vh - 44px - 40px - 10px - 28px - 12px)
    /* total:100vh
    header: 44px
    title: 40px
    search: 38px
    tabs: 57px
    editor
    margin-bottom: 12px
    footer: 28px
    */
  }
  .setting-list {
    padding-top: 0px;
  }
  .v-list .group-head .v-list-group__header {
    padding-left: 12px !important;
    min-height: 32px !important;
  }
  .group-head .group-head-content {
    padding: 0px !important;
  }
  .group-head .group-head-title {
    font-weight: 600;
    font-size: 14px;
    font-family: PingFangSC-Semibold;
    line-height: 14px;
  }
  .setting-list .v-list-item__icon {
    margin-top: 9px !important;
    margin-bottom: 9px !important;
    margin-right: 6px !important;
    width: 16px;
    height: 14px;
  }
  .active-setting-card {
    background: #EEEEF9;
  }
  .active-setting-card .setting-card-title {
    font-weight: 600;
    color: #5E5BC9 !important;
    line-height: 14px;
  }
  .active-setting-card .setting-card-subtitle {
    color: #5E5BC9 !important;
  }
  .setting-card-content {
    width: 0px !important;
  }
  .setting-card-title {
    font-weight: 400;
    font-family: PingFangSC-Regular;
    font-size: 12px;
    color: #000520 !important;
    line-height: 12px !important;
    margin-bottom: 4px !important;
    width: calc(100vh - 10px) !important;
  }
  .setting-card-subtitle {
    font-weight: 400;
    font-family: PingFangSC-Regular;
    font-size: 12px;
    color: #9B9CB7 !important;
    line-height: 12px !important;
    max-width: calc(100vh - 10px) !important;
  }
  .v-list-group--sub-group .v-list-group__header {
    padding-left: 0px !important;
  }
  .setting-card {
    padding-left: 36px !important;
    padding-right: 0px !important;
    min-height: 52px !important;
  }
  .setting-card-divider {
    margin-left: 36px;
  }
  </style>
  
  