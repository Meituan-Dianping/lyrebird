<template>
  <div class="button-bar">
    <Tooltip :content="recordBtnTooltip" placement="bottom-start" :delay="500">
      <Button @click="switchRecord">
        <Icon :type="recordingBtn.type" :color="recordingBtn.color" />
      </Button>
    </Tooltip>
    <div class="inline">
      <Divider type="vertical"></Divider>
    </div>
    <Tooltip content="Clear" :delay="500">
      <Button @click="showClearModal=true" icon="md-refresh"></Button>
    </Tooltip>

    <div class="inline" v-if="showDataButtons">
      <div class="inline">
        <Divider type="vertical"></Divider>
      </div>

      <Tooltip content="Save" :delay="500">
        <Button @click="saveSelectedFlow">
          <Icon type="md-archive"></Icon>
        </Button>
      </Tooltip>

      <Tooltip content="Delete" :delay="500">
        <Button @click="deleteSelectedFlow" icon="md-trash"></Button>
      </Tooltip>
    </div>

    <div class="inline">
      <Divider type="vertical"></Divider>
    </div>

    <label style="padding-right:5px"><b>Activated Data:</b></label>

    <div class="inline">
      <Select v-model="activatedGroupId" filterable clearable style="width: 15vw">
        <OptionGroup label="DataGroup">
          <Option v-for="item in dataGroups" :key="item.id" :value="item.id">{{item.name}}</Option>
        </OptionGroup>
      </Select>
    </div>

    <div class="inline" style="margin-left:auto">
      <Input search clearable style="width:30vw" v-model="searchStr"></Input>
    </div>

    <Modal v-model="showClearModal" title="Alert" @on-ok="clearModalOk" @on-cancel="showClearModal=false">
      <p>Clear flow list?</p>
    </Modal>

    <Modal v-model="showCreateGroupModal" title="Create mock group" @on-ok="createAndActivateGroupOk">
      <Input v-model="newDataGroupName" placeholder="Data group name"></Input>
    </Modal>
  </div>
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
        recordingBtn: stopedStatus
      };
    },
    mounted() {
      this.$store.dispatch('iLoadGroupList')
      this.$store.dispatch('loadActivatedGroup')
      this.getRecordStatus(); 
    },
    computed: {
      showDataButtons() {
        return this.$store.state.inspector.showDataButtons;
      },
      dataGroups(){
        return this.$store.state.inspector.groupList
      },
      activatedGroupId:{
        get(){
          return this.$store.state.inspector.activatedGroupId
        },
        set(groupId){
          if(groupId){
            this.$store.dispatch('activateGroup', groupId)
          }else{
            this.$store.dispatch('deactivateGroup')
          }
        }
      },
      searchStr:{
        get(){
          return this.$store.state.inspector.searchStr
        },
        set(val){
          this.$store.commit('search', val)
        }
      },
      recordBtnTooltip(){
        if(this.recordingBtn.recording){
          return 'Stop recording'
        }else{
          return 'Record'
        }
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
          if (!this.activatedGroupId) {
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
        this.$http.delete('/api/flow', {body: {ids:null}}).then(response => {
        });

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
        if(!this.activatedGroupId){
          this.showCreateGroupModal = true;
          return
        }
        this.$http.post('/api/flow',
          {
            ids:this.$store.state.inspector.selectedIds,
            group:this.activatedGroupId
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
                  desc:resp.data.message,
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
      },
      createAndActivateGroupOk(){
        this.$store.dispatch('createAndActivateGroup', this.newDataGroupName)
      }
    }
  };
</script>

<style scoped>
  .inline {
    display: inline;
  }
  .button-bar {
    flex-grow: 1
  }
</style>