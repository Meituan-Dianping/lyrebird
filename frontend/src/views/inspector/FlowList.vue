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
      ></Table>
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
import { readablizeBytes } from '@/utils'

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
          key: 'src',
          width: 100,
          align: 'center',
          render: (h, params) => {
            const flag = this.getFlowSourceFlagForTable(params.row.response.mock, params.row.response.modified)
            const elements = [
              h("Tag", {
                props: {
                  color: flag.color,
                  size: 'small'
                }
              }, flag.text)
            ]
            if (flag.modified) {
              elements.push(
                h("Tooltip", {
                  props: { content: flag.modifyTag, placement: "top" }
                },
                  [
                    h("Icon", { props: { vif: flag.modified, type: "ios-build" } })
                  ]
                )
              )
            }
            return h("div", elements);
          }
        },
        {
          title: 'Method',
          key: 'method',
          width: 60,
          render: (h, params) => {
            return h("p", {
              style: {
                color: 'green'
              }
            }, params.row.request.method)
          }
        },
        {
          title: 'Status',
          key: 'status',
          width: 50,
          render: (h, params) => {
            let code = params.row.response.code;
            if (code === 200 || (code >= 300 && code <= 399)) {
              return h("p", { style: { color: "green" } }, code);
            } else {
              return h("p", { style: { color: "error" } }, code);
            }
          }
        },
        {
          title: 'URL',
          key: 'request',
          render: (h, params) => {
            return h("span",
              {                style: {
                  wordBreak: "keep-all",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis"
                }              },
              params.row.request.url)
          }
        },
        {
          title: 'Start',
          key: 'start_time',
          width: 60,
          sortable: true,
          render: (h, params) => {
            const startTime = new Date(params.row.start_time * 1000)
            function addZero (i) {
              if (i < 10) {
                i = "0" + i
              }
              return i
            }
            const timeStr = startTime.getHours() + ':'
              + addZero(startTime.getMinutes()) + ':'
              + addZero(startTime.getSeconds())
            return h("span", timeStr)
          }
        },
        {
          title: 'Duration',
          key: 'duration',
          width: 80,
          sortable: true,
          render: (h, params) => {
            const duration = params.row.duration
            if (duration >= 1) {
              return h("span", Math.round(duration * 100 / 100) + "s")
            } else {
              return h("span", (duration * 1000).toFixed(0) + "ms")
            }
          }
        },
        {
          title: 'Size',
          key: 'size',
          sortable: true,
          width: 60,
          render: (h, params) => {
            return h("span", readablizeBytes(params.row.size))
          }
        }
      ],
    };
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
    getFlowSourceFlagForTable: function (mockTag, modifyTag) {
      const flag = {
        text: '',
        color: 'default',
        modified: false,
        modifyTag
      }
      // Handle empty mockTag
      // TODO: remove when upgrade inspector
      if (!mockTag) {
        flag.text = 'pending'
      }
      if (mockTag.startsWith('mock')) {
        flag.text = 'mock'
        flag.color = 'green'
      } else if (mockTag.startsWith('proxy')) {
        flag.text = 'proxy'
      } else {
        flag.text = 'pending'
      }
      flag.modified = modifyTag.length > 0
      return flag
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
</style>
