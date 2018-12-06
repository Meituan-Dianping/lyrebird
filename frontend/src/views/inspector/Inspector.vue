<template>
  <div>
    <Row class="button-bar">
      <button-bar></button-bar>
    </Row>
    <Row>
      <Col span="12">
        <flow-list v-on:select-detail="selectedFlowChange" class="inspector-left"></flow-list>
      </Col>
      <Col span="12">
        <flow-detail v-bind:flow="selectedFlow" class="inspector-right"></flow-detail>
      </Col>
    </Row>
  </div>
</template>

<script>
  let stopedStatus = {
    recording: false,
    type: "record",
    color: "red",
    text: "Start recording"
  };
  let recordingStatus = {
    recording: true,
    type: "stop",
    color: "black",
    text: "Stop recording"
  };
  import FlowList from '@/views/inspector/FlowList.vue'
  import FlowDetail from '@/views/inspector/FlowDetail.vue'
  import ButtonBar from '@/views/inspector/ButtonBar.vue'

  export default {
    name: 'Inspector',
    data: function () {
      return {
        showClearModal: false,
        selectedFlow: null,
        recordingBtn: stopedStatus,
        activatedData: null,
        selectedDataGroup: "",
        dataGroups: ["None"],
        newDataGroupName: "",
        showCreateGroupModal: false
      };
    },
    components: {
      FlowList,
      FlowDetail,
      ButtonBar,
    },
    mounted: function () {
      this.getRecordStatus();
      this.updateDataGroups();
      this.updateActivatedDataGroup();
    },
    methods: {
      selectedFlowChange: function (payload) {
        this.selectedFlow = payload;
      },
      switchRecord: function () {
        if (this.recordingBtn.recording) {
          this.$http.put("/api/mode/normal").then(
            response => {
              this.recordingBtn = stopedStatus;
              console.log("stop recording", response);
            },
            error => {
              console.log("stop recording failed", response);
            }
          );
        } else {
          if (this.selectedDataGroup === "None") {
            this.showCreateGroupModal = true;
          }
          this.$http.put("/api/mode/record").then(
            response => {
              this.recordingBtn = recordingStatus;
              console.log("start recode", response);
            },
            error => {
              console.log("start recode failed", error);
            }
          );
        }
      },
      getRecordStatus: function () {
        this.$http.get("/api/mode").then(
          response => {
            if (response.data.mode === 'record') {
              this.recordingBtn = recordingStatus;
            } else {
              this.recordingBtn = stopedStatus;
            }
            console.log("get recode mode", response);
          },
          error => {}
        );
      },
      clearModalOk: function () {
        this.$http.delete("/api/flow").then(response => {});
        this.selectedFlow = null;
      },
      activateData: function (name) {
        if (name === 'None') {
          this.resetActivatedData();
        } else {
          this.$http.put("/api/mock/" + name + "/activate").then(
            response => {
              console.log("activated group", name);
              this.updateActivatedDataGroup();
            },
            errpr => {}
          );
        }
      },
      resetActivatedData: function () {
        this.$http.put("/api/mock/group/deactivate").then(
          response => {
            console.log("reset group");
            this.updateActivatedDataGroup();
          },
          errpr => {}
        );
      },
      filterMethod: function (value, option) {
        return option.toUpperCase().indexOf(value.toUpperCase()) !== -1;
      },
      updateDataGroups: function () {
        this.$http.get("/api/mock").then(response => {
          this.dataGroups = response.data;
          this.dataGroups.push("None");
        });
      },
      updateActivatedDataGroup: function () {
        this.$http.get("/api/mock/activated").then(
          response => {
            if (response.data.name) {
              this.selectedDataGroup = response.data.name;
            } else {
              this.selectedDataGroup = "None";
            }
            console.log("activated group", response);
          },
          error => {}
        );
      },
      activatedDataChange: function (val) {
        console.log("Change", val);
        this.updateDataGroups();
        this.activateData(val);
      },
      creatGroupModalOk: function () {
        let data = new FormData();
        data.append("name", this.newDataGroupName);
        data.append("data", '{"parent": null, "filters": []}');
        data.append("origin_name", "");

        let name = this.newDataGroupName;

        this.$http.post("/api/mock", data).then(
          response => {
            console.log("Create data group success");
            this.updateDataGroups();
            this.activateData(name);
            this.newDataGroupName = null;
          },
          error => {
            this.newDataGroupName = null;
          }
        );
      }
    }
  };
</script>

<style>
  .button-bar {
    margin-bottom: 5px;
    height: 48px;
  }

  .inspector-left {
    margin-right: 5px
  }

  .inspector-right {
    margin-left: 5px
  }
</style>