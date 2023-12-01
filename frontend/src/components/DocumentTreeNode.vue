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
          <v-icon small :color="toggleColor" :class="toggleClass">
            {{ isLoading ? 'mdi-autorenew': 'mdi-chevron-down' }}
          </v-icon>
        </v-btn>
        <v-icon v-else-if="data.type === 'json'" small :color="iconColor" size="14px" class="mr-1">mdi-alpha-j-box-outline</v-icon>
        <v-icon v-else-if="data.type === 'config'" small :color="iconColor" size="14px" class="mr-1">mdi-file-cog-outline</v-icon>
        <v-icon v-else small :color="iconColor" size="14px" class="mr-1">mdi-file</v-icon>
      </span>

      <span>
        <div class="status-point" v-show="isGroupActivated"/>
        <span :class="nameClass">
          <span v-if="data.parent_id">{{data.name}}</span>
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

        <v-btn
          icon
          @click="changeMenuStatus"
          class="mr-1"
          v-show="isNodeEditable"
        >
          <v-icon
            size="12px" 
            color="primary"
          >mdi-dots-horizontal</v-icon>
        </v-btn>

      </span>

    </v-row>
  </v-container>
</template>

<script>

import { getGroupChildren } from '@/api'

export default {
  props: ['data', 'selected', 'editable', 'deletable'],
  data () {
    return {
      isMouseOver: false,
      isLoading: false,
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
      if (this.data.link) {
        return ['tree-node-inner-text', 'accent--text', 'text--secondary']
      }
      return ['tree-node-inner-text', 'accent--text']
    },
    toggleClass () {
      if (this.isLoading) {
        return 'loading-icon'
      }
      if (!this.isNodeOpen) {
        return 'toggle-icon-status'
      }
      return ''
    },
    toggleColor () {
      if (this.isGroupActivated) {
        return 'success'
      }
      if (this.isNodeFocused) {
        return 'primary'
      }
      if (!this.isNodeOpen) {
        return 'accent'
      }
      if (this.data.children && this.data.children.length) {
        return 'accent'
      }
      return 'content'
    },
    iconColor () {
      return this.data.link ? 'text--secondary' : 'accent'
    },
    isSelectableStatus () {
      return this.$store.state.dataManager.isSelectableStatus
    },
    isGroupActivated () {
      return this.$store.state.inspector.activatedGroup.hasOwnProperty(this.data.id)
    },
    isNodeFocused () {
      return this.$store.state.dataManager.focusNodeInfo && this.data.id === this.$store.state.dataManager.focusNodeInfo.id
    },
    isNodeDeletable () {
      return this.deletable && this.$store.state.dataManager.treeUndeletableId.indexOf(this.data.id) === -1
    },
    isNodeEditable () {
      return this.editable && this.data.type !== 'config'
    },
    isNodeOpen () {
      return this.$store.state.dataManager.groupListOpenNode.indexOf(this.data.id) > -1
    },
    isDisplayConfiguration () {
      return this.$store.state.dataManager.isDisplayConfiguration
    },
    isLoadTreeAsync () {
      return this.$store.state.dataManager.isLoadTreeAsync
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
    changeDeleteDialogStatus () {
      this.$store.commit('setDeleteNode', [this.data])
      this.$store.commit('setDeleteDialogSource', 'single')
      this.$store.commit('setIsShownDeleteDialog', true)
    },
    changeMenuStatus (e) {
      e.preventDefault()
      this.$store.commit('setIsShownNodeMenu', true)
      this.$store.commit('setShownNodeMenuPosition', {'x': e.clientX, 'y': e.clientY})
    },
    onToggleStatusChange () {
      if (this.isNodeOpen) {
        this.$store.commit('deleteGroupListOpenNode', this.data.id)
        return
      } 
      if (!this.isLoadTreeAsync) {
        this.$store.commit('addGroupListOpenNode', this.data.id)
        return
      }
      if (this.isLoading) {
        return
      }

      this.isLoading = true
      getGroupChildren(this.data.id)
        .then(response => {
          this.data.children = response.data.data
          this.isLoading = false
          this.$store.commit('addGroupListOpenNode', this.data.id)
        })
        .catch(error => {
          this.$bus.$emit('msg.error', 'Load group ' + this.data.name + ' children error: ' + error.data.message)
        })
    },
    onTreeNodeClick () {
      if (!this.editable) {
        return
      }
      this.$store.commit('setFocusNodeInfo', this.data)
      if (this.data.type === 'group') {
        this.$store.dispatch('loadGroupDetail', this.data)
      } else if (this.data.type === 'data') {
        this.$store.dispatch('loadDataDetail', this.data)
      } else if (this.data.type === 'json') {
        this.$store.dispatch('loadDataDetail', this.data)
      } else if (this.data.type === 'config') {
        this.$store.dispatch('loadDataDetail', this.data)
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
.toggle-icon-status {
  transform:rotate(-90deg);
}
.loading-icon {
  animation-name: loading-icon-rotate;
  animation-duration: 800ms;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}
@keyframes loading-icon-rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
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
