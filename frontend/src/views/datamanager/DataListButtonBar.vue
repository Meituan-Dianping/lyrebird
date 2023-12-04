<template>
  <v-container class="pa-0 data-list-button-bar">
    <v-row no-gutters align="center" class="mx-1">

      <span class="mx-1">
        <b>{{title}}</b>
      </span>

      <v-btn icon @click.stop="reloadMockData" title="Reload mock data">
        <v-icon size="12px" color="primary">mdi-refresh</v-icon>
      </v-btn>

      <span v-show="editable" class="mx-1">
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
        v-model="treeSearchStr"
        flat
        hide-details
      ></v-text-field>

      <span v-show="editable">
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
      </span>

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
            v-show="editable"
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
              <v-switch v-model="isLoadTreeAsync"/>
            </v-list-item-action>

            <v-list-item-content>
              <v-list-item-title>Load asyn</v-list-item-title>
              <v-list-item-subtitle>Load data asynchronous</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

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
              <v-switch v-model="isLabelDisplay"/>
            </v-list-item-action>

            <v-list-item-content>
              <v-list-item-title>Labels</v-list-item-title>
              <v-list-item-subtitle>Display labels in each tree node</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-list-item>
            <v-list-item-action>
              <v-switch v-model="isDisplayConfiguration"/>
            </v-list-item-action>

            <v-list-item-content>
              <v-list-item-title>Configuration</v-list-item-title>
              <v-list-item-subtitle>Display configuration file in each group</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

        </v-list>

      </v-menu>

    </v-row>
  </v-container>
</template>

<script>
import LabelDropdown from '@/components/LabelDropdown.vue'

export default {
  components: {
    LabelDropdown,
  },
  props: {
    editable: {
      default: true
    }
  },
  computed: {
    title () {
      return this.$store.state.dataManager.title
    },
    selectedLabel () {
      return this.$store.state.dataManager.dataListSelectedLabel
    },
    treeSearchStr: {
      get () {
        this.$store.state.dataManager.treeSearchStr
      },
      set (val) {
        this.$store.commit('setTreeSearchStr', val)
      }
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
    isDisplayConfiguration: {
      get () {
        return this.$store.state.dataManager.isDisplayConfiguration
      },
      set (val) {
        this.$store.commit('setIsDisplayConfiguration', val)
        this.$store.dispatch('updateConfigByKey', {
          'mock.data.shownConfig': val
        })
        this.$store.dispatch('loadDataMap')
      }
    },
    isLoadTreeAsync: {
      get () {
        return this.$store.state.dataManager.isLoadTreeAsync
      },
      set (val) {
        this.$store.commit('setIsTreeLoadAsync', val)
        this.$store.dispatch('updateConfigByKey', {
          'mock.data.tree.asynchronous': val
        })
        this.$store.dispatch('loadDataMap')
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
  methods: {
    editLabel (payload) {
      // When label is not empty, close isLoadTreeAsync
      if (payload.labels.length > 0) {
        this.isLoadTreeAsync = false
      }
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
.data-list-button-bar {
  line-height: 30px;
  border-bottom: 1px solid #ddd;
  max-width: none;
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
