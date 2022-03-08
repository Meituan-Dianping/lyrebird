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
          <v-btn icon @click="showClearModal=true" v-bind="attrs" v-on="on">
            <v-icon size="18px" color="accent">mdi-eraser</v-icon>
          </v-btn>
        </template>
        <span>Clear</span>
      </v-tooltip>

      <v-divider vertical class="button-bar-divider border"/>
      <b style="padding-right:5px">Diff Mode</b>
      <v-switch
        small
        dense
        inset
        v-model="diffMode"
        color="primary"
        class="button-bar-diff-mode"
        @change="changeDiffMode"
      />

      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn plain icon small v-bind="attrs" v-on="on">
            <v-icon small size="18px" color="content">mdi-help-circle-outline</v-icon>
          </v-btn>
        </template>
        <span>Get the proxy response while the request is mocked</span>
      </v-tooltip>

      <v-divider vertical class="button-bar-divider border"/>

      <b style="padding-right:5px">Mock Group</b>

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
          label="Separate multiple keywords by spaces"
          clearable
          @click:clear="clearInspectorSearch"
        />
      </div>
    </div>

    <Modal
      v-model="showClearModal"
      title="Clear Inspector Flow"
      @on-ok="clearAllFlow"
      @on-cancel="showClearModal=false"
      width=300px
    >
      <p>Clear flow list?</p>
    </Modal>

    <MockDataSelector ref="searchModal" :showRoot="false">
      <template #selected>
        <div v-if="activatedGroups">
          <label style="padding-right:5px">Activated Mock Group</label>
          <Tag v-for="group in activatedGroups" :key="group.id">{{group.name}}</Tag>
        </div>
      </template>
      <template #searchItem="{ searchResult }">
        <Row type="flex" align="middle" class="search-row" @click.native="onActivateClick(searchResult)">
          <Col span="22">
            <p class="search-item">
              <b class="search-item-title">{{searchResult.name}}</b>
              <span class="search-item-path">{{searchResult.abs_parent_path}}</span>
            </p>
          </Col>
          <Col span="2" align="right">
            <Icon
              type="ios-play"
              color="#19be6b"
              size="22"
              class="search-item-btn"
            />
          </Col>
        </Row>
      </template>
    </MockDataSelector>
  </div>
</template>

<script>
import MockDataSelector from '@/components/SearchModal.vue'
import Icon from 'vue-svg-icon/Icon.vue'
import { getDiffModeStatus, setDiffModeStatus } from '@/api'

export default {
  name: 'buttonBar',
  components: {
    MockDataSelector,
    'svg-icon': Icon
  },
  data () {
    return {
      showClearModal: false,
      diffMode: false,
      clearTypes: ['Real-time']
    }
  },
  mounted () {
    this.loadDiffModeStatus()
  },
  computed: {
    isRecordMode () {
      return this.$store.state.inspector.recordMode === 'record'
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
        return this.$store.state.inspector.selectedFlowFilter.name
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
      this.$refs.searchModal.toggal()
    },
    loadDiffModeStatus () {
      getDiffModeStatus()
        .then(response => {
          this.diffMode = response.data.diffmode === 'multiple'
        })
        .catch(error => {
          this.$bus.$emit('msg.error', 'Load diff mode status failed: ' + error.data.message)
        })
    },
    changeDiffMode (payload) {
      const mode = payload ? 'multiple' : 'normal'
      setDiffModeStatus(mode)
    },
    changeFlowFilter () {
      this.$store.dispatch('loadFlowList')
    },
    clearAllFlow () {
      this.$store.dispatch('clearInspector', this.clearTypes)
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
}
.inspector-search .v-icon {
  font-size: 14px !important;
}
.flow-filter {
  width: 100px !important;
  height: 26px;
}
.flow-filter-select {
  width: 100px;
  min-height: 26px !important;
  height: 26px !important;
  font-size: 14px;
  font-weight: 400;
  line-height: 14px;
}
.flow-filter .v-text-field--outlined, .v-text-field--solo {
  border-radius: 4px 0px 0px 4px !important;
}
.v-input__slot {
  min-height: 26px !important;
  height: 26px !important;
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
