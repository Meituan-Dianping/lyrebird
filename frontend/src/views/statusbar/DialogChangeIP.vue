<template>
  <v-dialog v-model="shown" width="400">
    <v-card>
      <v-card-title style="font-size:16px;">Change IP</v-card-title>

      <v-divider/>

      <v-card-text class="overflow-auto py-0 mt-3 mb-2" style="font-size:14px">
          <v-radio-group v-model="selectedIp">
            <v-radio
              color="primary"
              v-for="(ipInfo, index) in ipList"
              :key="index"
              
              :value="ipInfo.addr"
              mandatory
            >
              <template v-slot:label>
                <span>{{ipInfo.addr}}</span>
                <v-chip
                  small
                  class="ml-2"
                  v-show="ipInfo.desc"
                >
                  {{ipInfo.desc}}
                </v-chip>
              </template>
            </v-radio>
          </v-radio-group>
      </v-card-text>

      <v-divider/>

      <v-card-actions>
        <v-spacer/>
        <v-btn text @click="onCancel">
          Cancel
        </v-btn>
        <v-btn text color="primary" @click="onSave">
          Save
        </v-btn>
      </v-card-actions>

    </v-card>
  </v-dialog>
</template>

<script>
export default {
  data () {
    return {
      isShowDialogChangeIp: false,
      selectedIp: ''
    }
  },
  computed: {
    shown: {
      get () {
        this.OnShown()
        return this.$store.state.isShownDialogChangeIp
      },
      set (val) {
        this.$store.commit('setIsShownDialogChangeIp', val)
      }
    },
    ipList () {
      return this.$store.state.ipList
    }
  },
  methods: {
    OnShown () {
      this.selectedIp = this.$store.state.settings.config.ip
    },
    onSave () {
      this.$store.dispatch('updateConfigByKey', {
        'ip': this.selectedIp
      })
      this.shown = false
    },
    onCancel () {
      this.shown = false
    }
  }
}
</script>
