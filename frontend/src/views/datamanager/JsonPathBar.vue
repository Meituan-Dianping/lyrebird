<template>
  <div>
    <label v-if="jsonPath">
      <b style="padding-right:5px">JSONPath:</b>
      <span>{{jsonPath}}</span>
    </label>
  </div>
</template>

<script>
export default {
  computed: {
    jsonPath() {
      return this.$store.state.dataManager.jsonPath
    }
  }
}
</script>
