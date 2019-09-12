<template>
  <div class="inspector-button-bar">
    <Tooltip :content="recordBtnTooltip" placement="bottom-start" :delay="500">
      <Icon
        class="inspector-button"
        :type="recordingBtn.type"
        :color="recordingBtn.color"
        @click="switchRecord"
        style="margin-right:3px"
        size="18"
      />
    </Tooltip>

    <Tooltip content="Clear" :delay="500">
      <div class="inspector-button ivu-icon" @click="showClearModal=true">
        <svg-icon class="ivu-icon" name="short-broom" color="#666" scale="5"></svg-icon>
      </div>
    </Tooltip>

    <div class="inline" v-if="showDataButtons">
      <div class="inline">
        <Divider type="vertical"></Divider>
      </div>

      <Tooltip content="Save" :delay="500">
        <div class="inspector-button ivu-icon" @click="saveSelectedFlow">
          <svg-icon class="ivu-icon" name="md-save" color="#666" scale="4"></svg-icon>
        </div>
      </Tooltip>

      <Tooltip content="Delete" :delay="500">
        <Icon
          class="inspector-button"
          @click="deleteSelectedFlow"
          type="md-trash"
          color="#666"
          size="18"
        />
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
          <Tooltip content="Deactivate mock group" :delay="500">
            <Icon type="ios-backspace-outline" color="red" size="16" />
          </Tooltip>
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

    <MockDataSelector ref="searchModal">
      <template #selected>
        <div v-if="activatedGroups">
          <label style="padding-right:5px">Activated Mock Group:</label>
          <Tag v-for="group in activatedGroups" :key="group.id">{{group.name}}</Tag>
        </div>
      </template>
      <template #searchItem="{ searchResult }">
        <Row type="flex" align="middle" class="search-row" @click.native="onActivateClick(searchResult.id)">
          <Col span="22">
            <p class="search-item">
              <b class="search-item-title">{{searchResult.name}}</b>
              <span class="search-item-path">{{searchResult.abs_parent_path}}</span>
            </p>
          </Col>
          <Col span="2" align="right">
            <Icon
              type="ios-play"
              color="#19be6b"
              size="22"
              class="search-item-btn"
            />
          </Col>
        </Row>
      </template>
    </MockDataSelector>
  </div>
</template>

<script>
import MockDataSelector from '@/components/SearchModal.vue'
import Icon from 'vue-svg-icon/Icon.vue'

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
    MockDataSelector,
    'svg-icon': Icon
  },
  data: function () {
    return {
      showClearModal: false,
      recordingBtn: stopedStatus
    };
  },
  mounted () {
    this.getRecordStatus()
  },
  computed: {
    showDataButtons () {
      return this.$store.state.inspector.showDataButtons
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
        text = text + activatedGroups[groupId].name + ' '
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
      this.$refs.searchModal.toggal()
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
      if (Object.keys(this.activatedGroups).length <= 0) {
        this.$Message.warning('Please activate a mock group before save.')
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
                title: 'HTTP flow saved',
                desc: resp.data.message
              }
            )
          } else {
            this.$Notice.error(
              {
                title: 'Save HTTP flow failed',
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
    onActivateClick (groupId) {
      this.$store.dispatch('activateGroup', groupId)
    }
  }
}
</script>

<style>
.inline {
  display: inline;
}
.inspector-button-bar {
  flex-grow: 1;
}
.inspector-button {
  padding: 3px 8px 3px;
  font-size: 14px;
  cursor: pointer;
}
.inspector-searchbox {
  width: 30vw;
  float: right;
}
</style>

