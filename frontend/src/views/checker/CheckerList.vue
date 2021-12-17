<template>
  <div>
    <v-toolbar-title class="extension-title">Extension</v-toolbar-title>
    <v-tabs
      v-if="checkerList.length"
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
    <v-divider class="extension-divider" v-if="checkerList.length"></v-divider>
    <v-card v-if="checkerList.length" class="extension-tab-content" flat>
    <v-tabs-items :value="focusPanel">
      <v-tab-item
        v-for="checker_group in checkerList"
        :key="checker_group.key"
      >
        <v-list class="extension-list">
          <v-list-group
            :value="true"
            no-action
            sub-group
            class="group-head"
            v-for="script_group in checker_group.script_group"
            :key="script_group.category"
          >
            <template v-slot:activator>
              <v-list-item-content class="group-head-content">
                <v-list-item-title class=group-head-title>
                  <v-icon
                  class="list-grop-icon">
                    mdi-folder-outline
                  </v-icon> {{script_group.category}}
                  <v-tooltip v-if="script_group.description" right z-index="10">
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
            <template v-for="(checker, index) in script_group.scripts">
              <v-list-item
                class="extension-card"
                active-class="active-extension-card"
                :key="checker.name"
                :input-value="isSelected(checker.name)"
                @click="onClickItem(checker.name)"
              >
                <v-list-item-content class="extension-card-content">
                  <v-list-item-title class="extension-card-title">{{checker.title}}</v-list-item-title>
                  <v-list-item-subtitle class="extension-card-subtitle">{{checker.name}}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action class="extension-card-action">
                  <v-switch
                    inset
                    dense
                    class="extension-switch"
                    v-model="checker.activated"
                    @change="changeStatus(checker)"
                  ></v-switch>
                </v-list-item-action>
              </v-list-item>
              <v-divider 
              :key="index"
              v-if="index !== script_group.scripts.length-1"
              class="extention-card-divider">
              </v-divider>
            </template>
          </v-list-group>
        </v-list>
      </v-tab-item>
    </v-tabs-items>
    </v-card>
    <div v-else class="checker-empty">
      No scripts
    </div>
  </div>
</template>

<script>
export default {
  computed: {
    checkerList() {
      return this.$store.state.checker.checkers
    },
    focusPanel() {
      return this.$store.state.checker.focusCheckerPanel
    }
  },
  methods: {
    onClickItem(name) {
      this.$store.commit('setFocusChecker', name)
      this.$store.dispatch('loadCheckerDetail', name)
    },
    onClickTab(name) {
      this.$store.commit('setFocusCheckerPanel', name)
    },
    changeStatus(checker) {
      this.$store.dispatch('updateCheckerStatus', checker)
    },
    isSelected(name) {
      return name === this.$store.state.checker.focusChecker
    }
  }
}
</script>

<style>
.extension-title {
  padding-left: 12px;
  padding-bottom: 19px;
  padding-top: 16px;
  font-weight: 600;
  font-family: PingFangSC-Semibold;
  font-size: 16px;
  color: #000520;
  line-height: 16px;
}
.extension-tab-content {
  overflow-y: scroll;
  height: calc(100vh - 155px)
}
.extension-tabs {
  padding-left: 12px;
  padding-right: 12px;
  padding-bottom: 15px;
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
.v-list-item__icon {
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
  width: calc(100vh - 850px) !important;
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
.extention-card-divider {
  margin-left: 36px;
  background: #F1F0F4;
}
.extension-divider {
  background: #F1F0F4;
}
</style>

