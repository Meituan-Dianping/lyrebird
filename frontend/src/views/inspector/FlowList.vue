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
      :headers="headers"
      :items="flowList"
      :search="searchStr"
      :page.sync="currentPage"
      :items-per-page="pageSize"
      @click:row="selectFlow"
      @page-count="pageCount = $event"
    >
      <template
        v-slot:header.data-table-select="{ on, props }"
      >
        <v-simple-checkbox
          color="purple"
          v-bind="props"
          v-on="on"
        ></v-simple-checkbox>
      </template>

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
        <span v-if="item.response.code === 200">{{ item.response.code }}</span>
        <span v-else-if="item.response.code >= 300 && item.response.code <= 399" style="color:olive">{{ item.response.code }}</span>
        <span v-else style="color:red">{{ item.response.code }}</span>
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

                <v-btn
                  icon
                  x-small
                  plain
                >
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

    <v-row class="tabel-pagination">
      <v-spacer></v-spacer>
      <v-col>
        <v-pagination
        v-model="currentPage"
        :length="pageCount"
        @input="refreshFlowList"
        total-visible=7
      ></v-pagination>
      </v-col>
    </v-row>

    
    
    <!-- <Table
      highlight-row
      size="small"
      ref="selection"
      :columns="columns"
      :data="flowList"
      @on-row-click="selectFlow"
      @on-selection-change="itemSelectChange"
      class="data-table"
    >
      <template slot-scope="{ row }" slot="source">
        <Tooltip class="flow-list-item-source" :content="getSourceTooltipContent(row)" placement="bottom-start" transfer>
          <Tag v-if="row.status === 'kill'" class="flow-list-item-tag" size="small" color="red">kill</Tag>
          <Tag v-else-if="row.response.mock === 'mock'" class="flow-list-item-tag" size="small" color="green">mock</Tag>
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
            <p v-for="(value, index) in getRequestEditors(row)" :key=index>{{index + 1}}. {{value.name}}</p>
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
     -->
    <!-- 
    <div style="float: right; margin-top: 5px">
      <Page
        :total="displayFlowCount"
        :page-size="pageSize"
        :current.sync="currentPage"
        @on-change="refreshFlowList"
      />
    </div> -->
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
      pageSize: 20,
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
      ],
      columns: [
        {
          type: 'selection',
          width: 30,
          align: 'center'
        },
        {
          title: 'Source',
          slot: 'source',
          width: 105
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
      const height = window.innerHeight - 44 - 40 - 38 - 12 - 28 - 68
      /* reset table height
      Header 44px
      Title 40px
      buttonbar 38px
      tabel
      Margin Bottom: 12px
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
      this.pageCount = Math.ceil(this.displayFlowCount / this.pageSize) // todo
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
.flow-table table>thead>tr>th{
  padding: 0px !important;
  height: 30px !important;
  font-size: 12px !important;
  background-color: #FAF9FA !important;
  /* padding-left: 5px !important;
  padding-right: 5px !important; */
}
.flow-table table>thead>tr>th>span{
  color: #000520 !important;
  /* padding-left: 5px !important;
  padding-right: 5px !important; */
}
.flow-table table>tbody>tr>td {
  padding: 0px !important;
  height: 36px !important;
  font-size: 12px !important;
  /* padding-left: 2px !important;
  padding-right: 2px !important; */
}
.flow-table table>tbody>tr>td>span {
  color: #9B9CB7 !important;
  /* padding-left: 2px !important;
  padding-right: 2px !important; */
}
.flow-list-item-source > span {
  padding: 0px 8px !important;
}
.flow-list .v-data-table-header{
  /* position: absolute !important;  */ 
  /* z-index not work without position: absolute */
  z-index: 0 !important;
}
.tabel-pagination .v-pagination {
  justify-content: right;
}
</style>

<style scoped>
.flow-list {
  height: calc(100vh - 44px - 40px - 38px - 28px - 12px);
  /* total:100vh
  header: 44px
  title: 40px
  buttonBar: 38px
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
  font-weight: 500;
}
.flow-list-item-url-path {
  color:#318CD7;
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
.tabel-pagination {
  margin: 0px;
}
</style>
