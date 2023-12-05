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
      item-key="id"

      style="padding-left:0px"
    >
      <template v-slot:label="{ item, selected }">
        <v-lazy
          :options="{threshold: 0.5}"
          transition="fade-transition"
        >
          <DocumentTreeNode :data="item" :selected="selected" :editable="editable" :deletable="deletable"/>
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
  props: {
    'treeData': Array,
    'searchStr': String,
    'editable': {
      default: true
    },
    'deletable': {
      default: true
    }
  },
  data() {
    return {
      searchRefreshDataListTimer: null,
      realSearchStr: '',
      searchByIdResult: '',
      selectLimit: 500,
      originAsync: false
    }
  },
  created() {
    this.originAsync = this.isLoadTreeAsync
  },
  computed: {
    isSelectableStatus () {
      return this.$store.state.dataManager.isSelectableStatus
    },
    isLoadTreeAsync: {
      get () {
        return this.$store.state.dataManager.isLoadTreeAsync
      },
      set (val) {
        this.$store.dispatch('commitAndupdateConfigByKey', {
          'command': 'setIsTreeLoadAsync',
          'isShowMessage': false,
          val
        })
        this.$store.dispatch('loadDataMap')
      }
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
      clearTimeout(this.searchRefreshDataListTimer)
      this.searchRefreshDataListTimer = setTimeout(() => {
        if (newValue !== oldValue) {
          // When originAsync is true, and searchStr is not empty, close isLoadTreeAsync
          if (this.originAsync == true) {
            this.isLoadTreeAsync = newValue === ''
          }
          this.realSearchStr = this.searchStr
          clearTimeout(this.searchRefreshDataListTimer)
        }
      }, 1000)
    },
    selectedLeaf (newValue, oldValue) {
      // Why not computed?
      // The treeview's control of this value is later than the computed variable `set()`
      // Therefore, computed variable `set()` cannot take effect.
      const newValueLength = newValue.length
      const oldValueLength = oldValue.length

      if (newValueLength > this.selectLimit) {
        this.$store.state.dataManager.selectedLeaf.splice(oldValueLength)
        this.$bus.$emit('msg.error', `Select more than ${this.selectLimit} is not allowed!`)
        return
      }
    },
    searchByIdResult (newVal) {
      this.showNode(newVal)
    }
  },
  methods: {
    searchFilter (item, search, textKey) {
      // By default, it will search case insensitively
      // Once customized `filter`, case-insensitive search needs to implement by self
      if (item.id === search) {
        this.searchByIdResult = item
        return true
      }
      // textKey defaults to name, this value cannot be customized in the component
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
        this.$store.dispatch('saveTreeViewOpenNodes', this.$store.state.dataManager.groupListOpenNode)
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
.document-tree .v-treeview-node__checkbox {
  margin-left: 10px;
}
.document-tree .v-treeview--dense .v-treeview-node__root{
  min-height: 32px;
  padding: 0px;
  margin-left: -28px;
}
</style>
