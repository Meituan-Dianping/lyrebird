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

  </card>
</template>

<script>
  module.exports = {
    mounted() {
      this.$store.dispatch('loadGroupList')
    },
    methods: {
      test() {
        this.$store.dispatch('loadDataList', 'TTT')
      },
      onGroupSelected() {
        this.$store.dispatch('loadDataList', this.selectedDataGroup)
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
