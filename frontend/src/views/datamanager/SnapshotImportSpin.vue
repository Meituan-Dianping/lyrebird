<template>
  <div>
    <!-- snapshot import spin -->
    <Spin fix v-if='spinDisplay'>
      <Icon type='ios-loading' size='25' class='snapshot-import-spin-icon-load'></Icon>
      <div>
        <span style='font-size:25px'>importing snapshot……</span>
      </div>
    </Spin>
  </div>
</template>

<script>
export default {
  computed: {
    spinDisplay () {
      return this.$store.state.dataManager.spinDisplay
    }
  }
}
</script>
<style scoped>
.snapshot-import-spin-icon-load {
  animation: ani-demo-spin 1s linear infinite;
}
</style>
