<template>
  <v-menu
    v-model="isShownNodeMenu"
    offset-y
    bottom
    left
    allow-overflow
    offset-overflow
    absolute
    :position-x="menuPositionX"
    :position-y="menuPositionY"
  >
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
</template>

<script>

export default {
  computed: {
    data () {
      return this.$store.state.dataManager.focusNodeInfo
    },
    isShownNodeMenu: {
      get () {
        return this.$store.state.dataManager.isShownNodeMenu
      },
      set (val) {
        this.$store.commit('setIsShownNodeMenu', val)
      }
    },
    menuPositionX () {
      if (this.$store.state.dataManager.shownNodeMenuPosition) {
        return this.$store.state.dataManager.shownNodeMenuPosition.x
      }
    },
    menuPositionY () {
      if (this.$store.state.dataManager.shownNodeMenuPosition) {
        return this.$store.state.dataManager.shownNodeMenuPosition.y
      }
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
    shownNodeMenuPosition () {
      return this.$store.state.dataManager.shownNodeMenuPosition
    }
  },
  watch: {
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
    onTreeNodeCut () {
      this.$store.dispatch('cutGroupOrData', this.data)
      let targetNode = this.findNode(this.$store.state.dataManager.treeData, this.data.parent_id)
      targetNode.children = targetNode.children.filter(item => item.id != this.data.id)
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
      let targetNode = this.findNode(this.$store.state.dataManager.treeData, this.data.parent_id)
      this.$store.dispatch('duplicateGroupOrData', {
        data: this.data,
        targetTreeNode: targetNode
      })
    },
    findNode (tree, parent_id) { 
      if (!tree) { return null}
      for (let node of tree) { 
        if (node.id == parent_id) { 
          return node
        }
        if (!this.$store.state.dataManager.groupListOpenNode.includes(node.id)) { 
          continue
        }
        let result = this.findNode(node.children, parent_id)
        if (result) {
          return result
        }
      }
    },
    onTreeNodeAddGroup () {
      this.$store.commit('setIsShownCreateDialog', true)
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
  }
}
</script>

<style>
.data-list-tree-node .v-btn--icon.v-size--default {
  height: 20px;
  width: 20px;
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
</style>

<style lang='scss' scoped>
  .v-application ol, .v-application ul {
    padding-left: 0px;
  }
</style>
