<template>
  <div class="split-right-table">
    <Split v-model="detailSplit" mode="vertical">
      <div ref="eventContainer" slot="top" class="demo-split-pane">
        <EventInspector ref="eventList"></EventInspector>
      </div>
      <div slot="bottom" class="demo-split-pane">
        <CodeEditor read-only language="json" v-model="eventDetail" style="height:800px"></CodeEditor>
      </div>
    </Split>
  </div>
</template>

<script>
import EventInspector from '@/views/event/EventInspector.vue'
import CodeEditor from '@/views/event/CodeEditor.vue'

export default {
  components: {
    EventInspector,
    CodeEditor
  },
  data () {
    return {
      detailSplit: 0.6,
      scrollRate: 0
    }
  },
  created () {
    this.$bus.$on('eventLitScroll', this.setEventContainerScroll)
  },
  computed: {
    eventDetail: {
      get () {
        return this.$store.state.event.eventDetail
      },
      set (val) {

      }
    }
  },
  methods: {
    addDescAttach (row) {
      if (this.channelAddToDesc.indexOf(row.channel) > -1) {
        this.dispatch('addIntoDesc', row.id)
      } else if (this.channelAddToAttach.indexOf(row.channel) > -1) {
        this.dispatch('addIntoAttach', row.id)
      }
      this.$Message.error(
        'Add description and attachments have not supported yet!'
      )
    },
    timestampToTime (timeStamp) {
      let date = new Date(timeStamp * 1000)
      let hour = date.getHours() + ':'
      let minute =
        (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()) +
        ':'
      let second =
        date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds()
      return hour + minute + second
    },
    getColunmsFilterItem () {
      return []
    },
    setEventContainerScroll (event) {
      this.scrollRate = event
      setTimeout(() => {
        const container = this.$refs.eventContainer
        const topHeight = container.scrollHeight * event
        this.$refs.eventContainer.scrollTop = topHeight - (container.scrollHeight / 20)
      }, 1)
    }
  }
}
</script>

<style scoped>
.split-right-table {
  height: calc(100vh - 66px);
  /* total:100vh
    form
    padding: 10px
    button: 32px
    padding: 10px
    */
  overflow-y: auto;
  border-bottom: 1px solid #dcdee2;
}
.demo-split {
  height: 200px;
  border: 1px solid #dcdee2;
}
.demo-split-pane {
  padding: 10px;
  overflow-y: auto;
  height: 100%;
}
</style>
