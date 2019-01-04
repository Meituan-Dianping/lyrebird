<template>
  <div class="button-bar">
    <Row type="flex" justify="start" align="middle" :gutter="5" class="button-bar">
      <i-col span="6">
        <label>
          <b>DataGroup:</b>
        </label>
        <div class="inline">
          <Select
            ref="groupSelector"
            v-model="selectedDataGroup"
            filterable
            clearable
            size="small"
            style="width: 60%"
            @on-change="onGroupSelected"
          >
            <option-group label="DataGroup">
              <i-option v-for="item in groupList" :key="item.id" :value="item.id">{{item.name}}</i-option>
            </option-group>
          </Select>
        </div>
      </i-col>
      <i-col span="12">
        <ButtonGroup size="small">
          <Button @click="groupNameModal=true" size="small">NewGroup</Button>
          <Button @click="deleteGroupModal=true" size="small">DeleteGroup</Button>
          <Button @click="dataNameModal=true" size="small">NewData</Button>
          <Button @click="deleteDataModal=true" size="small">DeleteData</Button>
        </ButtonGroup>
      </i-col>
    </Row>
    <Modal v-model="groupNameModal" title="DataGroup" @on-ok="createNewGroup">
      <Form :label-width="80">
        <FormItem label="GroupName">
          <Input v-model="dataGroupProp.name" placeholder="Data group name"></Input>
        </FormItem>
        <FormItem label="Parent">
          <Select v-model="dataGroupProp.parentId" @on-change="onCreateGroupModalParentChange" clearable>
            <Option v-for="groupItem in groupList" :key="groupItem.id" :value="groupItem.id">{{groupItem.name}}</Option>
          </Select>
        </FormItem>
        <label v-if="dataGroupProp.parentId">Copy data from parent group</label>
        <div v-if="dataGroupProp.parentId" class="modal-data-list">
          <Table
          :columns="parentListColumns"
          :data="parentDataList"></Table>
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
export default {
  data() {
    return {
      groupNameModal: false,
      groupName: '',
      deleteGroupModal: false,
      dataNameModal: false,
      dataName: '',
      deleteDataModal: false,
      dataGroupProp:{
        name: '',
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
    createNewGroup(){
      this.$store.dispatch('newDataGroup', this.groupName)
    },
    deleteGroup(){
      this.$store.dispatch('deleteDataGroup', this.selectedDataGroup)
    },
    createNewData(){
      this.$store.dispatch('newData', {groupId:this.selectedDataGroup, name:this.dataName})
    },
    deleteData(){
      this.$store.dispatch('deleteData', this.selectedDataGroup)
    },
    onCreateGroupModalParentChange(value){
      console.log(value);
      this.$store.dispatch('loadDataListForNewGroupForm', value)
    }
  },
  computed: {
    selectedDataGroup: {
      get() {
        const selectedDataGroupId = this.$store.state.dataManager.currentDataGroup;
        if(!selectedDataGroupId && this.$refs.groupSelector){
          this.$refs.groupSelector.reset()
        }
        return selectedDataGroupId
      },
      set(value) {
        this.$store.commit("setCurrentDataGroup", value);
      }
    },
    groupList() {
      return this.$store.state.dataManager.groupList;
    },
    parentDataList(){
      return this.$store.state.dataManager.createGroupModal.parentDataList
    }
  }
};
</script>

<style>
.inline {
  display: inline;
}
.button-bar {
  flex-grow: 1;
  display: flex;
}
.modal-data-list {
  height: 30vh;
  overflow-y: auto;
}
</style>
