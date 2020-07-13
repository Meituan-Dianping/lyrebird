<template>
  <div class="root-window">
    <div class="event-inspector-split">
      <Split v-model="split">
        <div slot="left">
          <EventList class="event-inspector-left"  @click.native="getEventDetail"></EventList>
        </div>
        <div v-if="eventDetail" slot="right">
          <EventDetail v-model="eventDetail" class="event-inspector-right"></EventDetail>
        </div>
      </Split>
    </div>
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
      scrollRate: 0,
      split: 1
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
    getEventDetail () {
      if (this.eventDetail) {
        this.split = 0.5
        return true
      } else {
        this.split = 1
        return false
      }
    },
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
.event-inspector-left {
  margin-right: 0px;
}
.event-inspector-right {
  margin-left: 5px;
}
.event-inspector-split {
  height: calc(100vh - 138px);
  border: 1px solid #dcdee2;
}
</style>
