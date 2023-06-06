<template>
  <div>
    <snapshot-import-selector></snapshot-import-selector>
    <Split v-model="split" min=300px max=543px class="datamanager-split">
      <div slot="left">
        <data-list></data-list>
      </div>
      <div slot="right">
        <data-detail></data-detail>
      </div>
    </Split>

    <v-snackbar
      v-model="isShownReloadMessage"
      transition="slide-y-reverse-transition"
      color="primaryBrightest"
      :timeout="-1"
      rounded="pill"
      class="mb-3"
    >
      <span class="accent--text">Mock Data updated {{durationMessage}}</span>
      <v-btn text small class="px-1 ml-1" height="20" color="primary" @click.stop="loadDataMap"><b>CLICK TO UPDATE</b></v-btn>

      <template v-slot:action="{ attrs }">
        <v-btn
          plain
          v-bind="attrs"
          class="primaryLight--text"
          @click="isShownReloadMessage = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>

  </div>
</template>

<script>
import DataList from '@/views/datamanager/DataList.vue'
import DataDetail from '@/views/datamanager/DataDetail.vue'
import SnapshotImportSelector from '@/views/datamanager/SnapshotImportSelector.vue'

export default {
  components: {
    DataList,
    DataDetail,
    SnapshotImportSelector,
  },
  activated () {
    if (this.groupList.length == 0 || !this.isLoadTreeAsync) {
      this.loadDataMap()
    }
    this.$io.on('datamanagerUpdateMessage', this.onDatamanagerUpdateMessage)
  },
  deactivated() {
    this.$io.removeListener('datamanagerUpdateMessage', this.onDatamanagerUpdateMessage)
  },
  data () {
    return {
      split: 0.35,
      isShownReloadMessage: false,
      durationMessage: 'for a long time',
    }
  },
  computed: {
    groupList () {
      return this.$store.state.dataManager.groupList
    },
    isLoadTreeAsync () {
      return this.$store.state.dataManager.isLoadTreeAsync
    }
  },
  methods: {
    onDatamanagerUpdateMessage (payload) {
      this.isShownReloadMessage = true
      this.durationMessage = payload.durationMessage ? payload.durationMessage : 'for a long time'
    },
    loadDataMap () {
      this.isShownReloadMessage = false
      this.$store.dispatch('loadDataMap')
    }
  }
}
</script>

<style scoped>
.datamanager-split{
  height: calc(100vh - 44px - 40px - 28px - 12px);
  /* total:100vh
    header: 44px
    title: 40px
    tree
    margin-bottom: 12px
    footer: 28px
  */
}
</style>
