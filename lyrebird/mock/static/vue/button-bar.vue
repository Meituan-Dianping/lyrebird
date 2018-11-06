<template>
  <card :padding="5">
    <tooltip content="Record http flow" :delay="500">
      <i-button @click="switchRecord">
        <icon :type="recordingBtn.type" :color="recordingBtn.color" />
      </i-button>
    </tooltip>

    <tooltip content="Clear & reload flow list" :delay="500">
      <i-button @click="showClearModal=true" icon="md-refresh"></i-button>
    </tooltip>

    <div class="inline" v-if="showDataButtons">
      <div class="inline">
        <divider type="vertical"></divider>
      </div>

      <tooltip content="Save selected flow" :delay="500">
        <i-button @click="saveSelectedFlow">
          <i class="fa fa-save"></i>
        </i-button>
      </tooltip>

      <tooltip content="Delete selected flow" :delay="500">
        <i-button @click="deleteSelectedFlow" icon="md-trash"></i-button>
      </tooltip>
    </div>

    <div class="inline">
      <divider type="vertical"></divider>
    </div>

    <label>Activated Data:</label>

    <div class="inline">
      <i-select v-model="activatedGroupId" filterable clearable class="data-group">
        <option-group label="DataGroup">
          <i-option v-for="item in dataGroups" :key="item.id" :value="item.id">{{item.name}}</i-option>
        </option-group>
      </i-select>
    </div>

    <div class="inline pull-right">
      <i-input search clearable class="search-box" v-model="searchStr"></i-input>
    </div>

    <modal v-model="showClearModal" title="Alert" @on-ok="clearModalOk" @on-cancel="showClearModal=false">
      <p>Clear flow list?</p>
    </modal>
  </card>
</template>

<script>
  let stopedStatus = {
    recording: false,
    type: "md-radio-button-on",
    color: "red",
    text: "Start recording"
  };

  let recordingStatus = {
    recording: true,
    type: "md-square",
    color: "black",
    text: "Stop recording"
  };

  module.exports = {
    components: {},
    data: function () {
      return {
        showClearModal: false,
        showCreateGroupModal: false,
        newDataGroupName: '',
        recordingBtn: stopedStatus,
        searchStr: ''
      };
    },
    mounted() {
      this.$store.dispatch('loadGroupList')
      this.$store.dispatch('loadActivatedGroup')
      this.getRecordStatus();      
      this.$Notice.config({
        top: 75
      })
    },
    computed: {
      showDataButtons() {
        return this.$store.state.inspector.showDataButtons;
      },
      dataGroups(){
        return this.$store.state.dataManager.groupList
      },
      activatedGroupId:{
        get(){
          return this.$store.state.inspector.activatedGroupId
        },
        set(groupId){
          this.$store.dispatch('activateGroup', groupId)
        }
      }
    },
    watch: {
      searchStr: function(){
        this.$store.commit('search', this.searchStr)
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
            if (response.data.mode === "record") {
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
      saveSelectedFlow: function () {
        if(this.selectedDataGroup === 'None'){
          this.showCreateGroupModal = true;
          return
        }
        this.$http.post('/api/flow',
          {
            ids:this.$store.state.inspector.selectedIds,
            group:this.selectedDataGroup
          }
        )
        .then(resp=>{
          if(resp.data.code===1000){
            this.$Notice.success(
                {
                  title:'Flow saved',
                  desc:resp.data.message
                }
              )
          }else{
            this.$Notice.error(
                {
                  title:'Save flow failed',
                  desc:resp.data,
                  duration:0
                }
              )
          }
          console.log('POST flow', this.$store.state.inspector.selectedIds, resp);
        })
      },
      deleteSelectedFlow: function () {
        this.$http.delete('/api/flow', {body:{ids:this.$store.state.inspector.selectedIds}})
        .then(resp=>{
          console.log('DEL flow', this.$store.state.inspector.selectedIds, resp);
          this.$store.commit('clearSelectedId')
        })
      }
    }
  };
</script>

<style>
  .inline {
    display: inline;
  }
  .data-group {
    width: 15vw;
  }
  .search-box {
    width: 30vw;
  }
</style>