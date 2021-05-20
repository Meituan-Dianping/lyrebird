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
      <span v-if="data.label && isLabelDisplay">
        <span v-for="(label, index) in data.label" class="tree-node-inner-button">
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
        @click.stop="isGroupActivated ? onTreeNodeDeactivate() : onTreeNodeActivate()"
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
          <DropdownMenu slot="list" class="dropdown-menu">
            <DropdownItem align="left" name="activate" v-show="data.type==='group'">Activate</DropdownItem>
            <DropdownItem
              align="left"
              name="deactivate"
              v-show="data.type==='group'"
              :disabled="!isGroupActivated"
              class="dropdown-menu-item-divided"
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
            <DropdownItem
              align="left"
              name="duplicate"
              :disabled="!duplicateButtonEnable"
              class="dropdown-menu-item-divided"
            >Duplicate</DropdownItem>
            <DropdownItem align="left" name="addGroup" v-show="data.type==='group'">Add group</DropdownItem>
            <DropdownItem
              align="left"
              name="addData"
              v-show="data.type==='group'"
              class="dropdown-menu-item-divided"
            >Add data</DropdownItem>
            <DropdownItem align="left" name="import" v-show="data.type==='group'" style="padding:0px">
              <Upload
                :on-success="handlerUploadSuccess"
                :on-error="handlerUploadError"
                action="/api/snapshot/import"
                :format="['lb']"
                accept=".lb"
                :data="{parent_id: data.id}"
                :show-upload-list="false"
                style="width: 100%;"
              >
                <div style="padding: 7px 16px; width:100%;">
                  Import
                </div>
              </Upload>
            </DropdownItem>
            <DropdownItem align="left" name="export" v-show="data.type==='group'" style="padding:0px">
              <a :href="'/api/snapshot/export/' + data.id"
                :download="data.name + '.lb'"
                class="dropdown-menu-item-link"
              >Export</a>
            </DropdownItem>
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
    <Modal v-model="shownDuplicateModal">
      <p slot="header" style="color:#f90;text-align:center">
        <Icon type="ios-information-circle"/>
        <span>Duplicate confirmation</span>
      </p>
      <div style="text-align:center">
        <p style="font-size:14px">
          You are duplicating {{data.type}} <b>{{data.name}}</b>
        </p>
        <p style="font-size:14px">
          <b>{{duplicateNodeChildrenCount}}</b> item will be duplicated, are you sure you want to duplicate them?
        </p>
      </div>
      <div slot="footer">
        <Button type="warning" size="large" long @click="onTreeNodeDelete">Duplicate</Button>
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
      shownDuplicateModal: false,
      shownDuplicateModleCount: 30,
      createName: null,
      createType: null,
      minLoadAnimationCount: 20
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
    duplicateButtonEnable () {
      return this.data.parent_id
    },
    showActivateButton () {
      return this.isMouseOver && (this.data.type === 'group')
    },
    isGroupActivated () {
      return this.$store.state.inspector.activatedGroup.hasOwnProperty(this.data.id)
    },
    duplicateNodeChildrenCount () {
      return this.countNodeChildren(this.data)
    },
    isLabelDisplay () {
      return this.$store.state.dataManager.isLabelDisplay
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
        if (!this.isGroupActivated) {
          return
        }
        this.onTreeNodeDeactivate()
      } else if (payload === 'delete') {
        this.shownDeleteModal = true
      } else if (payload === 'cut') {
        this.onTreeNodeCut()
      } else if (payload === 'copy') {
        this.onTreeNodeCopy()
      } else if (payload === 'paste') {
        if (!this.pasteButtonEnable) {
          return
        }
        this.onTreeNodePaste()
      } else if (payload === 'duplicate') {
        if (!this.duplicateButtonEnable) {
          return
        }
        if (this.duplicateNodeChildrenCount >= this.shownDuplicateModleCount) {
          this.shownDuplicateModal = true
          return
        }
        this.onTreeNodeDuplicate()
      } else if (payload === 'addGroup') {
        this.createType = 'group'
        this.shownCreateModal = true
      } else if (payload === 'addData') {
        this.createType = 'data'
        this.shownCreateModal = true
      } else { }
    },
    onToggleStatusChange () {
      const enableIsLoading = (Boolean(this.data.children) &&
        this.data.children.length > this.minLoadAnimationCount)
      if (enableIsLoading) {
        this.$store.commit('setIsLoading', true)
      }
      setTimeout( () => {
        this.treestore.toggleOpen(this.data)
        this.$nextTick(function(){
          this.$store.commit('setIsLoading', false)
        })
        if (this.data.open === true) {
          this.$store.commit('addGroupListOpenNode', this.data.id)
        } else {
          this.$store.commit('deleteGroupListOpenNode', this.data.id)
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
    onTreeNodeDuplicate () {
      this.$store.dispatch('duplicateGroupOrData', this.data)
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
    },
    handlerUploadSuccess (res, file) {
      this.$bus.$emit('msg.success', 'Import snapshot ' + file.name + ' success!')
      this.$store.dispatch('loadDataMap')
    },
    handlerUploadError (error, file) {
      this.$bus.$emit('msg.error', 'Import snapshot ' + file.name + ' error: ' + error)
    },
    countNodeChildren (node) {
      let count = 0
      if (!node.children || node.children.length===0) {
        return 0
      }
      for (const child of node.children) {
        count += this.countNodeChildren(child)
      }
      return count + node.children.length
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
  margin-left: 4px;
  padding: 0px 4px;
  color:white;
  border-radius: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: table-cell;
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
.dropdown-menu {
  min-width: 100px;
}
.dropdown-menu-item-divided {
  margin-bottom: 3px;
  border-bottom: 1px solid #e8eaec;
}
.dropdown-menu-item-link {
  position: relative;
  color: #515a6e;
  display: block;
  padding: 7px 16px;
}
.ivu-upload > .ivu-upload-select {
  width: 100%;
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
