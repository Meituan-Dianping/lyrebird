<template>

  <div style="padding:12px">
    <v-row class="inspector-container-button-bar">
      <ButtonBar/>
    </v-row>

    <v-divider class="border"/>

    <div class="inspector-realtime-split">
      <Split v-model="split" min="0px" max="0px">
        <div slot="left">
          <FlowList class="inspector-realtime-left"></FlowList>
        </div>
        <div slot="right">
          <FlowDetail class="inspector-realtime-right"></FlowDetail>
        </div>
      </Split>
    </div>
  </div>
</template>

<script>
import ButtonBar from '@/views/inspector/ButtonBar.vue'
import FlowList from '@/views/inspector/FlowList.vue'
import FlowDetail from '@/views/inspector/FlowDetail.vue'

export default {
  components: {
    ButtonBar,
    FlowList,
    FlowDetail
  },
  computed: {
    split: {
      get() {
        return this.$store.state.inspector.inspectorSplit
      },
      set(val) {
        this.$store.commit('setInspectorSplit', val)
      }
    },
    focusedFlowDetail () {
      return this.$store.state.inspector.focusedFlowDetail
    },
  },
  watch: {
    focusedFlowDetail (val) {
      if (!val) {
        this.split = 1
      } else if (this.split === 1) {
        this.split = 0.5
      } else { }
    }
  }
}
</script>

<style scoped>
.inspector-container-button-bar {
  height: 26px;
  display: flex;
  align-items: center;
  margin: 0px 0px 7px 0px !important;
}
.inspector-realtime-left {
  margin-right: 0px;
}
.inspector-realtime-right {
  margin-left: 5px;
}
.inspector-realtime-split {
  height: calc(100vh - 44px - 40px - 38px - 4px - 12px - 12px - 28px);
  /* total:100vh
  header: 44px
  title: 40px
  padding: 12px
  buttonBar: 26px
  margin-top: 4px
  split
  padding: 12px
  margin-bottom: 12px
  footer: 28px
    */
  width: calc(100vw - 5px - 68px - 12px - 12px - 3px);
}
</style>
