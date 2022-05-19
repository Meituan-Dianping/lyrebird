<template>

  <v-dialog v-model="shown" width="600">
    <v-card elevation="4">
      <v-card-title style="font-size:16px;">Duplicate</v-card-title>

      <v-divider/>

      <v-card-text class="overflow-auto py-0 mt-3 mb-2">
        <v-row justify="center">
          <v-col>
            <p>
              You are duplicating {{nodeInfo.type}} <b>{{nodeInfo.name}}</b>
            </p>
            <p>
              <b>{{duplicateNodeChildrenCount}}</b> item will be duplicated, are you sure you want to duplicate them?
            </p>
          </v-col>
        </v-row>
      </v-card-text>

      <v-divider/>

      <v-card-actions>
        <v-spacer/>
        <v-btn text @click="onCancel">
          Cancel
        </v-btn>
        <v-btn text color="warning" @click="onDuplicate">
          Duplicate
        </v-btn>
      </v-card-actions>

    </v-card>
  </v-dialog>
</template>

<script>
export default {
  computed: {
    shown: {
      get () {
        return this.$store.state.dataManager.isShownDuplicateDialog
      },
      set (val) {
        this.$store.commit('setIsShownDuplicateDialog', val)
      }
    },
    nodeInfo () {
      return this.$store.state.dataManager.focusNodeInfo
    },
    duplicateNodeChildrenCount () {
      return this.countNodeChildren(this.nodeInfo)
    }
  },
  methods: {
    onDuplicate () {
      this.$store.dispatch('duplicateGroupOrData', this.nodeInfo)
      this.shown = false
    },
    onCancel () {
      this.shown = false
    },
    countNodeChildren (node) {
      let count = 0
      if (!node.children || node.children.length===0) {
        return 0
      }
      for (const child of node.children) {
        count += this.countNodeChildren(child)
      }
      return count + node.children.length
    }
  }
}
</script>
