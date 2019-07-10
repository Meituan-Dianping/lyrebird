<template>
  <div class="inspector-button-bar">
    <Tooltip :content="recordBtnTooltip" placement="bottom-start" :delay="500">
      <Button class="inspector-button" @click="switchRecord">
        <Icon :type="recordingBtn.type" :color="recordingBtn.color" />
      </Button>
    </Tooltip>
    <div class="inline">
      <Divider type="vertical"></Divider>
    </div>
    <Tooltip content="Clear" :delay="500">
      <Button class="inspector-button" @click="showClearModal=true" icon="ios-trash"></Button>
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

    <label>
      <b style="padding-right:5px">Activated Mock Group:</b>
      <ButtonGroup>
        <Button @click="showMockDataSelector" size="small">{{activateBtnText}}</Button>
        <Button size="small" @click="resetActivatedData">
          <Icon type="ios-backspace-outline" color="red" />
        </Button>
      </ButtonGroup>
    </label>

    <div class="inline inspector-searchbox">
      <Input search clearable size="small" v-model="searchStr"></Input>
    </div>

    <Modal
      v-model="showClearModal"
      title="Alert"
      @on-ok="clearModalOk"
      @on-cancel="showClearModal=false"
    >
      <p>Clear flow list?</p>
    </Modal>

    <Modal
      v-model="showCreateGroupModal"
      title="Create mock group"
      @on-ok="createAndActivateGroupOk"
    >
      <Input v-model="newDataGroupName" placeholder="Data group name"></Input>
    </Modal>

    <MockDataSelector ref="dataSelector"></MockDataSelector>
  </div>
</template>

<script>
import MockDataSelector from '@/views/inspector/MockDataSelector.vue'

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
  components: {
    MockDataSelector
  },
  data: function () {
    return {
      showClearModal: false,
      showCreateGroupModal: false,
      newDataGroupName: '',
      recordingBtn: stopedStatus
    };
  },
  mounted () {
    this.$store.dispatch('iLoadGroupList')
    this.$store.dispatch('loadActivatedGroup')
    this.getRecordStatus();
  },
  computed: {
    showDataButtons () {
      return this.$store.state.inspector.showDataButtons;
    },
    dataGroups () {
      return this.$store.state.inspector.groupList
    },
    activatedGroups () {
      return this.$store.state.inspector.activatedGroup
    },
    activateBtnText () {
      const activatedGroups = this.$store.state.inspector.activatedGroup
      if (activatedGroups === null) {
        return 'None'
      }
      if (Object.keys(activatedGroups).length === 0) {
        return 'None'
      }
      let text = ''
      for (const groupId in activatedGroups) {
        text = text + activatedGroups[groupId].name
      }
      return text
    },
    searchStr: {
      get () {
        return this.$store.state.inspector.searchStr
      },
      set (val) {
        this.$store.commit('search', val)
      }
    },
    recordBtnTooltip () {
      if (this.recordingBtn.recording) {
        return 'Stop recording'
      } else {
        return 'Record'
      }
    }
  },
  methods: {
    showMockDataSelector () {
      this.$refs.dataSelector.toggal()
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
        error => { }
      );
    },
    clearModalOk: function () {
      this.$http.delete('/api/flow', { body: { ids: null } }).then(response => {
      });

      this.selectedFlow = null;
    },
    resetActivatedData: function () {
      this.$store.dispatch('deactivateGroup')
    },
    filterMethod: function (value, option) {
      return option.toUpperCase().indexOf(value.toUpperCase()) !== -1;
    },
    saveSelectedFlow: function () {
      if (!this.activatedGroupId) {
        this.showCreateGroupModal = true;
        return
      }
      this.$http.post('/api/flow',
        {
          ids: this.$store.state.inspector.selectedIds,
          group: this.activatedGroupId
        }
      )
        .then(resp => {
          if (resp.data.code === 1000) {
            this.$Notice.success(
              {
                title: 'Flow saved',
                desc: resp.data.message
              }
            )
          } else {
            this.$Notice.error(
              {
                title: 'Save flow failed',
                desc: resp.data.message,
                duration: 0
              }
            )
          }
          console.log('POST flow', this.$store.state.inspector.selectedIds, resp);
        })
    },
    deleteSelectedFlow: function () {
      this.$http.delete('/api/flow', { body: { ids: this.$store.state.inspector.selectedIds } })
        .then(resp => {
          console.log('DEL flow', this.$store.state.inspector.selectedIds, resp);
          this.$store.commit('clearSelectedId')
        })
    },
    createAndActivateGroupOk () {
      this.$store.dispatch('createAndActivateGroup', this.newDataGroupName)
    }
  }
};
</script>

<style>
.inline {
  display: inline;
}
.inspector-button-bar {
  flex-grow: 1;
}
.inspector-button {
  padding: 1px 6px 1px !important;
  font-size: 14px !important;
}
.inspector-searchbox {
  width: 30vw;
  float: right;
}
</style>

