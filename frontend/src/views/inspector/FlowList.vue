<template>
  <div class="flow-list">
    <v-data-table
      class="flow-table"
      checkbox-color="primary"
      :height="tableSize.height"
      show-select
      fixed-header
      calculate-widths
      hide-default-footer
      v-model="selectedFlows"
      v-resize="onTableResize"
      :header-props="{sortIcon:'mdi-menu-down'}"
      :headers="headers"
      :items="flowList"
      :page.sync="currentPage"
      :items-per-page="pageSize"
      @click:row="selectFlow"
    >

      <template v-slot:item.source="{ item }">

        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on" class="flow-list-item-source">
              <v-chip label small
                v-if="item.status === 'kill'"
                class="flow-list-item-tag"
                color="error"
                text-color="red"
              >kill</v-chip>
              <v-chip label small
                v-else-if="item.response.mock === 'mock'"
                class="flow-list-item-tag"
                color="primaryMost"
                text-color="primary"
              >mock</v-chip>
              <v-chip label small
                v-else-if="item.response.mock === 'proxy'"
                color="border"
                class="flow-list-item-tag"
                text-color="accent"
              >proxy</v-chip>
              <v-chip label small
                v-else
                class="flow-list-item-tag"
                color="border"
                text-color="content"
              >pending</v-chip>
            </span>
          </template>
          <span>{{getSourceTooltipContent(item)}}</span>
        </v-tooltip>

        <v-tooltip bottom v-if="item.proxy_response">
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on" class="flow-list-item-source">
              <v-chip label small
                class="flow-list-item-tag"
                color="#FFF7E2"
                text-color="#D69600"
              >diff</v-chip>
            </span>
          </template>
          <span>Get the server response while the request is mocked</span>
        </v-tooltip>

        <v-tooltip bottom v-if="getRequestEditors(item).length">
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on" class="flow-list-item-source">
              <v-icon x-small color="accent">mdi-wrench</v-icon>
            </span>
          </template>
          <p>Request modification:</p>
          <p v-for="(value, index) in getRequestEditors(item)" :key=index style="line-height:1">{{index + 1}}. {{value.name}}</p>
        </v-tooltip>
      </template>

      <template v-slot:item.method="{ item }">
        <span>{{ item.request.method }}</span>
      </template>

      <template v-slot:item.status="{ item }">
        <span>
          <span v-if="item.response.code >= 400" class="flow-list-status-error">{{ item.response.code }}</span>
          <span v-else>{{ item.response.code }}</span>
        </span>
      </template>

      <template v-slot:item.request="{ item }">
        <span class="flow-list-item-url">
          <span>{{ item.request.scheme }}</span>
          <span v-if="item.request.scheme">://</span>

          <span class="flow-list-item-url-host">{{ item.request.host}}</span>
          <span class="flow-list-item-url-path">{{ item.request.path}}</span>

          <span class="flow-list-item-url-params" v-if="item.request.params">?</span>
          <span class="flow-list-item-url-params">{{ item.request.params }}</span>
        </span>

        <span class="flow-list-item-copy-btn" @click.stop>
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span v-bind="attrs" v-on="on">
                <v-btn icon x-small plain>
                  <v-icon
                    x-small
                    color="accent"
                    v-clipboard:copy="item.request.url"
                    v-clipboard:success="onUrlCopy"
                    v-clipboard:error="onUrlCopyError"
                  >mdi-content-copy</v-icon>
                </v-btn>
              </span>
            </template>
            Copy
          </v-tooltip>

        </span>
      </template>

      <template v-slot:item.start_time="{ item }">
        <span>{{timestampToTime(item.start_time)}}</span>
      </template>

      <template v-slot:item.duration="{ item }">
        <span>{{readablizeDuration(item.duration)}}</span>
      </template>

      <template v-slot:item.size="{ item }">
        <span>{{readablizeBytes(item.size)}}</span>
      </template>

    </v-data-table>

    <v-row class="inspector-tabel-pagination-row">
      <v-spacer></v-spacer>
      <v-col class="inspector-tabel-pagination-col">
        <v-pagination
          v-model="currentPage"
          :length="pageCount"
          @input="refreshFlowList"
          total-visible=7
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { readablizeBytes, timestampToTime } from '@/utils'

export default {
  name: 'flowList',
  components: {
  },
  data () {
    return {
      tableSize: {
        width: 0,
        height: 0,
      },
      flowList: [],
      refreshFlowListTimer: null,
      displayFlowCount: 0,
      pageSize: 50,
      pageCount: 0,
      currentPage: 1,
      headers: [
        {
          text: 'Source',
          value: 'source',
          sortable: false,
          width: 105
        },
        {
          text: 'Method',
          value: 'method',
          sortable: false,
          filterable: false,
          width: 60
        },
        {
          text: 'Status',
          value: 'status',
          sortable: false,
          filterable: false,
          width: 50
        },
        {
          text: 'URL',
          value: 'request',
          sortable: false,
        },
        {
          text: 'Start',
          value: 'start_time',
          filterable: false,
          width: 80
        },
        {
          text: 'Duration',
          value: 'duration',
          filterable: false,
          width: 100
        },
        {
          text: 'Size',
          value: 'size',
          filterable: false,
          width: 80
        }
      ]
    }
  },
  created () {
    this.$io.on('action', this.reload)
  },
  destroyed () {
    this.$io.removeListener('action', this.reload)
  },
  mounted () {
    this.reload()
  },
  computed: {
    originFlowList () {
      return this.$store.state.inspector.originFlowList
    },
    searchStr () {
      return this.$store.state.inspector.searchStr
    },
    selectedFlows: {
      get () {
        return this.$store.state.inspector.selectedFlows
      },
      set (val) {
        this.$store.commit('setSelectedFlows', val)
        this.itemSelectChange(val)
      }
    }
  },
  watch: {
    originFlowList () {
      this.refreshFlowList()
    },
    searchStr (newValue, oldValue) {
      clearTimeout(this.refreshFlowListTimer)
      this.refreshFlowListTimer = setTimeout(() => {
        if (newValue !== oldValue) {
          this.refreshFlowList()
          clearTimeout(this.refreshFlowListTimer)
        }
      }, 500)
    }
  },
  methods: {
    reload () {
      this.$store.dispatch('loadFlowList')
    },
    onTableResize () {
      const height = window.innerHeight - 44 - 40 - 12 - 26 - 7 - 1 - 8 - 12 - 32 - 12 - 12 - 28
      /* reset table height
      Header 44px
      Title 40px
      padding 12px
      buttonbar 26px
      buttombar margin-bottom 7
      divider 1
      margin-top 8px
      tabel
      margin-top 12px
      pagination 32px
      padding 12px
      margin-bottom 12px
      Footer 28px
      */
      this.tableSize = { 
        width: window.innerWidth,
        height: height
      }
    },
    selectFlow (flow) {
      this.$store.dispatch('focusFlow', flow)
    },
    itemSelectChange (event) {
      let selectedIds = []
      for (const row of event) {
        selectedIds.push(row.id)
      }
      this.$store.commit('setSelectedId', selectedIds)
    },
    filterMethod (value, option) {
      return option.toUpperCase().indexOf(value.toUpperCase()) !== -1
    },
    refreshFlowList () {
      let displayFlowList = []
      let searchStr = this.searchStr.trim()
      // Split searchStr by one or more spaces
      let searchStrList = searchStr.split(/\s+/)
      for (const flow of this.originFlowList) {
        let isMatch = true
        for (const searchItem of searchStrList) {
          if (!this.filterMethod(searchItem, flow.request.url)) {
            isMatch = false
            break
          }
        }
        isMatch ? displayFlowList.push(flow) : null
      }
      this.displayFlowCount = displayFlowList.length
      this.pageCount = Math.max(Math.ceil(this.displayFlowCount / this.pageSize), 1)
      this.currentPage = this.pageCount && (this.currentPage > this.pageCount) ? this.pageCount : this.currentPage
      const startIndex = (this.currentPage - 1) * this.pageSize
      const endIndex = startIndex + this.pageSize
      this.flowList = displayFlowList.slice(startIndex, endIndex)
    },
    getRequestEditors (row) {
      let displayRowAction = []
      for (const action of row.action) {
        if (action.id === 'mock') {
          continue
        }
        displayRowAction.push(action)
      }
      return displayRowAction
    },
    readablizeBytes (size) {
      return readablizeBytes(size)
    },
    timestampToTime (timestamp) {
      return timestampToTime(timestamp)
    },
    readablizeDuration (duration) {
      if (duration >= 1) {
        return Math.round(duration * 100 / 100) + 's'
      } else {
        return (duration * 1000).toFixed(0) + 'ms'
      }
    },
    getSourceTooltipContent (row) {
      if (row.status === 'kill') {
        return 'Request is killed by lyrebird'
      } 
      return row.response.mock
    },
    onUrlCopy () {
      this.$bus.$emit('msg.success', 'URL copied!')
    },
    onUrlCopyError (e) {
      this.$bus.$emit('msg.error', 'Copy url error:' + e)
    }
  }
}
</script>

<style lang="css">
.flow-table table > thead > tr > th{
  padding: 0px !important;
  height: 30px !important;
  font-size: 12px !important;
  background-color: #FAF9FA !important;
}
.flow-table table > thead > tr > th > span{
  color: #000520 !important;
}
.flow-table table > thead > tr > th > div > div > i{
  padding-left: 5px;
  font-size: 18px !important;
}
.flow-table table > tbody > tr > td {
  padding: 0px !important;
  height: 36px !important;
  font-size: 12px !important;
}
.flow-table table > tbody > tr > td > div > div > i {
  padding-left: 5px;
  font-size: 18px !important;
}
.flow-table table>tbody>tr>td>span {
  color: #9B9CB7 !important;
}
.flow-list-item-source > span {
  padding: 0px 8px !important;
}
.inspector-tabel-pagination-row {
  margin: 0 !important;
  padding: 0 in !important;
}
.inspector-tabel-pagination-row .v-pagination {
  justify-content: right;
}
.inspector-tabel-pagination-row .v-pagination__navigation {
  margin: 5px !important;
  height: 30px;
  width: 30px;
  box-shadow: none !important;
  background-color: #F9F8FA !important;
}
.inspector-tabel-pagination-row .v-pagination .v-pagination__item {
  margin: 5px !important;
  height: 30px;
  min-width: 30px;
  box-shadow: none !important;
}
.inspector-tabel-pagination-row .v-pagination .v-pagination__item:not(.v-pagination__item--active) {
  margin: 5px !important;
  height: 30px;
  min-width: 30px;
  box-shadow: none !important;
  background-color: #F9F8FA !important;
}
.inspector-tabel-pagination-col {
  padding: 12px 0px 0px;
}
</style>

<style scoped>
.flow-list {
  /* height: calc(100vh - 44px - 40px - 38px - 8px - 28px - 12px); */
  /* total:100vh
  header: 44px
  title: 40px
  buttonBar: 38px
  margin-top: 8px
  table
  margin-bottom: 12px
  footer: 28px
    */
  overflow-y: auto;
}
.flow-list .v-data-table>.v-data-table__wrapper>table {
  width: calc(100% - 20px) !important;
}
.flow-list-item-source {
  text-transform: capitalize;
  padding: 0px;
}
.flow-list-item-tag {
  margin: 0px 2px;
}
.flow-list-status-error {
  color: #F51818;
  font-weight: 400;
}
.flow-list-item-url {
  display: inline-block;
  word-break: keep-all;
  max-width: calc(100% - 50px);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}
.flow-list-item-url-scheme {
  color: unset;
}
.flow-list-item-url-host {
  color: #5F5CCA;
  font-weight: 400;
}
.flow-list-item-url-path {
  color:#318CD7;
  font-weight: 400;
}
.flow-list-item-url-params {
  color: unset;
}
.flow-list-item-copy-btn {
  display: inline-block;
  overflow: hidden;
  cursor: pointer;
}
</style>
