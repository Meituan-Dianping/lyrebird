<template>
  <ContextMenuItem>
    <div>
      <span
        style="color: #52c41a; font-weight: bold; padding-left: 3px; padding-right: 3px"
      >{{event.flow.request.method}}</span>
      <span
        style="font-weight: bold; padding-left: 3px; padding-right: 3px"
        :style="{color: responseCodeColor}"
      >{{event.flow.response.code}}</span>
      <a
        style="font-weight: bold; padding-left: 3px; padding-right: 3px"
        @click.capture="openURL"
      >{{event.flow.request.scheme}}://{{event.flow.request.host}}{{ event.flow.request.path}}</a>
    </div>
    <div>
      <span class="property_font">Duration: {{duration}}</span>
      <span class="property_font">Size: {{size}}</span>
    </div>
  </ContextMenuItem>
</template>

<script>
import { readablizeBytes } from '@/utils'
import ContextMenuItem from '@/views/event/ContextMenuItem.vue'

export default {
  props: [
    'event'
  ],
  components: {
    ContextMenuItem
  },
  computed: {
    duration () {
      const duration = this.event.flow.duration
      if (duration >= 1) {
        return Math.round(duration * 100 / 100) + 's'
      } else {
        return (duration * 1000).toFixed(0) + 'ms'
      }
    },
    size () {
      const size = this.event.flow.size
      return readablizeBytes(size)
    },
    responseCodeColor () {
      if (this.event.flow.response.code <= 399) {
        return '#52c41a'
      } else {
        return '#ed4014'
      }
    }
  },
  methods: {
    openURL () {
      if (this.event.flow.request.method === 'GET') {
        window.open(this.event.flow.request.url, '_blank')
      }
    }
  }
}
</script>

<style scoped>
.title {
  font-size: 14px;
}
.info {
  color: dimgray;
  font-size: 12px;
}
.tag {
  color: green;
}
.property_font {
  font-size: 12px;
  font-weight: bold;
  color: #aeaeae;
  padding-left: 5px;
  padding-right: 5px;
}
</style>
