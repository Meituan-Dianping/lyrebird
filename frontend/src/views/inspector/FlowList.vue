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
                width: 50,
            align: 'center'
          },
          {
            title: 'Src',
            key: 'src',
            width: 100,
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
              }
            }
          },
          {
            title: 'Status',
            key: 'status',
            width: 80,
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
            title: 'Host',
            key: 'request',
            render: (h, params) => {
              return h("span", params.row.request.host)
            }
          },
          {
            title: 'Path',
            render:(h, params) => {
              return h("b", params.row.request.path)
            }
          },
          {
            title: 'Time',
            key: 'time',
            width: 60
          }
        ],
      };
    },
    mounted: function () {
      let sio = io();
      const reloadFlow = this.reload;
      sio.on("action", function () {
        reloadFlow();
      });
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
        this.$store.commit('setSelectedId', event)
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
