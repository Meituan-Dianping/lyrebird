<template>
    <div>
        <div class="box box-solid">
            <div class="box-body">
                <button-group>
                    <tooltip placement="top" content="Record http flow" :delay="1000">                    
                    <i-button @click="switchRecord"><icon :type="recordingBtn.type" :color="recordingBtn.color"/></i-button>
                    </tooltip>
                    <tooltip placement="top" content="Clear flow list" :delay="1000">                    
                    <i-button @click="showClearModal=true"><icon type="trash-a" color="orange"/></i-button>
                    </tooltip>
                    <modal v-model="showClearModal"
                    title="Alert"
                    @on-ok="clearModalOk"
                    @on-cancel="showClearModal=false">
                    <p>Clear flow list?</p>
                    </modal>
                </button-group>
                <button-group style="margin-left: 50px">
                    <tooltip placement="top" content="Create new data group" :delay="1000">
                    <i-button @click="showCreateGroupModal=true"><icon type="plus" color="green"/></i-button>
                    </tooltip>
                    <modal
                    v-model="showCreateGroupModal"
                    title="Dialog"
                    @on-ok="creatGroupModalOk"
                    >
                        <label>Create new data group</label>
                        <i-input placeholder="GroupName" v-model="newDataGroupName">
                    </modal>
                </button-group>
                <button-group>
                    <tooltip placement="top" content="Activate selected data group" :delay="1000">                    
                    <i-select v-model="selectedDataGroup" filterable clearable @on-change="activatedDataChange">
                        <i-option v-for="item in dataGroups" :key="item" :value="item">{{item}}</i-option>
                    </i-select>
                    </tooltip>
                </button-group>
                <button-group>
                    <tooltip placement="top" content="Deactivate data group" :delay="1000">                    
                    <i-button @click="resetActivatedData"><Icon type="backspace" color="red"></Icon></i-button>                   
                    </tooltip>
                </button-group>
            </div>
        </div>

        <div class="row">
            <div class="col-md-6">
                <flow-list v-on:select-detail="selectedFlowChange"></flow-list>
            </div>
            <div class="col-md-6">
                <flow-detail v-bind:flow="selectedFlow"></flow-detail>
            </div>
        </div>
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

module.exports = {
  data: function() {
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
    "flow-list": httpVueLoader("static/vue/flow-list.vue"),
    "flow-detail": httpVueLoader("static/vue/flow-detail.vue")
  },
  mounted: function() {
    this.getRecordStatus();
    this.updateDataGroups();
    this.updateActivatedDataGroup();
  },
  methods: {
    selectedFlowChange: function(payload) {
      this.selectedFlow = payload;
      console.log("on selectedFlowChange", payload);
    },
    switchRecord: function() {
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
    getRecordStatus: function() {
      this.$http.get("/api/mode").then(
        response => {
            if(response.data.mode==='record'){
                this.recordingBtn = recordingStatus;
            }else{
                this.recordingBtn = stopedStatus;
            }
            console.log("get recode mode", response);
        },
        error => {}
      );
    },
    clearModalOk: function() {
      this.$http.delete("/api/flow").then(response => {});
      this.selectedFlow = null;
    },
    activateData: function(name) {
      if(name==='None'){
        this.resetActivatedData();
      }else{
        this.$http.put("/api/mock/" + name + "/activate").then(
          response => {
            console.log("activated group", name);
            this.updateActivatedDataGroup();
          },
          errpr => {}
        );
      }
    },
    resetActivatedData: function() {
      this.$http.put("/api/mock/group/deactivate").then(
        response => {
          console.log("reset group");
          this.updateActivatedDataGroup();
        },
        errpr => {}
      );
    },
    filterMethod: function(value, option) {
      return option.toUpperCase().indexOf(value.toUpperCase()) !== -1;
    },
    updateDataGroups: function() {
      this.$http.get("/api/mock").then(response => {
        this.dataGroups = response.data;
        this.dataGroups.push("None");
      });
    },
    updateActivatedDataGroup: function() {
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
    activatedDataChange: function(val) {
      console.log("Change", val);
      this.updateDataGroups();
      this.activateData(val);
    },
    creatGroupModalOk: function() {
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
</style>