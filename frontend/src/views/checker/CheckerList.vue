<template>
  <div class="data-table">
    <div class="cell-border" style="background:#f8f8f9;font-size:14px">
      <Strong>Checker scripts</Strong>
    </div>
    <CellGroup style="" @on-click="onClickCell">
      <Cell 
        class="cell-border" 
        v-for="checker in checkerList" 
        title="With Switch" 
        :key="checker.name"
        :name="checker.name"
        :selected="checker.select"
      >
        {{checker.name}}
        <i-switch slot="extra" v-model="checker.activated" size="small" @on-change="changeStatus(checker)"></i-switch>
      </Cell>
    </CellGroup>
  </div>
</template>

<script>
export default {
  computed: {
    checkerList() {
      return this.$store.state.checker.checkers;
    }
  },
  methods: {
    onClickCell(name) {
      this.$store.commit("setFocusChecker", name);
      this.$store.dispatch("loadCheckerDetail", name);
    },
    changeStatus(checker) {
      this.$store.dispatch("updateCheckerStatus", checker);
    }
  }
};
</script>

<style scoped>
.data-table th div {
  padding-left: 5px;
  padding-right: 5px;
}
.data-table td div {
  padding-left: 5px;
  padding-right: 5px;
}
.cell-border {
  padding: 5px 5px;
  border-bottom: 1px dashed #dcdee2;
}
</style>