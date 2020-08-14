<template>
  <div class>
    <MockDataSelector :title="snapshotTitle" ref="searchModal" :showRoot="true">
      <template slot="modalHeader">
        <Row type="flex" justify="center" align="middle">
          <i-col span="2">
            <span>Name:</span>
          </i-col>
          <i-col span=21 offset="1">
            <i-input v-model="setMockDataName" size="small" />
          </i-col>
        </Row>
      </template>
        <template slot="selected">
        <Row style="padding-top:10px;word-break:break-all" type="flex" justify="center" align="middle">
          <i-col span="2">
            <span>Save to:</span>
          </i-col>
          <i-col span="21" offset="1">
            <b>{{rootNode.abs_parent_path}}</b>
          </i-col>
        </Row>
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
        <Button size="large" type="primary" long @click="importSnapshot()">
          <span>Save</span>
        </Button>
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
      snapshotTitle: 'Mock data selector for snapshot import',
      titleMsg: 'please select a parent node, it will be used to save snapshot mock data',
    }
  },
  computed: {
    setMockDataName: {
      get () {
        return this.$store.state.dataManager.snapshotName
      },
      set (val) {
        this.$store.commit('setSnapshotName', val)
      }
    },
    parentNode () {
      return this.$store.state.dataManager.importSnapshotParentNode
    },
    spinDisplay () {
      return this.$store.state.dataManager.spinDisplay
    },
    rootNode () {
      return this.$store.state.dataManager.importSnapshotParentNode
    }
  },
  methods: {
    changeSearchModalOpenState () {
      this.$refs.searchModal.toggal()
    },
    setSnapshotParentNode (searchResult) {
      this.$store.commit('setImportSnapshotParentNode', searchResult)
    },
    importSnapshot () {
      this.$store.commit('setSpinDisplay', true)
      this.changeSearchModalOpenState()
      this.$store.dispatch('importSnapshot')
      this.$router.push({ name: 'datamanager' })
    }
  },
  mounted () {
    if (this.$route.path == '/datamanager/import') {
      this.changeSearchModalOpenState()
      this.$store.dispatch('loadSnapshotName')
    }
  }
}
</script>
