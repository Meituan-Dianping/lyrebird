<template>

  <div>
    <v-row class="inspector-container-button-bar content-row">
      <ButtonBar/>
    </v-row>
  <v-divider class="border"></v-divider>
  <div class="inspector-realtime-split">
    <Split v-model="split" min="0px" max="0px">
      <div slot="left">
        <FlowList class="inspector-realtime-left"></FlowList>
      </div>
      <div slot="right">
        <FlowDetail v-if="focusedFlowDetail" class="inspector-realtime-right"></FlowDetail>
        <div v-else class="flow-detail-empty">No selected flow</div>
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
  data () {
    return {
      split: 1
    }
  },
  computed: {
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

<style scope>
.inspector-container-button-bar {
  height: 45px;
  display: flex;
  align-items: center;
  padding-top: 12px;
  padding-bottom: 7px;
  padding-left: 17px;
  padding-right: 12px;
}
.inspector-realtime-left {
  margin-right: 0px;
}
.inspector-realtime-right {
  margin-left: 5px;
}
.inspector-realtime-split {
  height: calc(100vh - 44px - 40px - 38px - 28px - 12px);
  /* total:100vh
  header: 44px
  title: 40px
  buttonBar: 38px
  split
  margin-bottom: 12px
  footer: 28px
    */
  width: calc(100vw - 5px - 68px - 12px);
}
.flow-detail-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}
</style>
