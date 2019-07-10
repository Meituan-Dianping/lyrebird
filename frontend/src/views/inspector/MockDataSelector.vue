<template>
  <Modal v-model="shown" title="Mock data selector">
    <Input search clearable v-model="searchStr"></Input>
  </Modal>
</template>

<script>
export default {
  data () {
    return {
      searchStr: '',
      shown: false
    }
  },
  methods: {
    togal () {
      this.shown = !this.shown
    }
  },
}
</script>
