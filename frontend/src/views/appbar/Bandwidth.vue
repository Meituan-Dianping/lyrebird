<template>
  <span class="top-bar-item mr-5">
    <v-select
      :value="bandwidth"
      :items="bandwidthTemplates"
      item-text="display"
      item-value="bandwidth"
      prepend-icon="mdi-speedometer"
      dense
      outlined
      return-object
      height="26"
      color="primary"
      class="top-bar-item-select"
      :menu-props="{ bottom: true, offsetY: true }"
      @change="updateBandwidth"
    />
  </span>
</template>

<script>

export default {
  name: 'Bandwidth',
  components: {
  },
  mounted () {
    this.$store.dispatch('loadBandwidth')
    this.$store.dispatch('loadBandwidthTemplates')
  },
  computed: {
    bandwidth () {
      return this.$store.state.bandwidth.bandwidth
    },
    bandwidthTemplates () {
      return this.$store.state.bandwidth.bandwidthTemplates
    }
  },
  methods: {
    updateBandwidth (bandwidthObj) {
      this.$store.dispatch('updateBandwidth', bandwidthObj.template_name)
    }
  }
}
</script>

<style scoped>
.top-bar-item {
  width: 180px !important;
}
.top-bar-item-select {
  width: 180px;
}
</style>
