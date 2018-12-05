<template>
  <Card :padding="5">
    <Row type="flex" justify="start" align="middle">
      <i-col span="2">
        <label>DataGroup:</label>
      </i-col>
      <i-col span="4">
        <div>
          <i-select v-model="selectedDataGroup" filterable clearable @on-change="onGroupSelected">
            <option-group label="DataGroup">
              <i-option v-for="item in groupList" :key="item.id" :value="item.id">{{item.name}}</i-option>
            </option-group>
          </i-select>
        </div>
      </i-col>
      <i-col span="12">
        <i-button>NewGroup</i-button>
        <i-button>DeleteGroup</i-button>
        <i-button>NewData</i-button>
        <i-button>DeleteData</i-button>
      </i-col>
    </Row>

    

    
  </Card>
</template>

<script>
export default {
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

</style>
