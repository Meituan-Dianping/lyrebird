<template>
  <Card :padding="5">
    <Row type="flex" justify="start" align="middle" :gutter="5">
      <i-col span="7">
        <label>
          <b>DataGroup:</b>
        </label>
        <div class="inline">
          <Select
            ref="groupSelector"
            v-model="selectedDataGroup"
            filterable
            clearable
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
        <ButtonGroup>
          <Button @click="groupNameModal=true">NewGroup</Button>
          <Button @click="deleteGroupModal=true">DeleteGroup</Button>
          <Button @click="dataNameModal=true">NewData</Button>
          <Button @click="deleteDataModal=true">DeleteData</Button>
        </ButtonGroup>
      </i-col>
    </Row>
    <Modal v-model="groupNameModal" title="Data group name" @on-ok="createNewGroup">
      <Input v-model="groupName" placeholder="Data group name"></Input>
    </Modal>
    <Modal v-model="deleteGroupModal" title="Delete group" @on-ok="deleteGroup">
      <p>Delete current group ?</p>
    </Modal>
    <Modal v-model="dataNameModal" title="Data name" @on-ok="createNewData">
      <Input v-model="dataName" placeholder="Data name"></Input>
    </Modal>
    <Modal v-model="deleteDataModal" title="Delete data" @on-ok="deleteData">
      <p>Delete all selected data?</p>
    </Modal>
  </Card>
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
      deleteDataModal: false
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
    }
  }
};
</script>

<style>
.inline {
  display: inline;
}
</style>
