<template>
  <div @contextmenu.prevent="onContextMenu" class="contextmenu-item">
    <div class="contextmenu-item-container">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    onContextMenu (event) {
      this.$bus.$emit('contextmenu.show', event)
    }
  }
}
</script>

<style less>
.contextmenu-item {
  display: flex;
  min-height: 40px;
  align-items: center; /*指定垂直居中*/
}
.contextmenu-item-container {
  display: block;
}
</style>

