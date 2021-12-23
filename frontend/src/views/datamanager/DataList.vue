<template>
  <div>
    <Row class="button-bar">
      <span>
        <b style="padding-left:5px">Mock Data</b>
      </span>
      <span>
        <a href="#" title="Reload mock data">
          <Icon type="md-refresh" style="margin-left: 5px;" size=12 @click.stop="reloadMockData"/>
        </a>
      </span>
      <span class="button-bar-group-right">
        <Tooltip content="Search" placement="bottom-end" :delay="500">
          <Icon
            type="md-search"
            class="button-bar-btn"
            @click="changeSearchModalOpenState"
          />
        </Tooltip>
        <span @click.stop v-show="false">
          <Dropdown>
            <a href="javascript:void(0)">
              <Icon type="ios-more-outline" class="button-bar-btn"/>
            </a>
            <DropdownMenu slot="list">
              <DropdownItem>Import...</DropdownItem>
              <DropdownItem>Export...</DropdownItem>
              <DropdownItem>Reload</DropdownItem>
            </DropdownMenu>
          </Dropdown>
        </span>
      </span>
      <span class="button-bar-group-right">
        <LabelDropdown :initLabels="selectedLabel" :placement="'bottom-end'" @onLabelChange="editLabel">
          <template #dropdownButton>
            <span class="button-bar-btn">
              Labels
              <Icon type="md-arrow-dropdown" size="14"/>
            </span>
          </template>
        </LabelDropdown>
      </span>
      <span class="button-bar-group-right">
        <a v-if="isLabelDisplay" href="#" title="Hide labels">
          <Icon @click.stop="changeLabelDisplayState" type="ios-eye-off" class="button-bar-btn"/>
        </a>
        <a v-else href="#" title="Display labels">
          <Icon @click.stop="changeLabelDisplayState" type="ios-eye" class="button-bar-btn"/>
        </a>
      </span>
    </Row>
    <Row>
      <v-overlay
        :absolute="true"
        opacity="0.8"
        color="#ffffff"
        :value="spinShow"
      >
        <v-progress-circular
          size="30"
          color="primary"
          width="2"
          indeterminate
        />
      </v-overlay>
      <DocumentTree :treeData="treeData" class="data-list" />
    </Row>
    <MockDataSelector ref="searchModal" :showRoot=true>
      <template #searchItem="{ searchResult }">
        <Row type="flex" align="middle" class="search-row" @click.native="showNodeAndCloseSearchModal(searchResult)">
          <Col span="24">
            <p class="search-item">
              <b v-if="searchResult.parent_id" class="search-item-title">{{searchResult.name}}</b>
              <Icon v-else type="ios-home" class="search-item-title"/>
              <span class="search-item-path">{{searchResult.abs_parent_path}}</span>
            </p>
          </Col>
        </Row>
      </template>
    </MockDataSelector>
  </div>
</template>

<script>
import LabelDropdown from '@/components/LabelDropdown.vue'
import DocumentTree from '@/components/DocumentTree.vue'
import MockDataSelector from '@/components/SearchModal.vue'
import { searchGroupByName } from '@/api'

export default {
  components: {
    LabelDropdown,
    DocumentTree,
    MockDataSelector
  },
  computed: {
    treeData () {
      return this.$store.state.dataManager.groupList
    },
    spinShow () {
      return this.$store.state.dataManager.isLoading
    },
    selectedLabel () {
      return this.$store.state.dataManager.dataListSelectedLabel
    },
    isLabelDisplay () {
      return this.$store.state.dataManager.isLabelDisplay
    }
  },
  watch: {
    treeData (val) {
      // Why does treeDate have Watchers, while treeData is computed property?
      // When Vue is still on mounting, value of "computed properties" is an observer, not an actual data
      if (val.length && this.$store.state.snapshot.importGroupId) {
        this.setDisplayDataDeteil()
      }
    }
  },
  methods: {
    changeSearchModalOpenState () {
      this.$refs.searchModal.toggal()
    },
    showNode (payload) {
      this.resetGroupListOpenNode(payload)
      this.resetFocusNodeInfo(payload)
      this.resetGroupDetail(payload)
    },
    showNodeAndCloseSearchModal (payload) {
      this.resetGroupListOpenNode(payload)
      this.resetFocusNodeInfo(payload)
      this.resetGroupDetail(payload)
      this.changeSearchModalOpenState()
    },
    resetGroupListOpenNode (payload) {
      for (const openId of this.$store.state.dataManager.groupListOpenNode) {
        this.$store.commit('deleteGroupListOpenNode', openId)
      }
      for (const parent of payload.abs_parent_obj) {
        this.$store.commit('addGroupListOpenNode', parent.id)
      }
    },
    resetFocusNodeInfo (payload) {
      this.$store.commit('setFocusNodeInfoByGroupInfo', payload)
    },
    resetGroupDetail (payload) {
      if (payload.type === 'group') {
        this.$store.dispatch('loadGroupDetail', payload)
      } else if (payload.type === 'data') {
        this.$store.dispatch('loadDataDetail', payload)
      } else { }
    },
    setDisplayDataDeteil () {
      const importGroupId = this.$store.state.snapshot.importGroupId
      searchGroupByName(importGroupId)
        .then(response => {
          const searchResults = response.data.data
          if (searchResults.length < 1) {
            this.$bus.$emit('msg.error', 'Load snapshot ' + importGroupId + ' error: Group id not found!')
            return
          }
          // Not handle situation of more than one groups have the same uuid
          // Only the first or searchResults is used
          const importGroup = searchResults[0]
          this.showNode(importGroup)
          this.$store.commit('clearImportGroupId')
          this.$bus.$emit('msg.success', 'Load snapshot ' + importGroup.name + ' success! ')
        }).catch(error => {
          this.$bus.$emit('msg.error', 'Load snapshot ' + importGroupId + ' error: ' + error.data.message)
        })
    },
    editLabel (payload) {
      this.$store.commit('setDataListSelectedLabel', {})
      let labels = []
      for (const id of payload.labels) {
        const label = this.$store.state.dataManager.labels[id]
        labels.push(label)
      }
      this.$store.commit('setDataListSelectedLabel', labels)
      this.$store.dispatch('loadDataMap')
    },
    changeLabelDisplayState () {
      const status = !this.isLabelDisplay
      this.$store.commit('setIsLabelDisplay', status)
    },
    reloadMockData () {
      this.$store.dispatch('loadDataMap')
    }
  }
}
</script>

<style scoped>
.data-list {
  height: calc(100vh - 44px - 28px - 40px - 28px - 12px);
  /* total:100vh
    header: 38px
    buttonBar: 28px
    tree
    footer: 28px
  */
  overflow-y: auto;
  margin-right: 0;
}
.button-bar {
  height: 27px;
  line-height: 27px;
  border-bottom: 1px solid #ddd;
  background-color: #ffffff;
}
.button-bar-group-right {
  float: right;
  margin-right: 10px;
}
.button-bar-btn {
  cursor: pointer;
}
.button-bar-btn img {
  width: 18px;
}
</style>
