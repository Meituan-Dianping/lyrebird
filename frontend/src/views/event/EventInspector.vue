<template>
  <div class="root-window">
    <Row>
      <Col :span="listSpan">
        <EventList class="inspector-left"></EventList>
      </Col>
      <div class="split" v-if="eventDetail"></div>
      <Col span="12" v-if="eventDetail">
        <EventDetail v-model="eventDetail" class="inspector-right"></EventDetail>
      </Col>
    </Row>
  </div>
</template>

<script>
import EventList from '@/views/event/EventList.vue'
import EventDetail from '@/views/event/EventDetail.vue'
import CodeEditor from '@/components/CodeEditor.vue'

export default {
  components: {
    EventList,
    EventDetail,
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
    listSpan () {
      if (this.eventDetail) {
        return '12'
      } else {
        return '24'
      }
    },
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
.content-pane {
  height: calc(100% - 60px);
}
.inspector-left {
  margin-right: 0px;
}
.inspector-right {
  margin-left: 5px;
}
.split {
  display: block;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  border: 1px dashed #eee;
}
</style>
