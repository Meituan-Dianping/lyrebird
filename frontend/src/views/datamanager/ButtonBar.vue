<template>
  <div class="button-bar">
    <Row type="flex" justify="start" align="middle" :gutter="5" class="button-bar">
      <i-col span="12">
        <label class="btn-label">
          <b>Group:</b>
        </label>
        <ButtonGroup size="small">
          <Button @click="onNewGroupBtnClick" size="small">New</Button>
          <Button @click="deleteGroupModal=true" size="small">Delete</Button>
        </ButtonGroup>
        <label class="btn-label">
          <b>Current:</b>
        </label>
        <Select
          ref="groupSelector"
          v-model="selectedDataGroup"
          filterable
          clearable
          size="small"
          style="width: 15vh"
          @on-change="onGroupSelected"
        >
          <option-group label="DataGroup">
            <i-option v-for="item in groupList" :key="item.id" :value="item.id">{{item.name}}</i-option>
          </option-group>
        </Select>
        <label class="btn-label" v-if="selectedDataGroupParentName">
          <b>Parent:</b>
        </label>
        <Tag
          v-if="selectedDataGroupParentName"
          color="default"
          class="parent-name"
          @click.native="onGroupEditBtnClick"
        >{{selectedDataGroupParentName}}</Tag>
        <Button icon="md-create" type="text" @click="onGroupEditBtnClick" class="edit-btn"></Button>
      </i-col>
      <i-col span="12">
        <label>
          <b class="btn-label">Data:</b>
        </label>
        <ButtonGroup size="small">
          <Button @click="dataNameModal=true" size="small">New</Button>
          <Button @click="deleteDataModal=true" size="small">Delete</Button>
        </ButtonGroup>
        <JsonPathBar class="json-path-bar"></JsonPathBar>
      </i-col>
    </Row>
    <Modal v-model="groupNameModal" title="DataGroup" @on-ok="createNewGroup">
      <Form :label-width="80">
        <FormItem label="GroupName">
          <Input v-model="dataGroupProp.name" placeholder="Data group name"></Input>
        </FormItem>
        <FormItem label="Parent">
          <Select
            v-model="dataGroupProp.parentId"
            @on-change="onCreateGroupModalParentChange"
            clearable
          >
            <Option
              v-for="groupItem in groupList"
              :key="groupItem.id"
              :value="groupItem.id"
            >{{groupItem.name}}</Option>
          </Select>
        </FormItem>
        <div v-show="false">
          <label v-if="dataGroupProp.parentId">Copy data from parent group</label>
          <div v-if="dataGroupProp.parentId" class="modal-data-list">
            <Table
              :columns="parentListColumns"
              :data="parentDataList"
              @on-selection-change="onModalParentDataSelectionChange"
            ></Table>
          </div>
        </div>
      </Form>
    </Modal>
    <Modal v-model="deleteGroupModal" title="Delete group" @on-ok="deleteGroup">
      <p>Delete current group ?</p>
    </Modal>
    <Modal v-model="dataNameModal" title="Data" @on-ok="createNewData">
      <Input v-model="dataName" placeholder="Data name"></Input>
    </Modal>
    <Modal v-model="deleteDataModal" title="Delete data" @on-ok="deleteData">
      <p>Delete all selected data?</p>
    </Modal>
  </div>
</template>

<script>
import JsonPathBar from '@/views/datamanager/JsonPathBar.vue'
export default {
  components:{
    JsonPathBar
  },
  data() {
    return {
      groupNameModal: false,
      groupName: "",
      deleteGroupModal: false,
      dataNameModal: false,
      dataName: "",
      deleteDataModal: false,
      dataGroupProp: {
        id: null,
        name: "",
        parentId: null,
        CopyDataIds: []
      },
      parentListColumns: [
        {
          type: "selection",
          width: 50,
          align: "center"
        },
        {
          title: "Name",
          key: "name"
        }
      ]
    };
  },
  mounted() {
    this.$store.dispatch("loadGroupList");
  },
  methods: {
    onGroupSelected() {
      this.$store.dispatch("loadDataList", this.selectedDataGroup);
    },
    activteCurrentGroup() {
      this.$store.dispatch("activateCurrentGroup");
    },
    createNewGroup() {
      if (this.dataGroupProp.id) {
        this.$store.dispatch("updateDataGroup", {
          groupId: this.dataGroupProp.id,
          groupName: this.dataGroupProp.name,
          parentGroupId: this.dataGroupProp.parentId
        });
      } else {
        this.$store.dispatch("newDataGroup", {
          groupName: this.dataGroupProp.name,
          parentGroupId: this.dataGroupProp.parentId
        });
      }
    },
    deleteGroup() {
      this.$store.dispatch("deleteDataGroup", this.selectedDataGroup);
    },
    createNewData() {
      this.$store.dispatch("newData", {
        groupId: this.selectedDataGroup,
        name: this.dataName
      });
    },
    deleteData() {
      this.$store.dispatch("deleteData", this.selectedDataGroup);
    },
    onCreateGroupModalParentChange(value) {
      this.$store.dispatch("loadDataListForNewGroupForm", value);
    },
    onModalParentDataSelectionChange(selection) {
      this.$store.commit("setCreateGroupModalSelectedData", selection);
    },
    onNewGroupBtnClick() {
      this.dataGroupProp.id = null;
      this.dataGroupProp.name = null;
      this.dataGroupProp.parentId = null;
      this.groupNameModal = true;
    },
    onGroupEditBtnClick() {
      this.dataGroupProp.id = this.selectedDataGroup;
      this.dataGroupProp.name = this.selectedDataGroupName;
      this.dataGroupProp.parentId = this.selectedDataGroupParentId;
      this.groupNameModal = true;
    }
  },
  computed: {
    selectedDataGroup: {
      get() {
        const selectedDataGroupId = this.$store.state.dataManager
          .currentDataGroup;
        if (!selectedDataGroupId && this.$refs.groupSelector) {
          this.$refs.groupSelector.reset();
        }
        return selectedDataGroupId;
      },
      set(value) {
        this.$store.commit("setCurrentDataGroup", value);
      }
    },
    selectedDataGroupName() {
      const groups = this.$store.state.dataManager.groupList;
      const selectedGroupId = this.$store.state.dataManager.currentDataGroup;
      let parentId = null;
      for (const group of groups) {
        if (group.id === selectedGroupId) {
          return group.name;
        }
      }
    },
    selectedDataGroupParentId() {
      const groups = this.$store.state.dataManager.groupList;
      const selectedGroupId = this.$store.state.dataManager.currentDataGroup;
      let parentId = null;
      for (const group of groups) {
        if (group.id === selectedGroupId) {
          return group.parent;
        }
      }
      return null;
    },
    selectedDataGroupParentName() {
      const groups = this.$store.state.dataManager.groupList;
      const selectedGroupId = this.$store.state.dataManager.currentDataGroup;
      let parentId = null;
      for (const group of groups) {
        if (group.id === selectedGroupId) {
          parentId = group.parent;
          break;
        }
      }
      for (const group of groups) {
        if (group.id === parentId) {
          return group.name;
        }
      }
      return "";
    },
    groupList() {
      return this.$store.state.dataManager.groupList;
    },
    parentDataList() {
      return this.$store.state.dataManager.createGroupModal.parentDataList;
    }
  }
};
</script>

<style scoped>
.edit-btn {
  padding: 0;
  font-size: 16px;
}
.button-bar {
  flex-grow: 1;
  display: flex;
}
.modal-data-list {
  height: 30vh;
  overflow-y: auto;
}
.group-label {
  margin-left: 5px;
  margin-right: 5px;
}
.btn-bar button {
  padding: 0;
  font-size: 18px;
  border-radius: 0px;
}
.parent-name {
  max-width: 200px;
  text-overflow: ellipsis;
}
.btn-label {
  margin-left: 5px;
  margin-right: 5px;
}
</style>
