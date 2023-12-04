<template>
  <div class="inspector-button-bar d-flex justify-space-between flex-grow-1">
    <div class="inline">

      <v-tooltip bottom open-delay=500>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon @click="saveSelectedFlow" v-bind="attrs" v-on="on" :disabled="isEmptySelectedFlow">
            <v-icon size="18px" color="accent">mdi-content-save-outline</v-icon>
          </v-btn>
        </template>
        <span>Save</span>
      </v-tooltip>

      <v-tooltip bottom open-delay=500>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon @click="deleteSelectedFlow" v-bind="attrs" v-on="on" :disabled="isEmptySelectedFlow">
            <v-icon size="18px" color="accent">mdi-delete-outline</v-icon>
          </v-btn>
        </template>
        <span>Delete</span>
      </v-tooltip>

      <v-tooltip bottom open-delay=500>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon @click="clearAllFlow" v-bind="attrs" v-on="on">
            <v-icon size="18px" color="accent">mdi-eraser</v-icon>
          </v-btn>
        </template>
        <span>Clear</span>
      </v-tooltip>

      <b class="pr-1 pl-3">Mock Group</b>

      <v-chip
        label small outlined
        color="#D9DADE"
        text-color="content"
        v-if="Object.keys(activatedGroups).length === 0"
        @click="showMockDataSelector"
      >
        <span>None</span>
      </v-chip>

      <span v-else>
        <v-chip
          label small outlined close
          color="#D9DADE"
          close-icon="mdi-close-circle"
          close-label="Reset selected mock group"
          text-color="content"
          @click="showMockDataSelector"
          @click:close="resetActivatedData"
          v-for="(group, groupId) in activatedGroups"
          :key="groupId"
        >
          <span style="color:#000520">
            {{group.name}}
          </span>
        </v-chip>
      </span>

      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn plain icon v-bind="attrs" v-on="on" small>
            <v-icon size="18px" color="content" small style="opacity:1">mdi-help-circle-outline</v-icon>
          </v-btn>
        </template>
        <span>Select a mock group</span>
      </v-tooltip>

    </div>

    <div class="inline">
      <div class="flow-filter">
        <v-select
          dense
          hide-details
          clearable
          label="Filter"
          color="primary"
          class="flow-filter-select"
          outlined
          v-model="selectedFlowFilter"
          :items="flowFilters"
          item-text="name"
          item-value="name"
          style="border-bottom:none!important;"
          :menu-props="{ bottom: true, offsetY: true }"
          @change="changeFlowFilter"
        />
      </div>
      <div class="inspector-search">
        <v-text-field
          outlined
          dense
          height=26
          v-model="searchStr"
          class="inspector-search-text"
          label="Separate multiple keywords by spaces or |"
          clearable
          @click:clear="clearInspectorSearch"
        />
      </div>

      <v-menu
        left
        bottom
        offset-y
        offset-overflow
        :close-on-content-click="false"
        style="position: absolute;"
      >

        <template v-slot:activator="{ on, attrs }">
          <v-btn
            icon
            v-bind="attrs"
            v-on="on"
            class="ml-1"
            title="Settings"
          >
            <v-icon size="18px" color="content">mdi-cog-outline</v-icon>
          </v-btn>
        </template>

        <v-list dense>
          <v-list-item>
            <v-list-item-action>
              <v-switch v-model="diffMode"/>
            </v-list-item-action>

            <v-list-item-content>
              <v-list-item-title>Diff Mode</v-list-item-title>
              <v-list-item-subtitle>Get the proxy response while the request is mocked</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-list-item>
            <v-list-item-action>
              <v-switch v-model="isRequestKeepOriginData"/>
            </v-list-item-action>

            <v-list-item-content>
              <v-list-item-title>Origin request body</v-list-item-title>
              <v-list-item-subtitle>Keep origin request body</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-list-item>
            <v-list-item-action>
              <v-switch v-model="isSsrMockInBody"/>
            </v-list-item-action>

            <v-list-item-content>
              <v-list-item-title>Open SSR</v-list-item-title>
              <v-list-item-subtitle>Put mock data in request body instead of response data</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>

      </v-menu>
    </div>

    <TempMockDrawer ref="treeDrawer"/>

  </div>
</template>

<script>
import TempMockDrawer from '@/views/inspector/TempMockDrawer.vue'

export default {
  name: 'buttonBar',
  components: {
    TempMockDrawer
  },
  computed: {
    diffMode: {
      get () {
        return this.$store.state.inspector.diffMode === 'multiple'
      },
      set (val) {
        const mode = val ? 'multiple' : 'normal'
        this.$store.commit('setDiffMode', mode)
        this.$store.dispatch('updateConfigByKey', {
          'mock.mode': mode
        })
      }
    },
    isRequestKeepOriginData: {
      get () {
        return this.$store.state.inspector.isRequestKeepOriginData
      },
      set (val) {
        this.$store.dispatch('commitAndupdateConfigByKey', {
          'command': 'setIsRequestKeepOriginData',
          'isShowMessage': true,
          val
        })
      }
    },
    isSsrMockInBody: {
      get () {
        return this.$store.state.inspector.isSsrMockInBody
      },
      set (val) {
        this.$store.dispatch('commitAndupdateConfigByKey', {
          'command': 'setIsSsrMockInBody',
          'isShowMessage': true,
          val
        })
      }
    },
    isEmptySelectedFlow () {
      return this.$store.state.inspector.selectedFlows.length === 0
    },
    selectedFlows () {
      return this.$store.state.inspector.selectedFlows
    },
    activatedGroups () {
      return this.$store.state.inspector.activatedGroup
    },
    activateBtnText () {
      const activatedGroups = this.$store.state.inspector.activatedGroup
      if (activatedGroups === null) {
        return 'None'
      }
      if (Object.keys(activatedGroups).length === 0) {
        return 'None'
      }
      let text = ''
      for (const groupId in activatedGroups) {
        text = text + activatedGroups[groupId].name + ' '
      }
      return text
    },
    flowFilters () {
      return this.$store.state.inspector.flowFilters
    },
    selectedFlowFilter: {
      get () {
        return this.$store.state.inspector.selectedFlowFilter
      },
      set (val) {
        this.$store.commit('setSelectedFlowFilter', val)
      }
    },
    searchStr: {
      get () {
        return this.$store.state.inspector.searchStr
      },
      set (val) {
        this.$store.commit('setSearchStr', val)
      }
    }
  },
  methods: {
    showMockDataSelector () {
      this.$refs.treeDrawer.toggal()
    },
    changeFlowFilter () {
      this.$store.dispatch('loadFlowList')
    },
    clearAllFlow () {
      this.$store.dispatch('clearInspector')
    },
    resetActivatedData () {
      this.$store.dispatch('deactivateGroup')
    },
    clearInspectorSearch () {
      this.$store.commit('setSearchStr', '')
    },
    saveSelectedFlow () {
      if (Object.keys(this.activatedGroups).length <= 0) {
        this.$bus.$emit('msg.info', 'Select a mock group')
        this.showMockDataSelector()
        return
      }
      this.$store.dispatch('saveSelectedFlow')
    },
    deleteSelectedFlow () {
      this.$store.dispatch('deleteSelectedFlow')
    },
    onActivateClick (group) {
      this.$store.dispatch('activateGroup', group)
    }
  }
}
</script>

<style>
.v-input--switch {
  display: inline-block;
}
.inspector-button-bar {
  height: 26px;
}
.inspector-button-bar .v-chip__close.v-icon.v-icon--right{
  font-size: 16px !important;
}
.inline {
  display: inline-flex;
  justify-content: center;
  min-height: 26px;
  height: 26px;
  max-height: 26px;
  align-content: flex-start;
  flex-wrap: nowrap;
  align-items: center;
  margin-bottom: 7px;
}
.button-bar-divider {
  margin-left: 8px;
  margin-right: 8px;
}
.button-bar-diff-mode .v-input--switch__track {
  height: 19px !important;
  width: 32px !important;
}
.button-bar-diff-mode .v-input--selection-controls__input {
  margin-right: 0px !important;
  width: 32px !important;
}
.button-bar-diff-mode .v-input--switch__thumb {
  height: 15px !important;
  width: 15px !important;
}
.v-application--is-ltr .button-bar-diff-mode.v-input--is-label-active .v-input--switch__thumb {
  transform: translate(11px) !important;
}
.v-application--is-ltr .button-bar-diff-mode.v-input--is-label-active .v-input--selection-controls__ripple
{
  transform: translate(11px) !important;
}
.inspector-button {
  padding: 3px 8px 3px;
  font-size: 14px;
  cursor: pointer;
}
.inspector-search .v-text-field--outlined, .v-text-field--solo {
  border-radius: 0px 4px 4px 0px !important;
}
.inspector-search .v-input__append-inner {
  margin-top: 2px !important;
}
.inspector-search .v-input__slot {
  padding-right: 4px !important;
  min-height: 26px !important;
  height: 26px !important;
}
.inspector-search .v-icon {
  font-size: 14px !important;
}
.flow-filter {
  width: 120px !important;
  height: 26px;
}
.flow-filter-select {
  width: 120px;
  font-size: 14px;
  font-weight: 400;
  line-height: 14px;
}
.flow-filter-select .v-input__slot {
  min-height: 26px !important;
  height: 26px !important;
}
.flow-filter .v-text-field--outlined, .v-text-field--solo {
  border-radius: 4px 0px 0px 4px !important;
}
.flow-filter .v-select__selections{
  min-height: 26px !important;
  height: 26px !important;
  padding: 6px 0 !important;
}
.flow-filter .v-select__selection {
  line-height: 14px;
  margin: 0 4px 18px 0 !important;
}
.flow-filter .v-input__icon--append {
  width: 14px;
  height: 14px;
  min-width: 14px;
  margin-bottom: 15px;
  margin-left: 0;
}
.flow-filter .v-input__append-inner {
  margin-top: 6px !important;
}
.flow-filter .v-input__prepend-outer {
  width: 24px;
  height: 24px;
  line-height: 24px;
  min-width: 24px;
  margin-bottom: 10px;
  margin-left: 0;
  margin-right: 8px;
  margin-top: 2px !important;
}
.flow-filter .v-icon {
  width: 14px;
  height: 14px;
  line-height: 14px;
  min-width: 14px;
}
.flow-filter .v-input__icon--clear {
  width: 14px;
  height: 14px;
  line-height: 14px;
  min-width: 14px;
}
.flow-filter .v-input__icon--clear button {
  font-size: 14px;
}
.flow-filter .v-label{
  font-size: 14px !important;
  top: 5px !important;
}
.inspector-search {
  width: 320px !important;
  height: 26px;
}
.inspector-search-text {
  width: 320px;
  min-height: 26px !important;
  height: 26px !important;
  font-size: 14px !important;
  font-weight: 400;
  line-height: 14px !important;
}
.inspector-search-text .v-label{
  font-size: 14px !important;
  top: 5px !important;
}
</style>
