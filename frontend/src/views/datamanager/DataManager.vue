<template>
  <div class="snapshot-import-spin">
    <!-- snapshot import spin -->
    <Spin fix v-if="isSpin">
      <Icon type="ios-loading" size="25" class="snapshot-import-spin-icon-load"></Icon>
      <div>
        <span style="font-size:25px">importing snapshot……</span>
      </div>
    </Spin>
    <!-- snapshot import parentNode selector -->
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
          <Col span="24">
            <p class="search-item">
              <b v-if="searchResult.parent_id" class="search-item-title">{{searchResult.name}}</b>
              <Icon v-else type="ios-home" class="search-item-title" />
              <span class="search-item-path">{{searchResult.abs_parent_path}}</span>
            </p>
          </Col>
        </Row>
      </template>
      <template slot="modalFooter">
        <Divider />
        <Row>
          <Col span="14">
            <span>You Selected: {{importSnapshotParentNodeShow}}</span>
          </Col>
          <Col span="2" offset="1">
            <Button long @click="clearImportSnapshotParentNode">clear</Button>
          </Col>
          <Col span="6" offset="1">
            <Button type="success" long @click="importSnapshot()">add</Button>
          </Col>
        </Row>
      </template>
    </MockDataSelector>
    <Split v-model="split" class="datamanager-split">
      <div slot="left">
        <data-list></data-list>
      </div>
      <div slot="right">
        <data-detail></data-detail>
      </div>
    </Split>
  </div>
</template>

<script>
import DataList from '@/views/datamanager/DataList.vue'
import DataDetail from '@/views/datamanager/DataDetail.vue'
import MockDataSelector from '@/components/SearchModal.vue'
import { bus } from '../../eventbus'
import * as api from '../../api'

export default {
  methods: {
    changeSearchModalOpenState () {
      this.$refs.searchModal.toggal()
    },
    setSnapshotParentNode(searchResult){
      this.selected = searchResult
      this.$store.commit('setImportSnapshotParentNode', searchResult)
    },
    clearImportSnapshotParentNode(){
      this.$store.commit('setImportSnapshotParentNode', {})
    },
    importSnapshot(){
      this.isSpin = true
      this.changeSearchModalOpenState()
      api
        .importSnapshot(this.parentNode)
        .then((res) => {
          if (res.data.code === 1000) {
            this.isSpin = false
            bus.$emit("msg.success", res.data.message)
            this.$router.push({ name: "datamanager" })
            this.$store.dispatch('loadDataMap')
          }
        }).catch(err => {
          this.isSpin = false
          bus.$emit("msg.error", err.data.message)
          this.$router.push({ name: "datamanager" })
          this.$store.dispatch('loadDataMap')
        })
    },
  },
  components: {
    DataList,
    DataDetail,
    MockDataSelector
  },
  mounted () {
    this.$store.dispatch('loadDataMap')
    if (this.$route.path == "/datamanager/import") {
      this.changeSearchModalOpenState()
    }
  },
  computed: {
    importSnapshotParentNodeShow () {
      let node = this.$store.state.dataManager.importSnapshotParentNode
      if (Object.keys(node).length == 0) {
        return ""
      }
      return `【${node["id"]}】+【${node["name"]}】`
    },
    parentNode () {
      return this.$store.state.dataManager.importSnapshotParentNode
    }
  },

  data () {
    return {
      split: 0.35,
      titleMsg: "please select a parent node, it will be used to save snapshot mock data",
      isSpin: false
    }
  }
}
</script>

<style scoped>
.datamanager-split{
  height: calc(100vh - 66px);
  /* total:100vh
    header: 38px
    tree
    footer: 28px
  */
  border: 1px solid #dcdee2;
}
.snapshot-import-spin{
  height: 100%;
  position: relative;
}
.snapshot-import-spin-icon-load{
  animation: ani-demo-spin 1s linear infinite;
}
</style>
