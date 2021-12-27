<template>
  <div class="inspector-button-bar">
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

      <!-- <Tooltip content="Clear" :delay="500">
        <div class="inspector-button ivu-icon" @click="showClearModal=true">
          <svg-icon class="ivu-icon" name="short-broom" color="#666" scale="5"></svg-icon>
        </div>
      </Tooltip> -->
      <v-divider vertical class="button-bar-divider border"/>
        <b style="padding-right:5px">Diff Mode</b>
        <v-switch v-model="diffMode" small dense inset color="primary" @change="changeDiffMode"/>
      <v-tooltip bottom open-delay=500>
        <template v-slot:activator="{ on, attrs }">
          <v-btn plain icon v-bind="attrs" v-on="on">
            <v-icon size="18px" color="content">mdi-help-circle-outline</v-icon>
          </v-btn>
        </template>
        <span>Get the proxy response while the request is mocked</span>
      </v-tooltip>


    <!-- <div class="inline">
      <Divider type="vertical" />
    </div> -->

    <!-- <Tooltip content="Get the proxy response while the request is mocked" placement="bottom-start" max-width="200" :delay="500">
    <label>
      <b style="padding-right:5px">Diff Mode</b>
      <i-switch size="small" v-model="diffMode" @on-change="changeDiffMode" />
    </label>
    </Tooltip> -->

    <v-divider vertical class="button-bar-divider border"/>

    <b style="padding-right:5px">Mock Group</b>

      <v-chip
        label small outlined close
        color="#D9DADE"
        close-icon="mdi-close-circle"
        close-label="Reset selected mock group"
        text-color="content"
        @click="showMockDataSelector"
        @click:close="resetActivatedData"
      >
        <span style="color:#000520">{{activateBtnText}}</span>
      </v-chip>

      <v-tooltip bottom open-delay=500>
        <template v-slot:activator="{ on, attrs }">
          <v-btn plain icon v-bind="attrs" v-on="on">
            <v-icon size="18px" color="content" style="opacity:1">mdi-help-circle-outline</v-icon>
          </v-btn>
        </template>
        <span>Select a mock group</span>
      </v-tooltip>

    </div>



      <!-- <v-tooltip bottom open-delay=500>
        <template v-slot:activator="{ on, attrs }">
          <v-btn plain icon @click="showClearModal=true" v-bind="attrs" v-on="on">
            <v-icon size="18px" color="accent">mdi-help-circle-outline</v-icon>
          </v-btn>
        </template>
        <span>Activate and deactivate mock group</span>
      </v-tooltip> -->

      <!-- <ButtonGroup>
        <Button @click="showMockDataSelector" size="small">{{activateBtnText}}</Button>
        <Button size="small" @click="resetActivatedData">
          <Tooltip content="Deactivate mock group" :delay="500">
            <Icon type="ios-backspace-outline" color="red" size="16" />
          </Tooltip>
        </Button>
      </ButtonGroup> -->
    <!-- </label> -->

    <div class="inspector-searchbox inspector-search">
      <v-text-field
        outlined
        dense
        height=26
        v-model="searchStr"
        class="inspector-search-text"
        label="Separate multiple keywords by spaces"
        clearable
      />
    </div>

    <span class="inspector-searchbox flow-filter">

      <v-select
        dense
        hide-details
        color="primary"
        class="flow-filter-select"
        outlined
        v-model="selectedFLowFilter"
        :items="flowFilters"
        item-text="name"
        item-value="name"
        :menu-props="{ bottom: true, offsetY: true }"
        @change="changeFLowFilter"
      />
    </span>

    <!-- <div class="inline inspector-searchbox">
      <Input
        size="small"
        search
        clearable
        v-model="searchStr"
        placeholder="Separate multiple keywords by spaces"
      >
        <Icon type="ios-funnel" slot="prepend" :color="selectedFLowFilter?'#2d8cf0':''"/>
        <Select
          v-model="selectedFLowFilter"
          size="small"
          slot="prepend"
          style="width:80px;"
          placeholder="Filters"
          not-found-text="No filters"
          @on-change="changeFLowFilter"
          clearable
          transfer
        >
          <Option v-for="(filter, index) in flowFilters" :value="filter.name" :key="filter.name">
            <Tooltip
              v-if="filter.desc"
              :delay="500"
              max-width="200"
              placement="bottom-start"
              :content="filter.desc"
              transfer
            >
              <Icon type="ios-help-circle-outline" size="14"/>
            </Tooltip>
            {{filter.name}}
          </Option>
        </Select>
      </Input>
    </div> -->

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
          <label style="padding-right:5px">Select Mock Group</label>
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
      isDisplayFLowFilterMenu: false,
      showClearModal: false,
      diffMode: false,
      clearTypes: ['Real-time']
    }
  },
  mounted () {
    this.getRecordStatus()
    this.loadDiffModeStatus()
    this.loadFLowFilters()
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
    selectedFLowFilter: {
      get () {
        return this.$store.state.inspector.selectedFLowFilter
      },
      set (val) {
        this.$store.commit('setSelectedFLowFilter', val)
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
    loadFLowFilters () {
      this.$store.dispatch('loadFlowFilters')
    },
    changeFLowFilter (payload) {
      this.$store.dispatch('saveFLowFilters', payload)
    },
    switchRecord () {
      let mode = this.$store.state.inspector.recordMode === 'record' ? 'normal' : 'record'
      this.$store.commit('setRecordMode', mode)
      this.$store.dispatch('saveRecordMode')
    },
    getRecordStatus () {
      this.$store.dispatch('loadRecordMode')
    },
    clearAllFlow () {
      this.$store.dispatch('clearInspector', this.clearTypes)
    },
    resetActivatedData () {
      this.$store.dispatch('deactivateGroup')
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

<style lang="scss">
// $color: red;
</style>

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
  margin-left: 16px;
  margin-right: 16px;
  /* color: #F1F0F4;
  border-color: #F1F0F4 !important; */
}
.inspector-button-bar {
  flex-grow: 1;
}
.inspector-button-bar .v-input--switch {
  height: 20px;
  margin-top: 0;
  padding-top: 0;
  margin-left: 6px;
  margin-right: 6px;
  width: 32px;
}
.inspector-button {
  padding: 3px 8px 3px;
  font-size: 14px;
  cursor: pointer;
}
.inspector-searchbox {
  width: 20vw;
  float: right;
  margin-right: 5px;
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
  margin: 0 4px 15px 0 !important;
}
.flow-filter .v-input__icon--append {
  width: 14px;
  height: 14px;
  min-width: 14px;
  margin-bottom: 15px;
  margin-left: 0;
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
