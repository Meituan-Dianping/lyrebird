<template>
  <Row :class="rowClass" @mouseover.native="isMouseOver=true" @mouseout.native="isMouseOver=false" @click.native="onTreeNodeClick(data)">
    <Col :span="isMouseOver?21:24">
      <b v-if="data.children && data.children.length" @click="onToggleStatusChange(data)">
        <Icon v-if="data.open" type="md-arrow-dropdown" class="tree-node-inner-button"/>
        <Icon v-else type="md-arrow-dropright" class="tree-node-inner-button"/>
      </b>
      <Icon v-show="data.type === 'data'" type="md-document" class="tree-node-inner-button" />
      <span class="tree-node-inner-text">{{data.name}}</span>
    </Col>
    <Col :span="isMouseOver?2:0" align="right">
      <Tooltip content="Delete this mock data" placement="bottom-end" :delay="500">
        <Icon v-show="isMouseOver" type="md-trash" class="tree-node-inner-button" color="#ed4014" @click="onTreeNodeDelete(data)"/>
      </Tooltip>
      <Dropdown v-show="isMouseOver" placement="bottom-end">
        <a href="javascript:void(0)">
          <Icon type="ios-more" class="tree-node-inner-button"></Icon>
        </a>
        <DropdownMenu slot="list" style="min-width:60px">
          <DropdownItem align="center" @click="onTreeNodeCopy(data)">Copy</DropdownItem>
          <DropdownItem align="center" @click="onTreeNodePaste(data)" :disabled="true">Paste</DropdownItem>
        </DropdownMenu>
      </Dropdown>
    </Col>
  </Row>
</template>

<script>
export default {
  props: ['data', 'treestore'],
  data() {
    return {
      isMouseOver: false,
      contextMenuLeft: null,
      contextMenuTop: null
    }
  },
  computed: {
    rowClass(){
      if (this.data.id === this.$store.state.dataManager.focusNodeInfo.id) {
        return ["tree-node-inner-row", "tree-node-inner-row-select"]
      }
      else if (this.isMouseOver) {
        return ["tree-node-inner-row", "tree-node-inner-row-foucs"]
      }
      return ["tree-node-inner-row"]
    }
  },
  methods: {
    onToggleStatusChange(payload) {
      this.treestore.toggleOpen(payload)
      if (payload.open === true) {
        this.$store.commit('addGroupListOpenNode', payload.id)
      } else {
        this.$store.commit('deleteGroupListOpenNode', payload.id)
      }
    },
    onTreeChange(payload) {
      this.$bus.$emit('treeChange', payload)
    },
    onTreeNodeClick(payload) {
      this.$store.commit('setFocusNodeInfo', payload)
      if (payload.type === 'group') {
        this.$store.dispatch('loadGroupDetail', payload)
      } else if (payload.type === 'data') {
        this.$store.dispatch('loadDataDetail', payload)
      } else {}
    },
    onTreeNodeDelete(payload) {
      if (payload.type === 'group') {
        this.$store.dispatch('deleteGroup', payload)
      } else if (payload.type === 'data') {
        this.$store.dispatch('deleteData', payload)
      } else {}
    },
    onTreeNodeCopy(payload) {

    },
    onTreeNodePaste(payload) {

    }
  }
}
</script>

<style>
.tree-node-inner-row {
  padding: 4px 0px 4px 0px;
}
.tree-node-inner-button {
  padding-left: 5px;
  cursor: pointer;
}
.tree-node-inner-text {
  padding-left: 3px;
  font-size: 14px;
  cursor: pointer;
  word-break: break-all;
}
.tree-node-inner-row-select {
  background-color: #ebf7ff
}
.tree-node-inner-row-foucs{
  background-color: #f8f8f9
}
.ivu-dropdown > .ivu-select-dropdown {
  margin:0px 0px
}
</style>
