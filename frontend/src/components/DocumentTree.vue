<template>
  <div class="document-tree">
    <v-treeview
      :items="treeData"
      v-model="selectedLeaf"
      :selectable="isSelectableStatus"
      selected-color="primary"

      :search="realSearchStr"
      :filter="searchFilter"

      expand-icon=""

      dense
      hoverable

      :open="groupListOpenNode"

      style="padding-left:0px"
    >
      <template v-slot:label="{ item, selected }">
        <v-lazy
          :options="{threshold: 0.5}"
          transition="fade-transition"
        >
          <DocumentTreeNode :data="item" :selected="selected"/>
        </v-lazy>
      </template>
    </v-treeview>
  </div>
</template>

<script>
import DocumentTreeNode from '@/components/DocumentTreeNode.vue'

export default {
  components: {
    DocumentTreeNode
  },
  props: ['treeData', 'searchStr'],
  data() {
    return {
      refreshFlowListTimer: null,
      realSearchStr: '',
      searchStrId: '',
      selectLimit: 10 // todo
    }
  },
  computed: {
    isSelectableStatus () {
      return this.$store.state.dataManager.isSelectableStatus
    },
    groupListOpenNode: {
      get () {
        return this.$store.state.dataManager.groupListOpenNode
      },
      set (val) {
        this.$store.commit('setGroupListOpenNode', val)
      }
    },
    selectedLeaf: {
      get () {
        return this.$store.state.dataManager.selectedLeaf
      }, 
      set (val) {
        this.$store.commit('setSelectedLeaf', val)
      }
    }
  },
  watch: {
    searchStr (newValue, oldValue) {
      clearTimeout(this.refreshFlowListTimer)
      this.refreshFlowListTimer = setTimeout(() => {
        if (newValue !== oldValue) {
          this.realSearchStr = this.searchStr
          clearTimeout(this.refreshFlowListTimer)
        }
      }, 1000)
    },
    selectedLeaf (newValue, oldValue) {
      // Why not computed?
      // treeview对这个值的控制，晚于computed的set。使得computed的set不能生效。
      const newValueLength = newValue.length
      const oldValueLength = oldValue.length

      if (newValueLength > this.selectLimit) {
        this.$store.state.dataManager.selectedLeaf.splice(oldValueLength)
        this.$bus.$emit('msg.error', `Select more than ${this.selectLimit} is not allowed!`)
        return
      }
    },
    searchStrId (newVal) {
      this.showNode(newVal)
    }
  },
  methods: {
    searchFilter (item, search, textKey) {
      // 不自定义时，默认忽略大小写；自定义后需要自己实现忽略大小写
      if (item.id === search) {
        this.searchStrId = item
        return true
      }
      // textKey is name
      if (item[textKey].toLowerCase().indexOf(search.toLowerCase()) > -1) {
        return true
      }
    },
    showNode (payload) {
      this.resetGroupListOpenNode(payload)
      this.resetFocusNodeInfo(payload)
      this.resetGroupDetail(payload)
    },
    resetGroupListOpenNode (payload) {
      for (const node of this.$store.state.dataManager.groupListOpenNode) {
        this.$store.commit('deleteGroupListOpenNode', node.id)
      }
      for (const parent of payload.parent) {
        this.$store.commit('addGroupListOpenNode', parent.id)
      }
    },
    resetFocusNodeInfo (payload) {
      this.$store.commit('setFocusNodeInfo', payload)
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

<style>
.tree-node-inner-row-activated {
  background-color: rgba(15, 204, 191, 0.15);
}
.document-tree .v-treeview-node__checkbox {
  margin-left: 10px;
}
.document-tree .v-treeview--dense .v-treeview-node__root{
  min-height: 32px;
  padding: 0px;
  margin-left: -28px;
}
</style>
