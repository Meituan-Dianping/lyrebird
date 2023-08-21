<template>
  <div class="inspector-pro-button-bar d-flex justify-space-between flex-grow-1">
    <div class="inline">

      <v-tooltip bottom open-delay=500>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon @click="isShowClearDialog=true" v-bind="attrs" v-on="on">
            <v-icon size="18px" color="accent">mdi-eraser</v-icon>
          </v-btn>
        </template>
        <span>Clear</span>
      </v-tooltip>

      <v-tooltip right open-delay=500 v-if=this.eventFileOversized>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon v-bind="attrs" v-on="on">
            <v-icon size="18px" color="warning">mdi-information-outline</v-icon>
          </v-btn>
        </template>
        <span>Database path: {{ eventFilePath }}</span><br>
        <span>Database size: {{ eventFileSize }}</span>
        <b style="white-space:pre">   Please clear</b><v-icon size="18px" color="accent">mdi-eraser</v-icon><b>as soon as possible.</b>
      </v-tooltip>
      <v-tooltip right open-delay=500 v-else>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon v-bind="attrs" v-on="on">
            <v-icon size="18px" color="accent">mdi-information-outline</v-icon>
          </v-btn>
        </template>
        <span>Database path: {{ eventFilePath }}</span><br>
        <span>Database size: {{ eventFileSize }}</span>
      </v-tooltip>

    </div>

    <div class="inline">
      <div class="inspector-pro-search">
        <v-text-field
          outlined
          dense
          prepend-inner-icon="mdi-magnify"
          height=26
          v-model="eventSearchStr"
          class="inspector-pro-search-text"
          label="Separate multiple keywords by spaces"
          clearable
        />
      </div>
    </div>
    <v-dialog
      v-model="isShowClearDialog"
      width="500"
    >

      <v-card>
        <v-card-title style="font-size: 16px">
          Clear confirm
        </v-card-title>

        <v-card-text>
          Clear event list?
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="isShowClearDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            text
            @click="clearAllEvents"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { eventFileInfo } from '@/api'
import Icon from 'vue-svg-icon/Icon.vue'

export default {
  name: 'eventButtonBar',
  components: {
    'svg-icon': Icon
  },
  activated () {
    this.checkEventFileInfo()
  },
  data () {
    return {
      isShowClearDialog: false
    }
  },
  computed: {
    eventSearchStr: {
      get () {
        return this.$store.state.event.eventSearchStr
      },
      set (val) {
        this.$store.commit('setEventSearchStr', val)
      }
    },
    eventFilePath() {
      return this.$store.state.event.eventFilePath
    },
    eventFileSize() {
      return this.$store.state.event.eventFileSize
    },
    eventFileOversized() {
      return this.$store.state.event.eventFileOversized
    }
  },
  methods: {
    checkEventFileInfo () {
      eventFileInfo()
        .then(response => {
          let eventFileInfo = response.data.file_info
          let eventFilePath = eventFileInfo.path
          let eventFileSizeThreshold = eventFileInfo.threshold
          let eventFileSize = eventFileInfo.size
          let eventFileOversized = eventFileInfo.oversized
          if (eventFileOversized) {
            this.$bus.$emit('msg.info', 'Database size has exceeded ' + eventFileSizeThreshold +', please clear it as soon!')
          }
          this.$store.commit('setEventFilePath', eventFilePath)
          this.$store.commit('setEventFileSizeThreshold', eventFileSizeThreshold)
          this.$store.commit('setEventFileSize', eventFileSize)
          this.$store.commit('setEventFileOversized', eventFileOversized)
        }).catch(error => {
          this.$bus.$emit('msg.error', 'Get event file info error: ' + error.data)
        })
    },
    clearAllEvents () {
      this.isShowClearDialog = false
      this.$store.dispatch('clearEvents')
    }
  }
}
</script>

<style>
.inspector-pro-button-bar {
  height: 26px;
}
.inline {
  display: inline-flex;
  justify-content: center;
  min-height: 26px;
  height: 26px;
  max-height: 26px;
  align-content: flex-start;
  flex-wrap: nowrap;
  align-items: center;
  margin-bottom: 7px;
}
.button-bar-diff-mode .v-input--switch__track {
  height: 19px !important;
  width: 32px !important;
}
.button-bar-diff-mode .v-input--selection-controls__input {
  margin-right: 0px !important;
  width: 32px !important;
}
.button-bar-diff-mode .v-input--switch__thumb {
  height: 15px !important;
  width: 15px !important;
}
.v-application--is-ltr .button-bar-diff-mode .v-input--is-label-active .v-input--switch__thumb {
  transform: translate(11px) !important;
}
.v-application--is-ltr .button-bar-diff-mode.v-input--is-label-active .v-input--selection-controls__ripple
{
  transform: translate(11px) !important;
}
.inspector-pro-search .v-input__prepend-inner {
  margin-top: 2px !important;
}
.inspector-pro-search .v-input__append-inner {
  margin-top: 2px !important;
}
.inspector-pro-search .v-input__slot {
  padding-right: 4px !important;
  min-height: 26px !important;
  height: 26px !important;
}
.inspector-pro-search .v-icon {
  font-size: 14px !important;
}
.inspector-pro-search {
  width: 500px !important;
  height: 26px;
}
.inspector-pro-search-text {
  width: 500px;
  min-height: 26px !important;
  height: 26px !important;
  font-size: 14px !important;
  font-weight: 400;
  line-height: 14px !important;
}
.inspector-pro-search-text .v-label{
  font-size: 14px !important;
  top: 4px !important;
}
</style>
