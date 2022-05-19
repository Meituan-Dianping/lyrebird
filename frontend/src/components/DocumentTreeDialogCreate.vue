<template>
  <v-dialog v-model="shown" width="600">
    <v-card>
      <v-card-title style="font-size:16px;">Create {{createType}}</v-card-title>

      <v-divider/>

      <v-card-text class="overflow-auto py-0 mt-3 mb-2" style="font-size:14px">
        <v-row>
          <v-col cols="2" >
            <p class="text-right"><b>Parent</b></p>
          </v-col>
          <v-col cols="10">
            <p>{{nodeInfo.abs_parent_path}}</p>
          </v-col>
        </v-row>
        <v-row align="center" class="mt-0">
          <v-col cols="2">
            <p class="text-right"><b>Name</b></p>
          </v-col>
          <v-col cols="10">
            <v-text-field v-model="createName" dense/>
          </v-col>
        </v-row>
      </v-card-text>

      <v-divider/>

      <v-card-actions>
        <v-spacer/>
        <v-btn text @click="onCancel">
          Cancel
        </v-btn>
        <v-btn text color="primary" @click="onCreate">
          Create
        </v-btn>
      </v-card-actions>

    </v-card>
  </v-dialog>
</template>

<script>
export default {
  data () {
    return {
      createName: null,
    }
  },
  computed: {
    shown: {
      get () {
        return this.$store.state.dataManager.isShownCreateDialog
      },
      set (val) {
        this.$store.commit('setIsShownCreateDialog', val)
      }
    },
    nodeInfo () {
      return this.$store.state.dataManager.focusNodeInfo
    },
    createType () {
      return this.$store.state.dataManager.createType
    }
  },
  methods: {
    onCreate () {
      if (this.createType === 'group') {
        this.$store.commit('addGroupListOpenNode', this.nodeInfo.id)
        this.$store.dispatch('createGroup', {
          groupName: this.createName,
          parentId: this.nodeInfo.id
        })
      } else if (this.createType === 'data') {
        this.$store.dispatch('createData', {
          dataName: this.createName,
          parentId: this.nodeInfo.id
        })
      } else { }
      this.shown = false
    },
    onCancel () {
      this.createName = ''
      this.shown = false
    }
  }
}
</script>
