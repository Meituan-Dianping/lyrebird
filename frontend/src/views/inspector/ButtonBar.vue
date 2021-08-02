<template>
  <div class="inspector-button-bar">
    <Tooltip v-if="isRecordMode" content="Stop recording" placement="bottom-start" :delay="500">
      <Icon
        class="inspector-button"
        type="md-square"
        color="black"
        @click="switchRecord"
        style="margin-right:3px"
        size="18"
      />
    </Tooltip>
    <Tooltip v-else content="Record" placement="bottom-start" :delay="500">
      <Icon
        class="inspector-button"
        type="md-radio-button-on"
        color="red"
        @click="switchRecord"
        style="margin-right:3px"
        size="18"
      />
    </Tooltip>

    <Tooltip content="Clear" :delay="500">
      <div class="inspector-button ivu-icon" @click="showClearModal=true">
        <svg-icon class="ivu-icon" name="short-broom" color="#666" scale="5"></svg-icon>
      </div>
    </Tooltip>

    <div class="inline" v-if="hasSelectedId">
      <div class="inline">
        <Divider type="vertical"></Divider>
      </div>

      <Tooltip content="Save" :delay="500">
        <div class="inspector-button ivu-icon" @click="saveSelectedFlow">
          <svg-icon class="ivu-icon" name="md-save" color="#666" scale="4"></svg-icon>
        </div>
      </Tooltip>

      <Tooltip content="Delete" :delay="500">
        <Icon
          class="inspector-button"
          @click="deleteSelectedFlow"
          type="md-trash"
          color="#666"
          size="18"
        />
      </Tooltip>
    </div>

    <div class="inline">
      <Divider type="vertical" />
    </div>

    <Tooltip content="Get the proxy response while the request is mocked" placement="bottom-start" max-width="200" :delay="500">
    <label>
      <b style="padding-right:5px">Diff mode:</b>
      <i-switch size="small" v-model="diffMode" @on-change="changeDiffMode" />
    </label>
    </Tooltip>

    <div class="inline">
      <Divider type="vertical"></Divider>
    </div>

    <label>
      <b style="padding-right:5px">Activated Mock Group:</b>
      <ButtonGroup>
        <Button @click="showMockDataSelector" size="small">{{activateBtnText}}</Button>
        <Button size="small" @click="resetActivatedData">
          <Tooltip content="Deactivate mock group" :delay="500">
            <Icon type="ios-backspace-outline" color="red" size="16" />
          </Tooltip>
        </Button>
      </ButtonGroup>
    </label>

    <div class="inline inspector-searchbox">
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
    </div>

    <Modal
      v-model="showClearModal"
      title="Clear Inspector"
      @on-ok="clearAllFlow"
      @on-cancel="showClearModal=false"
      width=300px
    >
      <CheckboxGroup v-model="clearTypes" size=default>
        <Tooltip max-width="200" content="This operation will clear all your Real-time flow list." placement="top-start">
          <Checkbox label="Real-time" border />
        </Tooltip>
        <Tooltip max-width="200" content="This operation will delete all your local saved data." placement="top-start">
          <Checkbox label="Advanced" border />
        </Tooltip>
      </CheckboxGroup>
    </Modal>

    <MockDataSelector ref="searchModal" :showRoot="false">
      <template #selected>
        <div v-if="activatedGroups">
          <label style="padding-right:5px">Activated Mock Group:</label>
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
    this.getRecordStatus()
    this.loadDiffModeStatus()
    this.loadFLowFilters()
  },
  computed: {
    isRecordMode () {
      return this.$store.state.inspector.recordMode === 'record'
    },
    hasSelectedId () {
      return this.$store.state.inspector.selectedIds.length > 0
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
        this.$bus.$emit('msg.error', 'Save flow error: No activated group')
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
.inline {
  display: inline;
}
.inspector-button-bar {
  flex-grow: 1;
}
.inspector-button {
  padding: 3px 8px 3px;
  font-size: 14px;
  cursor: pointer;
}
.inspector-searchbox {
  width: 30vw;
  float: right;
  margin-right: 5px;
}
</style>
