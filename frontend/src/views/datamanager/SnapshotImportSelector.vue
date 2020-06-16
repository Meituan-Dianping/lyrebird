<!-- SnapshotImportSelector -->
<template>
  <div class>
    <MockDataSelector ref="searchModal" :showRoot="true">
      <template slot="modalHeader">
        <div>
          <Alert show-icon>{{titleMsg}}</Alert>
        </div>
      </template>
      <template #searchItem="{ searchResult }">
        <Row
          type="flex"
          align="middle"
          class="search-row"
          @click.native="setSnapshotParentNode(searchResult)"
        >
          <i-col span="24">
            <p class="search-item">
              <b v-if="searchResult.parent_id" class="search-item-title">{{searchResult.name}}</b>
              <Icon v-else type="ios-home" class="search-item-title" />
              <span class="search-item-path">{{searchResult.abs_parent_path}}</span>
            </p>
          </i-col>
        </Row>
      </template>
      <template slot="modalFooter">
        <Divider />
        <Row>
          <i-col span="14">
            <span>You Selected: {{importSnapshotParentNodeDisplay}}</span>
          </i-col>
          <i-col span="2" offset="1">
            <Button long @click="clearImportSnapshotParentNode">clear</Button>
          </i-col>
          <i-col span="6" offset="1">
            <Button type="success" long @click="importSnapshot()">add</Button>
          </i-col>
        </Row>
      </template>
    </MockDataSelector>
  </div>
</template>

<script>

import MockDataSelector from '@/components/SearchModal.vue'

export default {
  components: {
    MockDataSelector
  },
  data () {
    return {
      titleMsg: 'please select a parent node, it will be used to save snapshot mock data',
    }
  },
  computed: {
    importSnapshotParentNodeDisplay () {
      let node = this.$store.state.dataManager.importSnapshotParentNode
      return Object.keys(node).length == 0  ? '' : `【${node['id']}】+【${node['name']}】`
    },
    parentNode () {
      return this.$store.state.dataManager.importSnapshotParentNode
    },
    spinDisplay () {
      return this.$store.state.dataManager.spinDisplay
    }
  },
  methods: {
    clearImportSnapshotParentNode () {
      this.$store.commit('setImportSnapshotParentNode', {})
    },
    changeSearchModalOpenState () {
      this.$refs.searchModal.toggal()
    },
    setSnapshotParentNode (searchResult) {
      this.selected = searchResult
      this.$store.commit('setImportSnapshotParentNode', searchResult)
    },
    importSnapshot () {
      this.$store.commit('setSpinDisplay', true)
      this.changeSearchModalOpenState()
      this.$store.dispatch('importSnapshot',this.parentNode)
      this.$router.push({ name: "datamanager" });
      
    },
  },
  mounted () {
    if (this.$route.path == '/datamanager/import') {
      this.changeSearchModalOpenState()
    }
  }
}
</script>
