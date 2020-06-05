<!-- SnapshotImportSelector -->
<template>
  <div class>
    <!-- snapshot import parentNode selector -->
    <MockDataSelector ref="searchModal" :showRoot="true">
      <template slot="modalHeader">
        <div>
          <Alert show-icon>{{titleMsg}}</Alert>
        </div>
      </template>
      <template #searchItem="{ searchResult }">
        <i-row
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
        </i-row>
      </template>
      <template slot="modalFooter">
        <Divider />
        <i-row>
          <i-col span="14">
            <span>You Selected: {{importSnapshotParentNodeDisplay}}</span>
          </i-col>
          <i-col span="2" offset="1">
            <Button long @click="clearImportSnapshotParentNode">clear</Button>
          </i-col>
          <i-col span="6" offset="1">
            <Button type="success" long @click="importSnapshot()">add</Button>
          </i-col>
        </i-row>
      </template>
    </MockDataSelector>
  </div>
</template>

<script>

import MockDataSelector from '@/components/SearchModal.vue'
import { bus } from '../../eventbus'
import * as api from '../../api'

export default {
  components: {
    MockDataSelector
  },
  data () {
    return {
      titleMsg: 'please select a parent node, it will be used to save snapshot mock data',
    };
  },
  computed: {
    importSnapshotParentNodeDisplay () {
      let node = this.$store.state.dataManager.importSnapshotParentNode
      return '' ? Object.keys(node).length == 0 : `【${node['id']}】+【${node['name']}】`
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
      api
        .importSnapshot(this.parentNode)
        .then((res) => {
          if (res.data.code === 1000) {
            this.$store.commit('setSpinDisplay', false)
            bus.$emit('msg.success', res.data.message)
            this.$router.push({ name: 'datamanager' })
            this.$store.dispatch('loadDataMap')
          }
        }).catch(err => {
          this.$store.commit('setSpinDisplay', false)
          bus.$emit('msg.error', err.data.message)
          this.$router.push({ name: 'datamanager' })
          this.$store.dispatch('loadDataMap')
        })
    },
  },
  mounted () {
    if (this.$route.path == '/datamanager/import') {
      this.changeSearchModalOpenState();
    }
  }
}
</script>
