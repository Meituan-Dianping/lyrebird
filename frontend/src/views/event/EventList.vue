<template>
  <div class="event-list">
    <Table
      ref="eventTable"
      size="small"
      highlight-row
      :columns="columns"
      :data="events"
      @on-filter-change="onFilterChange"
      @on-row-click="onRowClick"
      class="event-table"
      :height="tableHeight"
    >
      <template slot-scope="{ row }" slot="action">
        <ContextMenuItem>
          <!-- <Button type="text" shape="circle" icon="ios-add-circle-outline" @click="onAddEvent(row)"></Button> -->
        </ContextMenuItem>
      </template>
      <template slot-scope="{ row }" slot="timestamp">
        <ContextMenuItem>
          <div>{{ts2String(row.timestamp)}}</div>
        </ContextMenuItem>
      </template>
      <template slot-scope="{ row }" slot="channel">
        <ChannelColumn :channel="row.channel"></ChannelColumn>
      </template>
      <template slot-scope="{ row }" slot="content">
        <component :is="contentComponentName(row.content)" :event="content2Obj(row.content)"></component>
      </template>
    </Table>
    <div class="page">
      <Page
        v-if="page"
        :current="page.index+1"
        :total="page.count*page.size"
        :page-size="page.size"
        @on-change="onPageChange"
      ></Page>
    </div>
    <div
      v-show="isContextMenuShown"
      class="row-contextmenu ivu-select-dropdown"
      :style="{left:contextMenuLeft, top:contextMenuTop}"
    >
      <ul class="ivu-dropdown-menu" style="padding-left:0px">
        <li class="ivu-dropdown-item" @click="onContextMenuShowNotice">Show notice</li>
        <li class="ivu-dropdown-item" @click="onContextMenuShowAll">Show all</li>
        <li v-show="isSnapshot" class="ivu-dropdown-item" @click="onContextMenuExportSnapshot">Export snapshot</li>
      </ul>
    </div>
  </div>
</template>

<script>
import FlowTableItem from '@/views/event/FlowTableItem.vue'
import CustomTableItem from '@/views/event/CustomTableItem.vue'
import ChannelColumn from '@/views/event/ChannelColumn.vue'
import ContextMenuItem from '@/views/event/ContextMenuItem.vue'

export default {
  components: {
    FlowTableItem,
    CustomTableItem,
    ChannelColumn,
    ContextMenuItem
  },
  created () {
    const urlParams = new URLSearchParams(window.location.search)
    const eventId = urlParams.get('event_id')
    this.$store.dispatch('loadChannelNames')
    this.$bus.$on('contextmenu.show', this.showContextMenu)
    this.$bus.$on('contextmenu.dismiss', this.dismissContextMenu)
    this.$io.on('db_action', this.reload)
  },
  mounted () {
    this.reload()
    this.tableRect = this.$refs.eventTable.$el.getBoundingClientRect()
    this.onResize()
    window.addEventListener('resize', this.onResize)
  },
  beforeDestroy () {
    window.removeEventListener('resize', this.onResize)
    this.$io.removeListener('db_action', this.reload)
  },
  data () {
    return {
      tableRect: null,
      tableHeight: 500,
      isContextMenuShown: false,
      contextMenuLeft: 0,
      contextMenuTop: 0,
      refreshEventListTimer: null,
    }
  },
  computed: {
    events () {
      return this.$store.state.event.events
    },
    page () {
      return this.$store.state.event.page
    },
    channelNames () {
      return this.$store.state.event.channelNames
    },
    columns () {
      let filters = []
      for (const channelName of this.$store.state.event.channelNames) {
        filters.push({ label: channelName, value: channelName })
      }
      return [
        {
          title: '',
          slot: 'action',
          width: 35
        },
        {
          title: 'Time',
          key: 'timestamp',
          slot: 'timestamp',
          width: 90
        },
        {
          title: 'Channel',
          key: 'channel',
          slot: 'channel',
          width: 80,
          filters: filters,
          filteredValue: this.$store.state.event.channelFilters,
          filterRemote (value) {
            this.$store.dispatch('updateChannelFilters', value)
          }
        },
        {
          title: 'Content',
          key: 'content',
          slot: 'content'
        }
      ]
    },
    isSnapshot () {
      let selectedEvent = this.$store.state.event.selectedEvent
      return selectedEvent && selectedEvent.channel === 'snapshot'
    },
    eventSearchStr () {
      return this.$store.state.event.eventSearchStr
    },
  },
  watch: {
    eventSearchStr (newValue, oldValue) {
      if (newValue === null) {
        newValue = ''
      }
      clearTimeout(this.refreshEventListTimer)
      this.refreshEventListTimer = setTimeout(() => {
        if (newValue.trim() !== oldValue.trim()) {
          this.reload()
          clearTimeout(this.refreshEventListTimer)
        }
      }, 500)
    }
  },
  methods: {
    reload () {
      this.$store.dispatch('loadEvents', { page: this.$store.state.event.paginationIndex })
    },
    content2Obj (content) {
      return JSON.parse(content)
    },
    contentComponentName (content) {
      const eventObj = JSON.parse(content)
      if (eventObj.channel === 'flow') {
        return 'FlowTableItem'
      } else {
        return 'CustomTableItem'
      }
    },
    onFilterChange (opt) {
      console.log('filter change', opt)
    },
    onRowClick (row) {
      this.$store.commit('setSelectedEventId', row.event_id)
      this.$store.commit('setSelectedEvent', row)
      const prettyJson = JSON.stringify(JSON.parse(row.content), null, 2)
      this.$store.commit('setEventDetail', prettyJson)
      this.isContextMenuShown = false
    },
    ts2String (timeStamp) {
      let date = new Date(timeStamp * 1000)
      let hour = date.getHours() + ':'
      let minute = (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()) + ':'
      let second = date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds()
      return date.getMonth() + 1 + '-' + date.getDate() + ' ' + hour + minute + second
    },
    onPageChange (page) {
      this.$store.commit('setSelectedEventId', null)
      this.$store.commit('setEventDetail', '')
      this.$store.dispatch('loadEvents', { page: page - 1 })
      this.$store.commit('setPaginationIndex', page - 1)
    },
    onAddEvent (row) {
      const eventObj = JSON.parse(row.content)
      if (eventObj.summary) {
        this.$bus.$emit('addSummary', eventObj.summary)
      }
      if (eventObj.message) {
        this.$bus.$emit('addMessage', {
          channel: eventObj.channel,
          message: eventObj.message
        })
      }
      if (eventObj.attachments) {
        this.$bus.$emit('addAttachments', eventObj.attachments)
      }
    },
    showContextMenu (event) {
      const rect = this.$refs.eventTable.$el.getBoundingClientRect()
      this.contextMenuLeft = event.pageX - rect.left + 'px'
      this.contextMenuTop = event.pageY - this.tableRect.top + 'px'
      this.isContextMenuShown = true
    },
    dismissContextMenu () {
      this.isContextMenuShown = false
    },
    onContextMenuShowNotice () {
      this.$store.dispatch('showNotice')
      this.isContextMenuShown = false
    },
    onContextMenuShowAll () {
      this.$store.dispatch('showAll')
      this.isContextMenuShown = false
    },
    onContextMenuExportSnapshot () {
      this.$store.dispatch('exportSnapshotFromEvent')
      this.isContextMenuShown = false
    },
    onResize () {
      /* reset table height
      Header 44px
      Title 40px
      padding: 12px
      PaginationBar 32px
      buttonBar: 26px
      margin-bottom: 7px + line 1px = 8px
      table margin-top: 8px
      5px
      Margin Bottom: 12px
      Footer 28px
      */
      this.tableHeight = window.innerHeight - 44 - 40 - 12 - 32 - 26 - 8 - 8 - 5 - 28 - 12
    }
  }
}
</script>

<style less>
.event-list {
  height: calc(100vh - 44px - 40px - 26px - 8px - 8px - 12px - 28px - 12px);
  /* total:100vh
  header: 44px
  title: 40px
  padding: 12px
  buttonBar: 26px
  margin-bottom: 7px + line 1px = 8px
  table margin-top: 8px
  footer: 28px
  margin-bottom:12px
    */
  overflow-y: auto;
}
.page {
  text-align: center;
  margin-top: 5px;
}
.event-table {
  height: calc(100vh - 44px - 40px - 12px - 26px - 8px - 8px - 32px - 5px - 28px - 12px) !important;
  /* total:100vh
  header: 44px
  title: 40px
  padding: 12px
  buttonBar: 26px
  margin-bottom: 7px + line 1px = 8px
  table margin-top: 8px
  margin-top: 5px
  Page: 32px
  footer: 28px
  margin-bottom:12px
    */
}
.event-table .ivu-table-cell {
  padding-left: 3px;
  padding-right: 3px;
}
.row-contextmenu {
  position: absolute;
}
</style>
