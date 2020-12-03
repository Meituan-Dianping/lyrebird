<template>
  <ContextMenuItem>
    <div
      class="ivu-tag ivu-tag-checked"
      :style="{ background: bgColor, color: '#ffffff'}"
      style="min-width:60px;text-align:center"
    >
      <b>{{channel}}</b>
    </div>
  </ContextMenuItem>
</template>

<script>
import ContextMenuItem from '@/views/event/ContextMenuItem.vue'

export default {
  props: ['channel'],
  components: {
    ContextMenuItem
  },
  computed: {
    bgColor () {
      if (this.channel === 'flow') {
        return '#0fccbf'
      } else if (this.channel === 'notice') {
        return '#ff9900'
      } else if (this.channel === 'snapshot') {
        return '#52A7F9'
      } else {
        return '#808695'
      }
    }
  },
}
</script>
