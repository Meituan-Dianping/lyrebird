<template>
  <div>
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
          <Tooltip class="flow-list-item-source" :content="row.response.mock" placement="top" transfer>
            <Tag v-if="row.response.mock === 'mock'" class="flow-list-item-tag" size="small" color="green">mock</Tag>
            <Tag v-else-if="row.response.mock === 'proxy'" class="flow-list-item-tag" size="small">proxy</Tag>
            <Tag v-else size="small" class="flow-list-item-tag">pending</Tag>
          </Tooltip>

          <Tooltip class="flow-list-item-source" v-if="row.proxy_response" content="diff" placement="top" transfer>
            <Tag size="small" class="flow-list-item-tag" color="blue">diff</Tag>
          </Tooltip>

          <Tooltip class="flow-list-item-source" v-if="row.response.modified" content="modified" placement="top" transfer>
            <Icon type="md-build" />
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
          <span class="flow-list-item-url">{{ row.request.url }}</span>
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
          :total="originFlowList.length"
          :page-size="pageSize"
          :current.sync="currentPage"
          @on-change="refreshFlowList"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { readablizeBytes, timestampToTime } from '@/utils'

export default {
  name: 'flowList',
  components: {
  },
  data: function () {
    return {
      flowList: [],
      originFlowList: [],
      foucsFlow: null,
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
    this.$io.on("action", this.reload)
  },
  destroyed () {
    this.$io.removeListener('action', this.reload)
  },
  mounted: function () {
    this.reload();
  },
  computed: {
    searchStr: function () {
      return this.$store.state.inspector.searchStr
    },
    selectedIds: function () {
      return this.$store.state.inspector.selectedIds
    }
  },
  watch: {
    selectedIds: function () {
      if (this.selectedIds.length > 0) {
        this.$store.commit('showDataButtons', true)
      } else {
        this.$store.commit('showDataButtons', false)
      }
    },
    originFlowList: function () {
      this.refreshFlowList()
    },
    searchStr: function () {
      this.refreshFlowList()
    }
  },
  methods: {
    reload: function () {
      this.$http.get("/api/flow").then(
        response => {
          this.originFlowList = []
          const selectedIds = this.$store.state.inspector.selectedIds
          for (const flow of response.data) {
            if (selectedIds.includes(flow.id))
              flow['_checked'] = true
            this.originFlowList.push(flow)
          }
        },
        error => {
          console.log("Inspector: reload failed", error);
        }
      );
    },
    selectFlow: function (flow) {
      this.$store.dispatch('focusFlow', flow)
    },
    itemSelectChange: function (event) {
      let selectedIds = []
      for (const row of event) {
        selectedIds.push(row.id)
      }
      this.$store.commit('setSelectedId', selectedIds)
    },
    refreshFlowList: function () {
      let flowList = []
      for (const flow of this.originFlowList) {
        if (flow.request.url.indexOf(this.$store.state.inspector.searchStr) >= 0) {
          flowList.push(flow)
        }
      }
      this.pageCount = Math.ceil(flowList.length / this.pageSize)
      const startIndex = (this.currentPage - 1) * this.pageSize
      const endIndex = startIndex + this.pageSize
      this.flowList = flowList.slice(startIndex, endIndex)
    },
    rowClass: function (flow) {
      if (flow && this.foucsFlow) {
        return { foucs: flow.id === this.foucsFlow.id }
      } else {
        return { foucs: false }
      }
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
    }
  }
};
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
  table
  padding: 5px
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
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
