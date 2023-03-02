<template>
  <v-toolbar-title class="mb-2 page-title">
    <v-dialog v-model="dialog" width="500">
      <template v-slot:activator="{ on, attrs }">
        <v-btn v-bind="attrs" v-on="on" text>
          {{ activeMenuItem.title }}
        </v-btn>
      </template>

      <v-card>
        <v-card-title class="headline grey lighten-2" primary-title>
          Plugin Infomation.
        </v-card-title>

        <v-card-text>
          <Row style="margin:30px 0;">
            <i-col span="9">
              <b style="float: right">Plugin Title</b>
            </i-col>
            <i-col span="11" offset="1">
              {{ activeMenuItem.title }}
            </i-col>
            <i-col span="9">
              <b style="float: right">Plugin Version</b>
            </i-col>
            <i-col span="11" offset="1">
              {{ activeMenuItem.version }}
            </i-col>
            <i-col span="9">
              <b style="float: right">Plugin Type</b>
            </i-col>
            <i-col span="11" offset="1" v-if="activeMenuItem.params">
              Custom Plugin
            </i-col>
            <i-col span="11" offset="1" v-else>
              Main Plugin
            </i-col>
            <i-col span="9">
              <b style="float: right">Plugin Path</b>
            </i-col>
            <i-col span="11" offset="1" v-if="activeMenuItem.params">
              {{ activeMenuItem.params.src }}
            </i-col>
            <i-col span="11" offset="1" v-else>
              {{ activeMenuItem.path }}
            </i-col>
            <i-col span="9" v-if="activeMenuItem.params">
              <b style="float: right">Plugin Location</b>
            </i-col>
            <i-col span="11" offset="1" v-if="activeMenuItem.params">
              {{ activeMenuItem.params.location }}
            </i-col>
          </Row>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="dialog = false">
            OK
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-toolbar-title>
</template>

<script>
export default {
  name: 'PluginDialog',
  data() {
    return {
      dialog: false,
    }
  },
  computed: {
    activeMenuItem() {
      return this.$store.state.activeMenuItem
    },
  },
}
</script>

<style lang="scss" scoped></style>
