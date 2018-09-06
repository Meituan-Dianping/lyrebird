<template>
<card :padding="5">
    <i-button @click="test">Test</i-button>

    <div class="inline">
      <i-select v-model="selectedDataGroup" filterable clearable class="data-group" @on-change="onGroupSelected">
        <option-group label="DataGroup">
          <i-option v-for="item in groupList" :key="item" :value="item">{{item}}</i-option>
        </option-group>
      </i-select>
    </div>

    <modal v-model="showCreateGroupModal" title="Dialog" @on-ok="creatGroupModalOk">
      <label>Please select a data group or create a new data group first</label>
      <i-input placeholder="GroupName" v-model="newDataGroupName">
    </modal>

    <modal v-model="showClearModal" title="Alert" @on-ok="clearModalOk" @on-cancel="showClearModal=false">
      <p>Clear flow list?</p>
    </modal>
  </card>
</template>

<script>
    module.exports={
        methods: {
          test(){
            this.$store.dispatch('loadDataList', 'TTT')
          },
          onGroupSelected(){
            console.log('hh');
          }
        },
        computed: {
          selectedDataGroup: {
            get(){
              return this.$store.state.dataManager.currentDataGroup
            },
            set(value){
              this.$store.commit('setCurrentDataGroup', value)
            }
          },
          groupList(){
            return this.$store.state.dataManager.groupList
          }
        }
    }
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
