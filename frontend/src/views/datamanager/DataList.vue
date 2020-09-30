<template>
  <div class="data-load-spin-container">
    <Row class="button-bar">
      <span>
        <b style="padding-left:5px">Mock Data</b>
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
            <span style="cursor:pointer;">
              Label
              <Icon type="md-arrow-dropdown" size="14"/>
            </span>
          </template>
        </LabelDropdown>
      </span>
    </Row>
    <Spin fix v-if="spinShow">
      <Icon type="ios-loading" size=18 class="data-load-spin-icon-load"/>
      <div>Loading Mock Data</div>
    </Spin>
    <DocumentTree :treeData="treeData" class="data-list" />
    <MockDataSelector ref="searchModal" :showRoot=true>
      <template #searchItem="{ searchResult }">
        <Row type="flex" align="middle" class="search-row" @click.native="showNode(searchResult)">
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
import { breadthFirstSearch } from 'tree-helper'
import LabelDropdown from '@/components/LabelDropdown.vue'
import DocumentTree from '@/components/DocumentTree.vue'
import MockDataSelector from '@/components/SearchModal.vue'

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
      breadthFirstSearch(this.$store.state.dataManager.groupList, node => {
        if (node.id === payload.id) {
          this.$store.commit('setFocusNodeInfo', node)
          // `return false` is used to break loop, no related to search result
          return false
        }
      })
    },
    resetGroupDetail (payload) {
      if (payload.type === 'group') {
        this.$store.dispatch('loadGroupDetail', payload)
      } else if (payload.type === 'data') {
        this.$store.dispatch('loadDataDetail', payload)
      } else { }
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
    }
  }
}
</script>

<style scoped>
.data-list {
  height: calc(100vh - 94px);
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
  background-color: #f8f8f9;
}
.button-bar-group-right {
  float: right;
  margin-right: 10px;
}
.button-bar-btn {
  padding-left: 5px;
  cursor: pointer;
}
.button-bar-btn img {
  width: 18px;
}
.data-load-spin-container{
  position: relative;
}
.data-load-spin-icon-load{
  animation: ani-demo-spin 1s linear infinite;
}
</style>
