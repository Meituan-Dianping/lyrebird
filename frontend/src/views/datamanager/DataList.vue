<template>
  <div>
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
    </Row>
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
import DocumentTree from '@/components/DocumentTree.vue'
import MockDataSelector from '@/components/SearchModal.vue'

export default {
  components: {
    DocumentTree,
    MockDataSelector
  },
  computed: {
    treeData () {
      return this.$store.state.dataManager.groupList
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
      this.$nextTick(() => {
        document.getElementById(this.$store.state.dataManager.focusNodeInfo._id).scrollIntoView()
      })
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
</style>
