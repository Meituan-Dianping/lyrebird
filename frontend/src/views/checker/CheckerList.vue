<template>
  <div>
    <div class="checker-search">
      <v-text-field
        outlined
        dense
        prepend-inner-icon="mdi-magnify"
        height=26
        v-model="checkerSearchStr"
        class="checker-search-text"
        label="Search Extension Name"
        clearable
      />
    </div>

    <v-card v-if="extensionList.length" flat>
      <v-tabs
        hide-slider
        fixed-tabs
        active-class="active-tab"
        class="extension-tabs"
        :value="focusPanel"
        @change="onClickTab"
      >
        <v-tab class="rounded rounded-r-0" key="activated">Activated</v-tab>
        <v-tab class="rounded rounded-l-0" key="deactivated">Deactivated</v-tab>
      </v-tabs>
    </v-card>
    <v-divider class="border"></v-divider>
    <v-card v-if="extensionList.length" class="extension-tab-content" flat>
    <v-tabs-items :value="focusPanel">
      <v-tab-item
        v-for="extension_group in extensionList"
        :key="extension_group.key"
      >
        <v-list class="extension-list">
          <v-list-group
            :value="true"
            no-action
            sub-group
            class="group-head"
            v-for="script_group in extension_group.script_group"
            :key="script_group.category"
          >
            <template v-slot:activator>
              <v-list-item-content class="group-head-content">
                <v-list-item-title class=group-head-title>
                  <v-icon
                  class="list-grop-icon">
                    mdi-folder-outline
                  </v-icon> {{script_group.category}}
                  <v-tooltip v-if="script_group.description" right z-index="2">
                    <template v-slot:activator="{ on, attrs }">
                      <v-icon
                        small
                        class="info-icon"
                        v-bind="attrs"
                        v-on="on"
                      >
                        mdi-help-circle-outline
                      </v-icon>
                    </template>
                    <span class="extension-group-tooltip">{{script_group.description}}</span>
                  </v-tooltip>
                </v-list-item-title>
              </v-list-item-content>
            </template>
            <template v-for="(extension, index) in script_group.scripts">
              <v-list-item
                class="extension-card"
                active-class="active-extension-card"
                :key="extension.name"
                :input-value="isSelected(extension.name)"
                @click="onClickItem(extension)"
              >
                <v-list-item-content class="extension-card-content">
                  <v-list-item-title class="extension-card-title">{{extension.title}}</v-list-item-title>
                  <v-list-item-subtitle class="extension-card-subtitle">{{extension.name}}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action class="extension-card-action">
                  <v-switch
                    inset
                    dense
                    class="extension-switch"
                    v-model="extension.activated"
                    @change="changeStatus(extension)"
                  ></v-switch>
                </v-list-item-action>
              </v-list-item>
              <v-divider 
              :key="index"
              v-if="index !== script_group.scripts.length-1"
              class="extension-card-divider border">
              </v-divider>
            </template>
          </v-list-group>
        </v-list>
      </v-tab-item>
    </v-tabs-items>
    </v-card>
    <div v-else class="extension-empty">
      <p class="empty-text">No Scripts</p>
    </div>
  </div>
</template>

<script>
export default {
  activated () {
    // 0-activated, 1-deactivated
    const focusChecker = this.$store.state.checker.focusChecker
    if (focusChecker && !focusChecker.activated) {
      this.$store.commit('setFocusCheckerPanel', 1)
    } else {
      this.$store.commit('setFocusCheckerPanel', 0)
    }
  },
  data () {
    return {
      refreshCheckerListTimer: null
    }
  },
  computed: {
    extensionList() {
      return this.$store.state.checker.checkers
    },
    focusPanel() {
      return this.$store.state.checker.focusCheckerPanel
    },
    checkerSearchStr: {
      get() {
        return this.$store.state.checker.checkerSearchStr
      },
      set (val) {
        this.$store.commit('setCheckerSearchStr', val)
      }
    }
  },
  watch: {
    checkerSearchStr (newValue, oldValue) {
      if (newValue === null) {
        newValue = ''
      }
      clearTimeout(this.refreshCheckerListTimer)
      this.refreshCheckerListTimer = setTimeout(() => {
        if (newValue.trim() !== oldValue.trim()) {
          this.$store.dispatch('loadCheckers')
          clearTimeout(this.refreshCheckerListTimer)
        }
      }, 500)
    }
  },
  methods: {
    onClickItem(extension) {
      this.$store.commit('setFocusChecker', extension)
      this.$store.dispatch('loadCheckerDetail', extension.name)
    },
    onClickTab(name) {
      this.$store.commit('setFocusCheckerPanel', name)
    },
    changeStatus(extension) {
      this.$store.dispatch('updateCheckerStatus', extension)
    },
    isSelected(name) {
      return this.$store.state.checker.focusChecker && name === this.$store.state.checker.focusChecker.name
    }
  }
}
</script>

<style>
.checker-search {
  min-width: 265px;
  padding-left: 12px;
  padding-right: 12px;
  padding-bottom: 0px;
  padding-top: 12px;
}
.checker-search .v-text-field--outlined {
  border-radius: 4px 4px 4px 4px !important;
}
.checker-search .v-icon {
  font-size: 16px !important;
}
.checker-search .v-input__prepend-inner {
  margin-top: 3px !important;
}
.checker-search .v-input__append-inner {
  margin-top: 2px !important;
}
.checker-search .v-input__slot {
  min-height: 26px !important;
  height: 26px !important;
}
.checker-search-text {
  min-height: 26px !important;
  height: 26px !important;
  font-size: 14px !important;
  font-weight: 400;
  line-height: 14px !important;
}
.checker-search-text .v-label{
  font-size: 14px !important;
  top: 5px !important;
}
.extension-tab-content {
  overflow-y: auto;
  height: calc(100vh - 44px - 40px - 38px - 57px - 28px - 12px)
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
.extension-tabs {
  padding-left: 12px;
  padding-right: 12px;
  padding-bottom: 15px;
  padding-top: 16px;
}
.active-tab {
  background-color: #eeeef9;
  border: 1px solid #5F5CCA;
}
.v-tab {
  text-transform: none;
  font-weight: 600;
  font-size: 14px;
  font-family: PingFangSC-Regular;
}
.v-tab:not(.v-tab--active) {
  border:1px solid #D9DADE;
  color: #C3C4D4 !important;
}
.v-tabs-bar {
  height: 26px;
}
.extension-list {
  padding-top: 0px;
}
.info-icon {
  color: #9B9CB7 !important;
  font-size: 12px !important;
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
.extension-list .v-list-item__icon {
  margin-top: 9px !important;
  margin-bottom: 9px !important;
  margin-right: 6px !important;
  width: 14px;
  height: 14px;
}
.active-extension-card {
  background: #EEEEF9;
}
.active-extension-card .extension-card-title {
  font-weight: 600;
  color: #5E5BC9 !important;
  line-height: 12px;
}
.active-extension-card .extension-card-subtitle {
  color: #5E5BC9 !important;
}
.extension-card-content {
  width: 0px !important;
}
.extension-card-title {
  font-weight: 400;
  font-family: PingFangSC-Regular;
  font-size: 12px;
  color: #000520 !important;
  line-height: 12px !important;
  margin-bottom: 4px !important;
  width: calc(100vh - 10px) !important;
}
.extension-card-subtitle {
  font-weight: 400;
  font-family: PingFangSC-Regular;
  font-size: 12px;
  color: #9B9CB7 !important;
  line-height: 12px !important;
  max-width: calc(100vh - 10px) !important;
}
.extension-card-action {
  margin-left: 8px !important;
  margin-right: 22px !important;
  margin-top: 16px;
  margin-bottom: 16px;
}
.extension-switch {
  width: 32px;
  height: 20px;
}
.v-list-group--sub-group .v-list-group__header {
  padding-left: 0px !important;
}
.extension-card {
  padding-left: 36px !important;
  padding-right: 0px !important;
  min-height: 52px !important;
}
.extension-card-divider {
  margin-left: 36px;
}
</style>

