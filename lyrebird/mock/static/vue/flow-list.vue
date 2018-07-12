<template>
    <div class="box box-solid">
        <div class="box-body">
            <div style="max-height: 550px; overflow-y: auto;">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>src</th>
                        <th>status</th>
                        <th>host</th>
                        <th>path</th>
                    </tr>
                </thead>
                <tbody>
                    <tr is="flow-list-item" v-for="flow in flowList" :key="flow.id" :flow="flow" @click.native="selectFlow(flow)"></tr>
                </tbody>
            </table>
            </div>
        </div>
    </div>
</template>

<script>
module.exports = {
  components: {
    "flow-list-item": httpVueLoader("static/vue/flow-list-item.vue")
  },
  data: function() {
    return {
      flowList: []
    };
  },
  mounted: function() {
    let sio = io();
    reloadFlow = this.reload;
    sio.on("action", function() {
      console.log("Inspector On new action");
      reloadFlow();
    });
    this.reload();
  },
  methods: {
    reload: function() {
      this.$http.get("/api/flow").then(
        response => {
          this.flowList = response.data;
        },
        error => {
          console.log("Inspector: reload failed", error);
        }
      );
    },
    selectFlow: function(flow) {
      console.log("FlowList: select flow", flow);
      this.$emit("select-detail", flow);
    }
  }
};
</script>

<style>
</style>