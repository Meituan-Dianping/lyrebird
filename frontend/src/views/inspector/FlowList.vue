<template>
  <Card> 
    <div class="flow-list">
      <Table highlight-row 
        size='small'
        ref="selection" 
        :columns="columns" 
        :data="flowList"
        @on-row-click="selectFlow" 
        @on-selection-change="itemSelectChange" 
        class="data-table"
      >
      </Table>
      <div style="float: right; margin-top: 5px">
        <Page :total="originFlowList.length" :page-size="pageSize" :current.sync="currentPage" @on-change="refreshFlowList"/>
      </div>
    </div>
  </Card>
</template>

<script>
  import FlowListItem from '@/views/inspector/FlowListItem.vue'
  import io from 'socket.io-client'
  import {readablizeBytes} from '@/utils'

  export default {
    name: 'flowList',
    components: {
      FlowListItem
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
            width: 75,
            align: 'center',
            render: (h, params) => {
              if (params.row.response.mock === 'proxy') {
                return h("Tag", {
                  props: {
                    color: 'default',
                    size: 'small'
                  }
                }, params.row.response.mock);
              } else if (params.row.response.mock === 'mock') {
                return h("Tag", {
                  props: {
                    color: 'green',
                    size: 'small'
                  }
                }, params.row.response.mock);
              } else {
                return h("Tag", {
                  props: {
                    color: 'default',
                    size: 'small'
                  }
                }, 'pending');
              }
            }
          },
          {
            title: 'Status',
            key: 'status',
            width: 50,
            render: (h, params) => {
              let code = params.row.response.code;
              if (code === 200 || (code >= 300 && code <= 399)) {
                return h("p", { style: { color: "green" } },code);
              } else {
                return h("p", { style: { color: "error" } },code);
              }
            }
          },
          {
            title: 'URL',
            key: 'request',
            render: (h, params) => {
              return h("span", 
              {style: {
                wordBreak:"keep-all",
                whiteSpace:"nowrap",
                overflow:"hidden",
                textOverflow:"ellipsis"
              }}, 
              params.row.request.url)
            }
          },
          {
            title: 'Size',
            key: 'size',
            width: 60,
            render: (h, params) => {
              return h("span", readablizeBytes(params.row.size))
            }
          },
          {
            title: 'Duration',
            key: 'duration',
            width: 60,
            render:(h,params) => {
              const duration = params.row.duration
              if(duration>=1){
                return h("span", Math.round(duration*100/100)+"s")
              }else{
                return h("span", (duration*1000).toFixed(0)+"ms")
              }
            }
          }
        ],
      };
    },
    created() {
      const reload = this.reload
      this.sio = this.$io
      this.sio.on("action", function(){
        reload()
      })
    },
    mounted: function () {
      this.reload();
    },
    computed: {
      searchStr: function(){
        return this.$store.state.inspector.searchStr
      },
      selectedIds: function(){
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
      originFlowList: function(){
        this.refreshFlowList()
      },
      searchStr: function(){
        this.refreshFlowList()
      }
    },
    methods: {
      reload: function () {
        this.$http.get("/api/flow").then(
          response => {
            this.originFlowList = response.data;
          },
          error => {
            console.log("Inspector: reload failed", error);
          }
        );
      },
      selectFlow: function (flow) {
        this.foucsFlow = flow
        this.$emit("select-detail", flow);
      },
      itemSelectChange: function (event) {
        let selectedIds = []
        for (const row of event) {
          selectedIds.push(row.id)
        }
        this.$store.commit('setSelectedId', selectedIds)
      },
      refreshFlowList: function(){
        let flowList = []
        for (const flow of this.originFlowList) {
          if(flow.request.url.indexOf(this.$store.state.inspector.searchStr)>=0){
            flowList.push(flow)
          }
        }
        this.pageCount = Math.ceil(flowList.length/this.pageSize)
        const startIndex = (this.currentPage-1)*this.pageSize
        const endIndex = startIndex + this.pageSize
        this.flowList = flowList.slice(startIndex, endIndex)
      },
      rowClass: function(flow){
        if(flow && this.foucsFlow){
          return { foucs: flow.id === this.foucsFlow.id}
        }else{
          return { foucs: false }
        }
      }
    }
  };
</script>

<style>
.flow-list {
  height: calc(100vh - 166px);
  /* total:100vh
  header: 38px
  padding: 5px + 5px
  buttonBar: 48px
  card-padding: 16px
  table
  card-padding: 16px
  padding: 5px
  footer: 28px
    */
  overflow-y: auto;
}
.data-table th div{
padding-left: 5px;
padding-right: 5px;
}
.data-table td div{
padding-left: 5px;
padding-right: 5px;
}
</style>
