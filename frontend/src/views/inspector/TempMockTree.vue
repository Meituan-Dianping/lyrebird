<template>
  <div class="temp-mock-tree">

    <v-treeview
      :items="temporaryMockDataList"
      :search="realSearchStr"
      :filter="searchFilter"

      expand-icon=""

      dense
      hoverable

      :open="openNode"
      style="padding-left:0px"
    >
      <template v-slot:label="{ item }">
        <v-lazy
          :options="{threshold: 0.5}"
          transition="fade-transition"
        >
          <v-container class="pa-0 data-list-tree-node">
            <v-row
              no-gutters
              align="center"
              @mouseover="mouseOverId=item.id"
              @mouseout="mouseOverId=null"
            >
              <span>
                <v-btn v-if="item.type === 'group'" icon class="mr-1 my-0" @click.stop="onToggleStatusChange">
                  <v-icon small color="accent" :class="toggleClass">
                    mdi-chevron-down
                  </v-icon>
                </v-btn>
                <v-icon v-else small color="accent" size="14px" class="mr-1">mdi-file</v-icon>
              </span>

              <span class="tree-node-inner-text accent--text">{{item.name}}</span>

              <v-spacer/>

              <span v-show="item.id === mouseOverId && item.id !== tempMockRootId">
                <v-btn
                  icon
                  @click.stop="deleteData(item)"
                >
                  <v-icon size="12px" color="error">mdi-delete</v-icon>
                </v-btn>
              </span>

            </v-row>
          </v-container>

        </v-lazy>

      </template>
    </v-treeview>
  </div>
</template>

<script>

export default {
  props: {
    'treeData': Array,
    'searchStr': String,
  },
  data() {
    return {
      searchRefreshDataListTimer: null,
      mouseOverId: null,
      realSearchStr: '',
      openNode: []
    }
  },
  computed: {
    temporaryMockDataList () {
      return this.$store.state.dataManager.temporaryMockDataList
    },
    tempMockRootId () {
      return this.$store.state.dataManager.tempGroupId
    },
    rootOpen () {
      return this.openNode.indexOf(this.tempMockRootId) !== -1
    },
    toggleClass () {
      return !this.rootOpen ? 'toggle-icon-status' : ''
    }
  },
  watch: {
    searchStr (newValue, oldValue) {
      clearTimeout(this.searchRefreshDataListTimer)
      this.searchRefreshDataListTimer = setTimeout(() => {
        if (newValue !== oldValue) {
          this.realSearchStr = this.searchStr
          clearTimeout(this.searchRefreshDataListTimer)
        }
      }, 1000)
    },
  },
  methods: {
    searchFilter (item, search, textKey) {
      // By default, it will search case insensitively
      // Once customized `filter`, case-insensitive search needs to implement by self
      if (item.id === search) {
        return true
      }
      // textKey defaults to name, this value cannot be customized in the component
      if (item[textKey].toLowerCase().indexOf(search.toLowerCase()) > -1) {
        return true
      }
    },
    onToggleStatusChange () {
      this.openNode = this.rootOpen ? [] : ['tmp_group']
    },
    deleteData (payload) {
      this.$store.dispatch('deleteTempMockData', payload)
    }
  }
}
</script>

<style>
.temp-mock-tree .v-treeview--dense .v-treeview-node__root{
  min-height: 32px;
  padding: 0px;
  margin-left: -28px;
}
</style>
