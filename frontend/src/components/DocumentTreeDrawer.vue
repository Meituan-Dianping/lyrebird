<template>
  <div class="" @click="drawerIsCollapsed=true">
    <v-navigation-drawer
      v-model="shown"
      absolute
      temporary
      hide-overlay
      right
      class=""
      width="600"
      color="rgba(230, 230, 230, 0.8)"
    >

    <!-- <v-container class="pa-0 data-list-button-bar">
      <v-row no-gutters align="center" class="mx-1">

        <v-btn icon @click.stop="reloadMockData" title="Reload mock data">
          <v-icon size="12px" color="primary">mdi-refresh</v-icon>
        </v-btn>

        <v-btn v-if="isLabelDisplay" icon @click.stop="changeLabelDisplayState" title="Hide labels">
          <v-icon size="12px" color="primary">mdi-eye-off-outline</v-icon>
        </v-btn>

        <v-btn v-else icon @click.stop="changeLabelDisplayState" title="Show labels">
          <v-icon size="12px" color="primary">mdi-eye-outline</v-icon>
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

      </v-row>

    </v-container> -->


    
      <!-- <DocumentTree :treeData="treeData" class="overflow-auto drawer-data-list" :searchStr="searchStr" :editable="true"/> -->
      <DataList :editable="false"/>
    </v-navigation-drawer>



  </div>
</template>

<script>
import DocumentTree from '@/components/DocumentTree.vue'
import DataList from '@/views/datamanager/DataList.vue'

export default {
  components: {
    DocumentTree,
    DataList
  },
  mounted() {
    this.$store.dispatch('loadDataMap')
  },
  created () {
    this.$store.dispatch('loadDataMap')
  },
  data() {
    return {
      shown: false,
      searchStr: ''
    }
  },
  computed: {
    treeData () {
      return this.$store.state.dataManager.groupList
    },
  },
  watch: {
  },
  methods: {
    toggal () {
      this.shown = !this.shown
    },
    loadDataMap () {
      
    }
  }
}
</script>

<style>
.drawer-data-list {
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
</style>
