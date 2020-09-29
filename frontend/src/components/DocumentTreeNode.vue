<template>
  <Row
    :class="rowClass"
    @mouseover.native="isMouseOver=true"
    @mouseout.native="isMouseOver=false"
    @click.native="onTreeNodeClick"
  >
    <span>
      <Icon
        v-show="data.type === 'group'"
        :class="toggleClass"
        size="14"
        @click="onToggleStatusChange"
      />
      <Icon v-show="data.type === 'data'" type="md-document" class="tree-node-inner-button" />
      <div class="status-point" v-show="isGroupActivated"/>

      <span class="tree-node-inner-text">
        <span v-if="data.parent_id">{{data.name}}</span>
        <Icon v-else type="ios-home" />
      </span>
      <span v-if="data.label">
        <span v-for="(label, index) in data.label">
          <span class="tree-node-inner-tag" :style="'background-color:'+(label.color?label.color:'#808695')">{{label.name}}</span>
        </span>
      </span>
    </span>

    <span class="tree-node-inner-button-bar-right" v-show="isMouseOver">
      <Icon
        v-show="data.type==='group'"
        :type="isGroupActivated ? 'md-square' : 'ios-play'"
        :color="isGroupActivated ? '#ed4014' : '#19be6b'"
        size="14"
        class="tree-node-inner-button"
        @click="isGroupActivated ? onTreeNodeDeactivate() : onTreeNodeActivate()"
      />
      <Icon
        type="md-trash"
        class="tree-node-inner-button"
        color="#ed4014"
        @click.stop="shownDeleteModal = true"
      />
      <span @click.stop>
        <Dropdown placement="bottom-end" @on-click="onDropdownMenuClick">
          <a href="javascript:void(0)">
            <Icon type="ios-more" class="tree-node-inner-button"></Icon>
          </a>
          <DropdownMenu slot="list" style="min-width:60px">
            <DropdownItem align="left" name="activate" v-show="data.type==='group'">Activate</DropdownItem>
            <DropdownItem
              align="left"
              name="deactivate"
              v-show="data.type==='group'"
              :disabled="!isGroupActivated"
            >Deactivate</DropdownItem>
            <DropdownItem align="left" name="delete">Delete</DropdownItem>
            <DropdownItem align="left" name="cut">Cut</DropdownItem>
            <DropdownItem align="left" name="copy">Copy</DropdownItem>
            <DropdownItem
              align="left"
              name="paste"
              v-show="data.type==='group'"
              :disabled="!pasteButtonEnable"
            >Paste</DropdownItem>
            <DropdownItem align="left" name="addGroup" v-show="data.type==='group'">Add group</DropdownItem>
            <DropdownItem align="left" name="addData" v-show="data.type==='group'">Add data</DropdownItem>
          </DropdownMenu>
        </Dropdown>
      </span>
    </span>
    <Modal
      v-model="shownCreateModal"
      title="Create"
      ok-text="OK"
      cancel-text="Cancel"
      @on-ok="onCreate"
      @on-cancel="createName = null"
    >
      <Row>
        <Col span="3" align="right">
          <span>Parent:</span>
        </Col>
        <Col span="18" offset="1">
          <span>{{data.name}}</span>
        </Col>
      </Row>
      <Row style="padding-top:10px">
        <Col span="3" align="right">
          <span>Name:</span>
        </Col>
        <Col span="18" offset="1">
          <Input v-model="createName" size="small" />
        </Col>
      </Row>
    </Modal>
    <Modal v-model="shownDeleteModal">
      <p slot="header" style="color:#f60;text-align:center">
        <Icon type="ios-information-circle"></Icon>
        <span>Delete confirmation</span>
      </p>
      <div style="text-align:center">
        <span style="font-size:14px">
          Are you sure you want to delete {{data.type}}
          <b>{{data.name}}</b>
        </span>
      </div>
      <div slot="footer">
        <Button type="error" size="large" long @click="onTreeNodeDelete">Delete</Button>
      </div>
    </Modal>
  </Row>
</template>

<script>
export default {
  props: ['data', 'treestore'],
  data () {
    return {
      isMouseOver: false,
      shownDeleteModal: false,
      shownCreateModal: false,
      createName: null,
      createType: null
    }
  },
  computed: {
    rowClass () {
      if (this.isGroupActivated) {
        return ['tree-node-inner-row', 'tree-node-inner-row-activated']
      } else if (this.$store.state.dataManager.focusNodeInfo && this.data.id === this.$store.state.dataManager.focusNodeInfo.id) {
        return ['tree-node-inner-row', 'tree-node-inner-row-select']
      } else if (this.isMouseOver) {
        return ['tree-node-inner-row', 'tree-node-inner-row-foucs']
      } else {
        return ['tree-node-inner-row']
      }
    },
    toggleClass () {
      let toggleClassObj = []
      if (this.data.open) {
        toggleClassObj.push('ivu-icon ivu-icon-md-arrow-dropdown')
      } else {
        toggleClassObj.push('ivu-icon ivu-icon-md-arrow-dropright')
      }
      if (this.data.children.length) {
        toggleClassObj.push('tree-node-inner-button')
      } else {
        toggleClassObj.push('tree-node-inner-button-empty')
      }
      return toggleClassObj
    },
    pasteButtonEnable () {
      const pasteTarget = this.$store.state.dataManager.pasteTarget
      if (pasteTarget === null) {
        return false
      } else {
        // Paste target should not be it self or it's children
        return !this.containsPasteTarget(pasteTarget, this.data)
      }
    },
    showActivateButton () {
      return this.isMouseOver && (this.data.type === 'group')
    },
    isGroupActivated () {
      return this.$store.state.inspector.activatedGroup.hasOwnProperty(this.data.id)
    }
  },
  methods: {
    containsPasteTarget (target, node) {
      if (node.id === target.id) {
        return true
      }
      if (node.parent) {
        return this.containsPasteTarget(target, node.parent)
      } else {
        return false
      }
    },
    onDropdownMenuClick (payload) {
      if (payload === 'activate') {
        this.onTreeNodeActivate()
      } else if (payload == 'deactivate') {
        this.onTreeNodeDeactivate()
      } else if (payload === 'delete') {
        this.shownDeleteModal = true
      } else if (payload === 'cut') {
        this.onTreeNodeCut()
      } else if (payload === 'copy') {
        this.onTreeNodeCopy()
      } else if (payload === 'paste') {
        this.onTreeNodePaste()
      } else if (payload === 'addGroup') {
        this.createType = 'group'
        this.shownCreateModal = true
      } else if (payload === 'addData') {
        this.createType = 'data'
        this.shownCreateModal = true
      } else { }
    },
    onToggleStatusChange () {
      const enableIsLoading = Boolean(this.data.children) && this.data.children.length > this.$store.state.dataManager.countEnableIsLoading
      if (enableIsLoading) {
        this.$store.commit('setIsLoading', true)
      }
      setTimeout( () => {
        this.treestore.toggleOpen(this.data)
        if (enableIsLoading) {
          this.$nextTick(function(){
            this.$store.commit('setIsLoading', false)
          })
        }
        if (this.data.open === true) {
          this.$store.commit('addGroupListOpenNode', this.data.id)
        } else {
          this.$store.commit('deleteGroupListOpenNode', this.data.id)
        }
        if (enableIsLoading) {
          this.$store.commit('setIsLoading', false)
        }
      }, 1)
    },
    onTreeNodeClick () {
      this.$store.commit('setFocusNodeInfo', this.data)
      if (this.data.type === 'group') {
        this.$store.dispatch('loadGroupDetail', this.data)
      } else if (this.data.type === 'data') {
        this.$store.dispatch('loadDataDetail', this.data)
      } else { }
    },
    onTreeNodeDelete () {
      if (this.data.type === 'group') {
        this.$store.dispatch('deleteGroup', this.data)
      } else if (this.data.type === 'data') {
        this.$store.dispatch('deleteData', this.data)
      } else { }
      this.shownDeleteModal = false
    },
    onTreeNodeCut () {
      this.$store.dispatch('cutGroupOrData', this.data)
    },
    onTreeNodeCopy () {
      this.$store.dispatch('copyGroupOrData', this.data)
    },
    onTreeNodePaste () {
      this.$store.dispatch('pasteGroupOrData', this.data)
    },
    onCreate () {
      this.$store.commit('addGroupListOpenNode', this.data.id)
      if (this.createType === 'group') {
        this.$store.dispatch('createGroup', {
          groupName: this.createName,
          parentId: this.data.id
        })
      } else if (this.createType === 'data') {
        this.$store.dispatch('createData', {
          dataName: this.createName,
          parentId: this.data.id
        })
      } else { }
    },
    onTreeNodeActivate () {
      this.$store.dispatch('activateGroup', this.data)
    },
    onTreeNodeDeactivate () {
      this.$store.dispatch('deactivateGroup')
    }
  }
}
</script>

<style>
.tree-node-inner-row {
  padding: 4px 0px 4px 0px;
}
.tree-node-inner-button-bar-right {
  float: right;
  margin-right: 15px;
}
.tree-node-inner-button {
  padding-left: 5px;
  cursor: pointer;
}
.tree-node-inner-tag {
  font-size: 12px;
  max-width: 200px;
  margin-left: 5px;
  padding: 0px 6px;
  display: inline;
  color:white;
  font-weight: 500;
  border-radius: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
  vertical-align: bottom;
}
.tree-node-inner-button-empty {
  padding-left: 5px;
  cursor: pointer;
  color: #c5c8ce;
}
.tree-node-inner-text {
  padding-left: 3px;
  font-size: 14px;
  cursor: pointer;
  word-break: break-all;
}
.tree-node-inner-row-select {
  background-color: #ebf7ff;
}
.tree-node-inner-row-foucs {
  background-color: #f8f8f9;
}
.tree-node-inner-row-activated {
  background-color: rgba(15, 204, 191, 0.15);
}
.ivu-dropdown > .ivu-select-dropdown {
  margin: 0px 0px;
}
.status-point {
  display: inline-block;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  margin: 0px 3px;
  background-color: #19be6b;
}
</style>
