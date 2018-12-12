<template>
  <Card :padding="5">
    <Tooltip content="Record http flow" :delay="500">
      <Button @click="switchRecord">
        <Icon :type="recordingBtn.type" :color="recordingBtn.color" />
      </Button>
    </Tooltip>

    <Tooltip content="Clear & reload flow list" :delay="500">
      <Button @click="showClearModal=true" icon="md-refresh"></Button>
    </Tooltip>

    <div class="inline" v-if="showDataButtons">
      <div class="inline">
        <Divider type="vertical"></Divider>
      </div>

      <Tooltip content="Save selected flow" :delay="500">
        <Button @click="saveSelectedFlow">
          <Icon type="md-archive"></Icon>
        </Button>
      </Tooltip>

      <Tooltip content="Delete selected flow" :delay="500">
        <Button @click="deleteSelectedFlow" icon="md-trash"></Button>
      </Tooltip>
    </div>

    <div class="inline">
      <Divider type="vertical"></Divider>
    </div>

    <label>Activated Data:</label>

    <div class="inline">
      <Select v-model="activatedGroupId" filterable clearable style="width: 15vw">
        <OptionGroup label="DataGroup">
          <Option v-for="item in dataGroups" :key="item.id" :value="item.id">{{item.name}}</Option>
        </OptionGroup>
      </Select>
    </div>

    <div class="inline" style="float:right">
      <Input search clearable style="width:30vw" v-model="searchStr"></Input>
    </div>

    <Modal v-model="showClearModal" title="Alert" @on-ok="clearModalOk" @on-cancel="showClearModal=false">
      <p>Clear flow list?</p>
    </Modal>
  </Card>
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

 export default {
    name: 'buttonBar',
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
</style>