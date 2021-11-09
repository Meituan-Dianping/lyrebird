<template>
  <div>
    <div class="cell-border" style="background:#f8f8f9;font-size:14px;color:#515A6E">
      <Strong>Checker scripts</Strong>
    </div>
    <Tabs v-if="checkerList.length" :value="focusPanel" class="checker-list" @on-click="onClickPanel">
      <TabPane v-for="checker_group in checkerList" :key="checker_group.key" :label="checker_group.status" :name="checker_group.key">
        <CellGroup v-if="checker_group.script_group.length" @on-click="onClickCell" v-show="checker_group.key === focusPanel">
          <template v-for="script_group in checker_group.script_group">
            <Cell 
              :key="script_group.category" 
              :title="script_group.category" 
              name="category_cell"
              disabled 
              style="padding:3px 3px;border-bottom:1px solid #dcdee2;border-top:1px solid #dcdee2;"
            >
              <Icon slot="icon" type="md-pricetag" />
            </Cell>
            <Cell 
              class="cell-border" 
              v-for="checker in script_group.scripts" 
              :label="checker.name" 
              :key="checker.name"
              :name="checker.name"
              :selected="isSelected(checker.name)"
            >{{checker.title}}
              <Tooltip content="Debug" placement="bottom-start" :delay="500" transfer>
                <Icon v-if="checker.debug" type="ios-build" color="#2b85e4" size="16"/>
              </Tooltip>
              <i-switch slot="extra" v-model="checker.activated" size="small" @on-change="changeStatus(checker)"></i-switch>
            </Cell>
          </template>
        </CellGroup>
      </TabPane>
    </Tabs>
    <div v-else class="checker-empty">
      No scripts
    </div>
  </div>
</template>

<script>
export default {
  computed: {
    checkerList() {
      return this.$store.state.checker.checkers
    },
    focusPanel() {
      return this.$store.state.checker.focusCheckerPanel
    }
  },
  methods: {
    onClickCell(name) {
      if (name === 'category_cell') {
        return;
      }
      this.$store.commit('setFocusChecker', name)
      this.$store.dispatch('loadCheckerDetail', name)
    },
    onClickPanel(name) {
      this.$store.commit('setFocusCheckerPanel', name)
    },
    changeStatus(checker) {
      this.$store.dispatch('updateCheckerStatus', checker)
    },
    isSelected(name) {
      return name === this.$store.state.checker.focusChecker
    }
  }
}
</script>

<style>
.checker-list {
  height: calc(100vh - 99px);
  /* total:100vh
    header: 38px
    textBar: 32px
    border: 1px
    list
    footer: 28px
  */
  overflow-y: auto;
  margin-right: 0;
}
.cell-border {
  padding: 5px 5px;
  border-bottom: 1px dashed #dcdee2;
}
.ivu-cell-group > .ivu-cell {
  padding: 5px 5px;
  border-bottom: 1px dashed #dcdee2;
}
.checker-list .ivu-collapse-content {
  padding: 0;
}
.checker-list .ivu-collapse-content>.ivu-collapse-content-box {
  padding-top: 0;
  padding-bottom: 0;
}
.ivu-cell-disabled {
  color:#0fccbf
}
.ivu-cell-disabled:hover {
  color:#0fccbf;
  cursor: default;
}

.checker-list .ivu-tabs-bar {
  margin-bottom: 0;
}
</style>
