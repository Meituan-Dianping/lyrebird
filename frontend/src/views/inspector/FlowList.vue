<template>
  <div class="flow-list">
    <Table
      highlight-row
      size="small"
      ref="selection"
      :columns="columns"
      :data="flowList"
      @on-row-click="selectFlow"
      @on-selection-change="itemSelectChange"
      class="data-table"
    >
      <template slot-scope="{ row, index }" slot="source">
        <Tooltip class="flow-list-item-source" :content="row.response.mock" :disabled="!row.response.mock" placement="bottom-start" transfer>
          <Tag v-if="row.response.mock === 'mock'" class="flow-list-item-tag" size="small" color="green">mock</Tag>
          <Tag v-else-if="row.response.mock === 'proxy'" class="flow-list-item-tag" size="small">proxy</Tag>
          <Tag v-else size="small" class="flow-list-item-tag">pending</Tag>
        </Tooltip>

        <Tooltip class="flow-list-item-source" v-if="row.proxy_response" content="diff" placement="bottom-start" transfer>
          <Tag size="small" class="flow-list-item-tag" color="blue">diff</Tag>
        </Tooltip>

        <Tooltip class="flow-list-item-source" v-if="getRequestEditors(row).length" placement="bottom-start" transfer>
          <Icon type="md-build" />
          <div slot="content">
            <p>Request modification:</p>
            <p v-for="(value, index) in getRequestEditors(row)">{{index + 1}}. {{value.name}}</p>
          </div>
        </Tooltip>
      </template>

      <template slot-scope="{ row }" slot="method">
        <span style="color:green">{{ row.request.method }}</span>
      </template>

      <template slot-scope="{ row }" slot="status">
        <span v-if="row.response.code === 200" style="color:green">{{ row.response.code }}</span>
        <span v-else-if="row.response.code >= 300 && row.response.code <= 399" style="color:olive">{{ row.response.code }}</span>
        <span v-else style="color:red">{{ row.response.code }}</span>
      </template>

      <template slot-scope="{ row }" slot="request">
        <span class="flow-list-item-url">
          <span class="flow-list-item-url-scheme">{{ row.request.scheme }}</span>
          <span class="flow-list-item-url-scheme" v-if="row.request.scheme">://</span>

          <span class="flow-list-item-url-host">{{ row.request.host}}</span>
          <span class="flow-list-item-url-path">{{ row.request.path}}</span>

          <span class="flow-list-item-url-params" v-if="row.request.params">?</span>
          <span class="flow-list-item-url-params">{{ row.request.params }}</span>
        </span>
        <span class="flow-list-item-copy-btn" @click.stop>
          <Tooltip placement="bottom" content="Copy" :delay="500" transfer>
            <Icon
              type="ios-copy-outline"
              size="16"
              v-clipboard:copy="row.request.url"
              v-clipboard:success="onUrlCopy"
              v-clipboard:error="onUrlCopyError"
            />
          </Tooltip>
        </span>
      </template>

      <template slot-scope="{ row }" slot="start_time">
        <span>{{timestampToTime(row.start_time)}}</span>
      </template>

      <template slot-scope="{ row }" slot="duration">
        <span>{{readablizeDuration(row.duration)}}</span>
      </template>

      <template slot-scope="{ row }" slot="size">
        <span>{{readablizeBytes(row.size)}}</span>
      </template>
    </Table>
    <div style="float: right; margin-top: 5px">
      <Page
        :total="displayFlowCount"
        :page-size="pageSize"
        :current.sync="currentPage"
        @on-change="refreshFlowList"
      />
    </div>
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
      flowList: [],
      refreshFlowListTimer: null,
      foucsFlow: null,
      displayFlowCount: 0,
      pageSize: 50,
      pageCount: 0,
      currentPage: 1,
      columns: [
        {
          type: 'selection',
          width: 30,
          align: 'center'
        },
        {
          title: 'Source',
          slot: 'source',
          width: 100
        },
        {
          title: 'Method',
          slot: 'method',
          width: 60
        },
        {
          title: 'Status',
          slot: 'status',
          width: 50
        },
        {
          title: 'URL',
          slot: 'request'
        },
        {
          title: 'Start',
          slot: 'start_time',
          width: 60,
          sortable: true
        },
        {
          title: 'Duration',
          slot: 'duration',
          width: 80,
          sortable: true
        },
        {
          title: 'Size',
          slot: 'size',
          sortable: true,
          width: 60
        }
      ],
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
    selectedIds () {
      return this.$store.state.inspector.selectedIds
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
          this.refreshFlowList(newValue)
          clearTimeout(this.refreshFlowListTimer)
        }
      }, 500)
    }
  },
  methods: {
    reload () {
      this.$store.dispatch('loadFlowList')
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
      let searchStr = this.$store.state.inspector.searchStr.trim()
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
      this.pageCount = Math.ceil(this.displayFlowCount / this.pageSize)
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
.data-table th div {
  padding-left: 5px;
  padding-right: 5px;
}
.data-table td div {
  padding-left: 2px;
  padding-right: 2px;
}
</style>

<style scoped>
.flow-list {
  height: calc(100vh - 148px);
  /* total:100vh
  header: 38px
  buttonBar: 38px
  divider:1px
  mode-tag:34px
  table
  padding: 9px
  footer: 28px
    */
  overflow-y: auto;
}
.flow-list-item-source {
  padding: 0px;
}
.flow-list-item-tag {
  margin: 0px 2px;
}
.flow-list-item-url {
  display: inline-block;
  word-break: keep-all;
  max-width: calc(100% - 24px);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}
.flow-list-item-url-scheme {
  color: unset;
}
.flow-list-item-url-host {
  color: #3780AF;
  font-weight: 500;
}
.flow-list-item-url-path {
  color:seagreen;
  font-weight: 500;
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
