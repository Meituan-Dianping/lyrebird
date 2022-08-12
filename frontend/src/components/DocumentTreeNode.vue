<template>
  <v-container class="pa-0 data-list-tree-node">
    
    <v-row
      no-gutters
      align="center"
      @mouseover="isMouseOver=true"
      @mouseout="isMouseOver=false"
      @click="onTreeNodeClick"
    >

      <span>
        <v-btn v-if="data.type === 'group'" icon class="mr-1 my-0" @click.stop="onToggleStatusChange">
          <v-icon small :color="toggleColor">
            {{isNodeOpen ? 'mdi-chevron-down' : 'mdi-chevron-right'}}
          </v-icon>
        </v-btn>
        <v-icon v-else-if="data.type === 'json'" small color="accent" size="14px" class="mr-1">mdi-alpha-j-box-outline</v-icon>
        <v-icon v-else small color="accent" size="14px" class="mr-1">mdi-file</v-icon>

        <div class="status-point" v-show="isGroupActivated"/>

        <span :class="nameClass">
          <span v-if="data.parent_id" color="accent" small>{{data.name}}</span>
          <v-icon v-else small color="accent">mdi-home</v-icon>
        </span>
        <span v-if="data.label && isLabelDisplay">
          <span v-for="(label, index) in data.label" :key=index class="tree-node-inner-button">
            <span class="tree-node-inner-tag" :style="'background-color:'+(label.color?label.color:'#808695')">{{label.name}}</span>
          </span>
        </span>
      </span>

      <v-spacer/>

      <span v-show="isMouseOver && !isSelectableStatus">

        <v-btn
          v-show="data.type==='group'"
          icon
          @click="isGroupActivated ? onTreeNodeDeactivate() : onTreeNodeActivate()"
          :title="isGroupActivated ? 'Deactivate' : 'Activate'"
        >
          <v-icon size="12px" :color="isGroupActivated ? 'error' : '#19be6b'">
            {{isGroupActivated ? 'mdi-square' : 'mdi-play'}}
          </v-icon>
        </v-btn>

        <v-btn
          v-show="isNodeDeletable"
          icon
          @click.stop="changeDeleteDialogStatus"
        >
          <v-icon size="12px" color="error">mdi-delete</v-icon>
        </v-btn>

        <v-menu
          v-model="showMenu"
          offset-y
          bottom
          left
          allow-overflow
          offset-overflow
          absolute
          :position-x="menuPositionX"
          :position-y="menuPositionY"
        >
          <!-- slot, got origin click event -->
          <template v-slot:activator="{ on:{click}, attrs }">
            <v-btn
              icon
              @click="changeMenuStatus"
              v-bind="attrs"
              class="mr-1"
            >
              <v-icon
                size="12px" 
                color="primary"
              >mdi-dots-horizontal</v-icon>
            </v-btn>
          </template>

          <v-list dense>

            <v-list-item key="cut" link @click="onTreeNodeCut">
              <v-list-item-title>Cut</v-list-item-title>
            </v-list-item>

            <v-list-item key="copy" link @click="onTreeNodeCopy">
              <v-list-item-title>Copy</v-list-item-title>
            </v-list-item>

            <v-list-item
              key="paste"
              link
              v-show="data.type==='group'"
              :disabled="!pasteButtonEnable"
              @click="onTreeNodePaste"
            >
              <v-list-item-title>Paste</v-list-item-title>
            </v-list-item>

            <v-list-item
              key="duplicate"
              link
              :disabled="!duplicateButtonEnable"
              @click="onTreeNodeDuplicate"
            >
              <v-list-item-title>Duplicate</v-list-item-title>
            </v-list-item>

            <v-divider v-show="data.type==='group'"/>

            <v-list-item
              key="addGroup"
              link
              v-show="data.type==='group'"
              @click="onTreeNodeAddGroup"
            >
              <v-list-item-title>Add</v-list-item-title>
            </v-list-item>

            <v-divider v-show="data.type==='group'"/>

            <v-list-item
              key="import"
              link
              v-show="data.type==='group'"
              style="padding:0px"
            >
              <v-list-item-title>
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
              </v-list-item-title>
            </v-list-item>

            <v-list-item
              key="export"
              link
              v-show="data.type==='group'"
              style="padding:0px;"
            >
              <v-list-item-title>
                <a :href="'/api/snapshot/export/' + data.id"
                  :download="data.name + '.lb'"
                  class="dropdown-menu-item-link"
                  style="color:#000520"
                >Export</a>
              </v-list-item-title>
            </v-list-item>

          </v-list>
        </v-menu>
      </span>

    </v-row>
  </v-container>
</template>

<script>

export default {
  props: ['data', 'selected'],
  data () {
    return {
      isMouseOver: false,
      shownDuplicateDialogCount: 50,
      showMenu: false,
      menuPositionX: 0,
      menuPositionY: 0,
    }
  },
  computed: {
    nameClass () {
      if (this.isGroupActivated) {
        return ['tree-node-inner-text', 'tree-node-inner-text-activate']
      }
      if (this.isNodeFocused) {
        return ['tree-node-inner-text', 'tree-node-inner-text-selected']
      }
      return ['tree-node-inner-text']
    },
    toggleColor () {
      if (this.isGroupActivated) {
        return 'success'
      }
      if (this.isNodeFocused) {
        return 'primary'
      }
      if (this.data.children && this.data.children.length) {
        return 'accent'
      }
      return 'content'
    },
    isSelectableStatus () {
      return this.$store.state.dataManager.isSelectableStatus
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
    isGroupActivated () {
      return this.$store.state.inspector.activatedGroup.hasOwnProperty(this.data.id)
    },
    isNodeFocused () {
      return this.$store.state.dataManager.focusNodeInfo && this.data.id === this.$store.state.dataManager.focusNodeInfo.id
    },
    duplicateNodeChildrenCount () {
      return this.countNodeChildren(this.data)
    },
    isNodeDeletable () {
      return this.$store.state.dataManager.treeUndeletableId.indexOf(this.data.id) === -1
    },
    isNodeOpen () {
      return this.$store.state.dataManager.groupListOpenNode.indexOf(this.data.id) > -1
    },
    isLabelDisplay () {
      return this.$store.state.dataManager.isLabelDisplay
    }
  },
  watch: {
    selected () {
      if (this.selected) {
        if (!this.data.parent_id) {
          this.$bus.$emit('msg.error', `Select root is not allowed!`)
          this.$store.commit('setSelectedLeaf', [])
          return
        }
        this.$store.commit('addSelectedNode', this.data)
      } else {
        this.$store.commit('deleteSelectedNode', this.data)
      }
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
    changeDeleteDialogStatus () {
      this.$store.commit('setDeleteNode', [this.data])
      this.$store.commit('setDeleteDialogSource', 'single')
      this.$store.commit('setIsShownDeleteDialog', true)
    },
    changeMenuStatus (e) {
      e.preventDefault()
      this.showMenu = false
      this.menuPositionX = e.clientX
      this.menuPositionY = e.clientY
      this.showMenu = true
    },
    onToggleStatusChange () {
      if (this.isNodeOpen) {
        this.$store.commit('deleteGroupListOpenNode', this.data.id)
      } else {
        this.$store.commit('addGroupListOpenNode', this.data.id)
      }
    },
    onTreeNodeClick () {
      this.$store.commit('setFocusNodeInfo', this.data)
      if (this.data.type === 'group') {
        this.$store.dispatch('loadGroupDetail', this.data)
      } else if (this.data.type === 'data') {
        this.$store.dispatch('loadDataDetail', this.data)
      } else if (this.data.type === 'json') {
        this.$store.dispatch('loadDataDetail', this.data)
      } else { }
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
      if (this.duplicateNodeChildrenCount >= this.shownDuplicateDialogCount) {
        this.$store.commit('setIsShownDuplicateDialog', true)
        return
      }
      this.$store.dispatch('duplicateGroupOrData', this.data)
    },
    onTreeNodeAddGroup () {
      this.$store.commit('setIsShownCreateDialog', true)
    },
    onTreeNodeActivate () {
      this.$store.dispatch('activateGroup', this.data)
    },
    onTreeNodeDeactivate () {
      this.$store.dispatch('deactivateGroup')
    },
    handlerUploadSuccess (res, file) {
      if (res.code === 1000) {
        this.$bus.$emit('msg.success', 'Import snapshot ' + file.name + ' success!')
        this.$store.dispatch('loadDataMap')
      } else {
        this.$bus.$emit('msg.error', 'Import snapshot ' + file.name + ' error: ' + res.message)
      }
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
.data-list-tree-node .v-btn--icon.v-size--default {
  height: 20px;
  width: 20px;
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
.tree-node-inner-text {
  font-size: 14px;
  cursor: pointer;
  word-break: break-all;
}
.tree-node-inner-text-selected {
  font-size: 16px;
  font-weight: 800;
  color: #5F5CCA;
}
.tree-node-inner-text-activate {
  font-size: 16px;
  font-weight: 900;
  color: #4CAF50;
}
.dropdown-menu-item-link {
  position: relative;
  color: #515a6e;
  display: block;
  padding: 7px 16px;
}
.tree-node-inner-row-select {
  background-color: #ebf7ff;
}
.tree-node-inner-row-activated {
  background-color: rgba(15, 204, 191, 0.15);
}
.ivu-upload > .ivu-upload-select {
  width: 100%;
}
.status-point {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin: 0px 5px 0px 1px;
  background-color: #19be6b;
  border: 1px solid #2d8cf0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  background-clip: text;
  animation-timing-function: ease-in-out;
  animation-name: status-point-breathe;
  animation-duration: 800ms;
  animation-iteration-count: infinite;
  animation-direction: alternate;
}
@keyframes status-point-breathe {
  0% {
    opacity: .9;
    box-shadow: 0 0px 2px rgba(0, 147, 223, 0.4), 0 1px 1px rgba(0, 147, 223, 0.1) inset;
  }
  100% {
    opacity: 1;
    box-shadow: 0 0px 10px #19be6b, 0 1px 10px #19be6b inset;
  }
}
</style>

<style lang='scss' scoped>
  .v-application ol, .v-application ul {
    padding-left: 0px;
  }
</style>
