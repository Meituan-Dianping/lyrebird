<template>
  <ContextMenuItem>
    <div class="description">{{ eventDescription }}</div>
  </ContextMenuItem>
</template>

<script>
import ContextMenuItem from '@/views/event/ContextMenuItem.vue'

export default {
  props: ['event'],
  components: {
    ContextMenuItem
  },
  computed: {
    eventDescription () {
      if (this.event.hasOwnProperty('message')) {
        return this.event.message
      } else {
        return JSON.stringify(this.event)
      }
    }
  }
}
</script>

<style scoped>
.description {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
