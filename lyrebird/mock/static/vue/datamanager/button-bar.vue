<template>
  <card :padding="5">
    <label>DataGroup:</label>
    <div class="inline">
      <i-select v-model="selectedDataGroup" filterable clearable class="data-group" @on-change="onGroupSelected">
        <option-group label="DataGroup">
          <i-option v-for="item in groupList" :key="item.id" :value="item.id">{{item.name}}</i-option>
        </option-group>
      </i-select>
    </div>

    <i-button>NewGroup</i-button>
    <i-button>DeleteGroup</i-button>
    <i-button>NewData</i-button>
    <i-button>DeleteData</i-button>
  </card>
</template>

<script>
  module.exports = {
    mounted() {
      this.$store.dispatch('loadGroupList')
    },
    methods: {
      onGroupSelected() {
        this.$store.dispatch('loadDataList', this.selectedDataGroup)
      },
      activteCurrentGroup() {
        this.$store.dispatch('activateCurrentGroup')
      }
    },
    computed: {
      selectedDataGroup: {
        get() {
          return this.$store.state.dataManager.currentDataGroup
        },
        set(value) {
          this.$store.commit('setCurrentDataGroup', value)
        }
      },
      groupList() {
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
