<template>
  <div class="root-window">
    <div class="search-box">
      <input type="text" />
    </div>
    <div class="content-pane">
      <Split v-model="detailSplit" mode="vertical">
        <div ref="eventContainer" slot="top" class="demo-split-pane">
          <EventInspector ref="eventList"></EventInspector>
        </div>
        <div slot="bottom" class="demo-split-pane">
          <CodeEditor read-only language="json" v-model="eventDetail" style="height:800px"></CodeEditor>
        </div>
      </Split>
    </div>
  </div>
</template>

<script>
import EventInspector from '@/views/event/EventInspector.vue'
import CodeEditor from '@/components/CodeEditor.vue'

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
.root-window {
  height: 100%;
  overflow-y: auto;
  border-bottom: 1px solid #dcdee2;
}
.demo-split-pane {
  padding: 10px;
  overflow-y: auto;
  height: 100%;
}
.search-box {
  height: 60px;
}
.content-pane {
  height: calc(100% - 60px);
}
</style>
