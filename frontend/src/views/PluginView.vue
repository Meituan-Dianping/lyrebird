<template>
  <div style="height:calc(100vh - 44px - 40px - 28px - 12px)">
    <iframe :src="src" frameborder="0" class="plugin-frame" @load="onLoad"></iframe>
  </div>
</template>

<script>
export default {
  computed: {
    src () {
      return this.$store.state.plugin.src
    }
  },
  methods: {
    onLoad (event) {
      console.log('plugins view on load', 'src=', this.src, this.$route)
    },
  }
}
</script>

<style>
.plugin-frame {
  position: relative;
  height: 100%;
  width: 100%;
}
</style>
