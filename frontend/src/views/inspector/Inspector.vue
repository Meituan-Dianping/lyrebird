<template>
  <div>
    <Row class="inspector-container-button-bar">
      <button-bar></button-bar>
    </Row>
    <div class="divider"></div>
    <Row>
      <Col :span="listSpan">
        <flow-list class="inspector-left"></flow-list>
      </Col>
      <div class="split" v-if="focusedFlow"></div>
      <Col span="12" v-if="focusedFlow">
        <flow-detail class="inspector-right"></flow-detail>
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
  computed: {
    listSpan () {
      if (this.focusedFlow) {
        return "12"
      } else {
        return "24"
      }
    },
    focusedFlow () {
      return this.$store.state.inspector.focusedFlow
    }
  },
  methods: {
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
        },
        error => { }
      );
    },
    clearModalOk: function () {
      this.$http.delete("/api/flow").then(response => {
        this.$store.commit('setFocusedFlow', null)
      });
    },
    activateData: function (name) {
      if (name === 'None') {
        this.resetActivatedData();
      } else {
        this.$http.put("/api/mock/" + name + "/activate").then(
          response => {
            this.updateActivatedDataGroup();
          },
          errpr => { }
        );
      }
    },
    resetActivatedData: function () {
      this.$http.put("/api/mock/group/deactivate").then(
        response => {
          this.updateActivatedDataGroup();
        },
        errpr => { }
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
        },
        error => { }
      );
    },
    activatedDataChange: function (val) {
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

<style scoped>
.inspector-container-button-bar {
  height: 38px;
  display: flex;
  align-items: center;
}
.inspector-left {
  margin-right: 0px;
}
.inspector-right {
  margin-left: 5px;
}
.divider {
  display: block;
  width: 100%;
  height: 1px;
  background: #eee;
  top: 0;
  left: 0;
}
.split {
  display: block;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  border: 1px dashed #eee;
}
</style>
