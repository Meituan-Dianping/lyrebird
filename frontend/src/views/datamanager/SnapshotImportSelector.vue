<template>
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
</template>

<script>

import MockDataSelector from '@/components/SearchModal.vue'

export default {
  components: {
    MockDataSelector
  },
  data () {
    return {
      snapshotTitle: 'Import snapshot',
      errorMsg: ''
    }
  },
  mounted () {
    if (this.$route.path === '/datamanager/import') {
      this.changeSearchModalOpenState()
      this.$store.dispatch('loadSnapshotName')
    } else if (this.$route.path === '/datamanager' && Object.keys(this.$route.query).length) {
      if (this.$route.query.errorMsg) {
        this.errorMsg = this.$route.query.errorMsg
        this.$bus.$emit('msg.error', this.$route.query.errorMsg)
        return
      }
      this.$store.dispatch('initSnapshotInfo', this.$route.query)
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
      this.changeSearchModalOpenState()
      this.$store.dispatch('importSnapshot')
      this.$router.push({ name: 'datamanager' })
    }
  }
}
</script>
