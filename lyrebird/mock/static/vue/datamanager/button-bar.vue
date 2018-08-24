<template>
<card :padding="5">
    <tooltip content="Clear & reload flow list" :delay="500">
      <i-button @click="showClearModal=true" icon="md-trush"></i-button>
    </tooltip>

    <div class="inline">
      <div class="inline">
        <divider type="vertical"></divider>
      </div>

      <tooltip content="Delete selected flow" :delay="500">
        <i-button icon="md-trash"></i-button>
      </tooltip>
    </div>

    <div class="inline">
      <divider type="vertical"></divider>
    </div>

    <label>DataGroup:</label>

    <div class="inline pull-right">
      <i-input search clearable class="search-box" v-model="searchStr"></i-input>
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
        
    }
</script>