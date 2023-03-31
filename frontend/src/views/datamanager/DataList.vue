<template>
  <div>
    <v-container class="pa-0 data-list-button-bar">
      <v-row no-gutters align="center" class="mx-1">

        <span class="mx-1">
          <b>{{title}}</b>
        </span>

        <v-btn icon @click.stop="reloadMockData" title="Reload mock data">
          <v-icon size="12px" color="primary">mdi-refresh</v-icon>
        </v-btn>

        <span class="mx-1">
          <LabelDropdown :initLabels="selectedLabel" :placement="'bottom-end'" @onLabelChange="editLabel">
            <template #dropdownButton>
              <v-btn text small class="px-0" height="20" color="primary">
                <span>Labels</span>
                <v-icon size="12px">mdi-menu-down</v-icon>
              </v-btn>
            </template>
          </LabelDropdown>
        </span>

        <v-text-field
          class="data-list-button-bar-search shading"
          placeholder="Search name/id"
          prepend-inner-icon="mdi-magnify"
          filled
          dense
          rounded
          height=12
          v-model="searchStr"
          flat
          hide-details
        ></v-text-field>

        <span v-if="isSelectableStatus">
          <v-btn text small class="px-0" height="20" color="primary" @click.stop="changeSelectableStatus">
            <span>Cancel</span>
          </v-btn>

          <v-divider vertical class="mx-1 data-list-button-bar-divider content"/>

          <v-btn
            icon
            @click.stop="changeDeleteDialogStatus"
            :disabled="selectedLeaf.length===0"
            title="Delete"
          >
            <v-icon size="12px" color="primary">mdi-trash-can-outline</v-icon>
          </v-btn>
        </span>

        <v-btn v-else icon class="ml-1" @click.stop="changeSelectableStatus" title="Select mode">
          <v-icon size="12px" color="primary">mdi-pencil</v-icon>
        </v-btn>

        <v-menu
          left
          bottom
          offset-y
          offset-overflow
          :close-on-content-click="false"
          style="position: absolute;"
        >

          <template v-slot:activator="{ on, attrs }">
            <v-btn
              icon
              v-bind="attrs"
              v-on="on"
              class="ml-1"
              title="Settings"
            >
              <v-icon size="12px" color="primary">mdi-cog-outline</v-icon>
            </v-btn>
          </template>

          <v-list dense>
            <v-list-item>
              <v-list-item-action>
                <v-switch v-model="isPreloadDataMap"/>
              </v-list-item-action>

              <v-list-item-content>
                <v-list-item-title>Preload</v-list-item-title>
                <v-list-item-subtitle>Proload DataTree before entering DataManager</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-action>
                <v-switch v-model="isReloadWhenEnter"/>
              </v-list-item-action>

              <v-list-item-content>
                <v-list-item-title>Reload</v-list-item-title>
                <v-list-item-subtitle>Reload when entering DataManager</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-action>
                <v-switch v-model="isLabelDisplay"/>
              </v-list-item-action>

              <v-list-item-content>
                <v-list-item-title>Labels</v-list-item-title>
                <v-list-item-subtitle>Display labels in each tree nodes</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>

        </v-menu>

      </v-row>
    </v-container>
    
    <Row>
      <v-overlay
        :absolute="true"
        opacity="0.8"
        color="#ffffff"
        :value="spinShow"
        z-index=3
      >
        <v-progress-circular
          size="30"
          color="primary"
          width="2"
          indeterminate
        />
      </v-overlay>
      <DocumentTree :treeData="treeData" class="overflow-auto data-list" :searchStr="searchStr"/>
    </Row>
    <DeleteDialog/>
    <CreateDialog/>
    <DuplicateDialog/>
  </div>
</template>

<script>
import LabelDropdown from '@/components/LabelDropdown.vue'
import DocumentTree from '@/components/DocumentTree.vue'
import DeleteDialog from '@/components/DocumentTreeDialogDelete.vue'
import CreateDialog from '@/components/DocumentTreeDialogCreate.vue'
import DuplicateDialog from '@/components/DocumentTreeDialogDuplicate.vue'
import { searchGroupByName } from '@/api'

export default {
  components: {
    LabelDropdown,
    DocumentTree,
    CreateDialog,
    DuplicateDialog,
    DeleteDialog,
  },
  data () {
    return {
      searchStr: ''
    }
  },
  computed: {
    treeData () {
      return this.$store.state.dataManager.groupList
    },
    spinShow () {
      return this.$store.state.dataManager.isLoading
    },
    title () {
      return this.$store.state.dataManager.title
    },
    selectedLabel () {
      return this.$store.state.dataManager.dataListSelectedLabel
    },
    isLabelDisplay: {
      get () {
        return this.$store.state.dataManager.isLabelDisplay
      },
      set (val) {
        this.$store.commit('setIsLabelDisplay', val)
        this.$store.dispatch('updateConfigByKey', {
          'mock.data.showLabel': val
        })
      }
    },
    isReloadWhenEnter: {
      get () {
        return this.$store.state.dataManager.isReloadWhenEnter
      },
      set (val) {
        this.$store.commit('setIsReloadWhenEnter', val)
        this.$store.dispatch('updateConfigByKey', {
          'mock.data.tree.forceReload': val
        })
      }
    },
    isPreloadDataMap: {
      get () {
        return this.$store.state.settings.preLoadFuncSet.has('loadDataMap')
      },
      set (val) {
        val ? this.$store.commit('addPreLoadFuncSet', 'loadDataMap') : this.$store.commit('deletePreLoadFuncSet', 'loadDataMap')
        this.$store.dispatch('updateConfigByKey', {
          'mock.data.tree.preload': val
        })
      }
    },
    isSelectableStatus () {
      return this.$store.state.dataManager.isSelectableStatus
    },
    selectedLeaf () {
      return this.$store.state.dataManager.selectedLeaf
    }
  },
  watch: {
    treeData (val) {
      // Why does treeDate have Watchers, while treeData is computed property?
      // When Vue is still on mounting, value of "computed properties" is an observer, not an actual data
      if (val.length && this.$store.state.snapshot.importGroupId) {
        this.setDisplayDataDeteil()
      }
    }
  },
  methods: {
    showNode (payload) {
      this.resetGroupListOpenNode(payload)
      this.resetFocusNodeInfo(payload)
      this.resetGroupDetail(payload)
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
      this.$store.commit('setFocusNodeInfo', payload)
    },
    resetGroupDetail (payload) {
      if (payload.type === 'group') {
        this.$store.dispatch('loadGroupDetail', payload)
      } else if (payload.type === 'data') {
        this.$store.dispatch('loadDataDetail', payload)
      } else { }
    },
    setDisplayDataDeteil () {
      const importGroupId = this.$store.state.snapshot.importGroupId
      searchGroupByName(importGroupId)
        .then(response => {
          const searchResults = response.data.data
          if (searchResults.length < 1) {
            this.$bus.$emit('msg.error', 'Load snapshot ' + importGroupId + ' error: Group id not found!')
            return
          }
          // Not handle situation of more than one groups have the same uuid
          // Only the first or searchResults is used
          const importGroup = searchResults[0]
          this.showNode(importGroup)
          this.$store.commit('clearImportGroupId')
          this.$bus.$emit('msg.success', 'Load snapshot ' + importGroup.name + ' success! ')
        }).catch(error => {
          this.$bus.$emit('msg.error', 'Load snapshot ' + importGroupId + ' error: ' + error.data.message)
        })
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
    },
    changeSelectableStatus () {
      this.$store.commit('setIsSelectableStatus', !this.isSelectableStatus)
      this.$store.commit('setSelectedLeaf', [])
    },
    changeDeleteDialogStatus () {
      this.$store.commit('setDeleteNode', Array.from(this.$store.state.dataManager.selectedNode))
      this.$store.commit('setDeleteDialogSource', 'multiple')
      this.$store.commit('setIsShownDeleteDialog', true)
    },
    reloadMockData () {
      this.$store.dispatch('loadDataMap')
    }
  }
}
</script>

<style>
.data-list {
  height: calc(100vh - 44px - 40px - 30px - 1px - 12px - 28px);
  /* total:100vh
    header: 44px
    title: 40px
    button-bar: 30px
    border: 1px
    tree
    margin-bottom: 12px
    footer: 28px
  */
}
.data-list-button-bar {
  line-height: 30px;
  border-bottom: 1px solid #ddd;
}
.data-list-button-bar .v-btn--icon.v-size--default {
  height: 20px;
  width: 20px;
}
.data-list-button-bar-divider {
  height: 15px;
}
.data-list-button-bar-search {
  font-size: 12px;
  width: 50px;
  height: 20px !important;
}
.data-list-button-bar-search .v-input__prepend-inner {
  margin-top: -2px !important;
}
.data-list-button-bar-search .v-input__slot {
  padding: 0px 4px !important;
  min-height: 20px !important;
  height: 20px !important;
}
.data-list-button-bar-search .v-icon.v-icon {
  font-size: 12px;
}
.data-list-button-bar-search .v-text-field input {
  font-size: 12px;
  padding: 0px !important;
}
</style>
