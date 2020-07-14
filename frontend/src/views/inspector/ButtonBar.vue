<template>
  <div class="inspector-button-bar">
    <Tooltip v-if="showRecordMode" content="Stop recording" placement="bottom-start" :delay="500">
      <Icon 
        class="inspector-button" 
        type="md-square"
        color="black"
        @click="switchRecord"
        style="margin-right:3px"
        size="18"
        />
    </Tooltip>
    <Tooltip v-else content="record" placement="bottom-start" :delay="500">
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

    <div class="inline" v-if="showDataButtons">
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
      <Divider type="vertical"/>
    </div>

    <label>
      <b style="padding-right:5px">Diff mode:</b>
      <i-switch size="small" v-model="diffMode" @on-change="changeDiffMode"/>
    </label>

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
      <Input search clearable size="small" v-model="searchStr"></Input>
    </div>

    <Modal
      v-model="showClearModal"
      title="Alert"
      @on-ok="clearModalOk"
      @on-cancel="showClearModal=false"
    >
      <p>Clear flow list?</p>
    </Modal>

    <MockDataSelector ref="searchModal" :showRoot=false>
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
      diffMode: false
    }
  },
  mounted () {
    this.getRecordStatus()
    this.loadDiffModeStatus()
  },
  computed: {
    showRecordMode () {
      if (this.$store.state.inspector.recordMode === 'normal') {
        return false
      } else {
        return true
      }
    },
    showDataButtons () {
      return this.$store.state.inspector.showDataButtons
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
    searchStr: {
      get () {
        return this.$store.state.inspector.searchStr
      },
      set (val) {
        this.$store.commit('search', val)
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
          this.diffMode = response.data.diffmode
        })
        .catch(error => {
          this.$bus.$emit('msg.error', 'Load diff mode status failed: ' + error.data.message)
        })
    },
    changeDiffMode (payload) {
      setDiffModeStatus(payload)
    },
    switchRecord () {
      if (this.$store.state.inspector.recordMode === 'record') {
        this.$store.dispatch('saveRecordMode', 'normal')
      } else {
        this.$store.dispatch('saveRecordMode', 'record')
      }
    },
    getRecordStatus () {
      this.$store.dispatch('loadRecordMode')
    },
    clearModalOk () {
      this.$store.dispatch('clearFlows')
      this.selectedFlow = null
    },
    resetActivatedData () {
      this.$store.dispatch('deactivateGroup')
    },
    filterMethod (value, option) {
      return option.toUpperCase().indexOf(value.toUpperCase()) !== -1
    },
    saveSelectedFlow () {
      if (Object.keys(this.activatedGroups).length <= 0) {
        this.$bus.$emit('msg.error', 'Please activate a mock group before save.')
        return
      }
      this.$store.dispatch('saveSelectedFlow', this.activatedGroupId)
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
}
</style>

