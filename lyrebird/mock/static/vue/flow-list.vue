<template>
  <card>
    <div style="max-height: 550px; overflow-y: auto;">
      <table class="table">
        <thead>
          <tr>
            <th>
              <input type="checkbox" v-model="selectAll">
            </th>
            <th>Src</th>
            <th>Status</th>
            <th>Host</th>
            <th>Path</th>
          </tr>
        </thead>
        <tbody>
          <tr is="flow-list-item" 
          v-for="flow in flowList" :key="flow.id" 
          :flow="flow" 
          :selected-ids="selectedIds" 
          @click.native="selectFlow(flow)"
          @item-checkbox-change="itemSelectChange"
          :class="rowClass(flow)"
          ></tr>
        </tbody>
      </table>
    </div>
  </card>
</template>

<script>
  module.exports = {
    components: {
      "flow-list-item": httpVueLoader("static/vue/flow-list-item.vue")
    },
    data: function () {
      return {
        flowList: [],
        originFlowList: [],
        selectAll: false,
        foucsFlow: null
      };
    },
    mounted: function () {
      let sio = io();
      reloadFlow = this.reload;
      sio.on("action", function () {
        console.log("Inspector On new action");
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
      selectAll: function () {
        this.$store.commit('clearSelectedId')
        if (this.selectAll) {
          for (const flow of this.flowList) {
            this.$store.commit('addSelectedId', flow.id)
          }
        }
      },
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
        console.log('Item select change', event);
        if (event.selected && this.selectedIds.indexOf(event.id) < 0) {
          this.$store.commit('addSelectedId', event.id)
        } else if (!event.selected && this.selectedIds.indexOf(event.id) >= 0) {
          this.$store.commit('deleteSelectedId', event.id)
        }
      },
      refreshFlowList: function(){
        this.flowList = []
        for (const flow of this.originFlowList) {
          if(flow.request.url.indexOf(this.$store.state.inspector.searchStr)>=0){
            this.flowList.push(flow)
          }
        }
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
.foucs{
  background-color: rgb(217, 239, 252)
}
</style>