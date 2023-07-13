<template>
  <v-dialog v-model="isShown" width="50%" class="data-list-dialog-delete">
    <v-card :loading="isLoadingChildren">
      <v-card-title style="font-size:16px;">Delete Confirmation</v-card-title>

      <v-divider/>

      <v-card-text style="max-height: 300px;" class="overflow-auto py-0 mt-3 mb-2">
        <p class="data-list-dialog-delete-info">
          <b>Delete {{deleteItem.length}} {{deleteItem.length===1 ? 'item' : 'items'}}: </b>
        </p>
        <p v-for="(value, index) in deleteItem" class="mb-3">
          <span class="data-list-dialog-delete-item pl-0" style="font-size:12px">{{value.abs_parent_path}}</span>
        </p>
      </v-card-text>

      <v-card-text v-show="source==='multiple'" class="data-list-dialog-delete-advanced mt-2">

        <v-row justify="center">
          <v-expansion-panels accordion>
            <v-expansion-panel>
              <v-expansion-panel-header style="font-size:12px;height:32px;color:rgba(0,0,0,.6)">Advanced</v-expansion-panel-header>
              <v-expansion-panel-content class="data-list-dialog-delete-tree">
                <v-row no-gutters justify="center">

                  <v-col cols="4">
                    <div :class="deleteSelectionType === 'all'? 'img-border' : ''" @click.stop="deleteSelectionType='all'">
                      <v-treeview
                        :items="selectionTypeExampleData"
                        dense
                        open-all
                        expand-icon=""
                        selection-type="leaf"
                        selected-color="primary"
                      >
                        <template v-slot:label="{ item }">
                          <span style="font-size:12px;">
                            <v-icon small color="primary">mdi-checkbox-marked</v-icon>
                            {{item.name}}
                          </span>
                        </template>
                      </v-treeview>
                    </div>
                  </v-col>

                  <v-col cols="4">
                    <div :class="deleteSelectionType === 'leaf'? 'img-border' : ''"  @click="deleteSelectionType='leaf'">
                      <v-treeview
                        :items="selectionTypeExampleData"
                        dense
                        open-all
                        expand-icon=""
                        selection-type="independent"
                        selected-color="primary"
                      >
                        <template v-slot:label="{ item }">
                          <span style="font-size:12px;">
                            <v-icon small color="primary">
                              {{item.id == 'parent'? 'mdi-checkbox-blank-outline':'mdi-checkbox-marked'}}
                            </v-icon>
                            {{item.name}}
                          </span>
                        </template>
                      </v-treeview>
                    </div>
                  </v-col>

                </v-row>
                <v-row justify="center" no-gutters>
                  <v-col cols="4" style="font-size:14px">
                    <p class="text-center data-list-dialog-delete-advanced-selection my-1">Delete Leaf and Parent</p>
                  </v-col>
                  <v-col cols="4">
                    <p class="text-center data-list-dialog-delete-advanced-selection my-1">Delete Leaf only</p>
                  </v-col>
                </v-row>

              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-row>

      </v-card-text>

      <v-divider/>

      <v-card-actions>
        <v-spacer/>
        <v-btn
          color="error"
          text
          @click="onTreeNodeDelete"
        >
          Delete
        </v-btn>
        <v-btn
          color="primary"
          text
          @click="isShown = false"
        >
          Cancel
        </v-btn>
      </v-card-actions>

    </v-card>

  </v-dialog>
</template>

<script>
export default {
  props: [],
  data () {
    return {
      deleteSelectionType: 'all',
      isLoadingChildren: false,
      selectionTypeExampleData: [
        {
          id: 'parent',
          name: 'Parent',
          children: [
            {
              id: 'leaf1',
              name: 'Leaf #1'
            },
            {
              id: 'leaf2',
              name: 'Leaf #2'
            }
          ]
        }
      ]
    }
  },
  computed: {
    isShown: {
      get () {
        return this.$store.state.dataManager.isShownDeleteDialog
      },
      set (val) {
        this.$store.commit('setIsShownDeleteDialog', val)
      }
    },
    nodeInfo () {
      return this.$store.state.dataManager.focusNodeInfo
    },
    source () {
      return this.$store.state.dataManager.deleteDialogSource
    },
    deleteNode () {
      return this.$store.state.dataManager.deleteNode
    },
    deleteItem () {
      return this.getDeleteItem()
    }
  },
  methods: {
    onTreeNodeDelete () {
      const deleteItemId = []
      for (const item of this.deleteItem) {
        deleteItemId.push(item.id)
      }
      this.$store.dispatch('deleteByQuery', deleteItemId)
      this.$store.commit('setIsSelectableStatus', false)
      this.isShown = false
    },
    getDeleteItem () {
      this.isLoadingChildren = true
      const allNodeSet = this.getDeleteItemSelectionTypeAll()
      this.isLoadingChildren = false

      if (this.deleteSelectionType === 'all') {
        return Array.from(allNodeSet)
      }
      if (this.deleteSelectionType === 'leaf') {
        return this.getDeleteItemSelectionTypeLeaf(allNodeSet)
      } 
      return []
    },
    getDeleteItemSelectionTypeAll () {
      const allNode = new Set()
      for (const node of this.deleteNode) {
        const nodeChildren = this.getNodeChildren(node)
        for (const child of nodeChildren) {
          allNode.add(child)
        }
      }
      return Array.from(allNode)
    },
    getNodeChildren (node) {
      let nodeList = []
      nodeList.push(node)
      if (!node.children || node.children.length===0) {
        return nodeList
      }
      for (const child of node.children) {
        nodeList.push(...this.getNodeChildren(child))
      }
      return nodeList
    },
    getDeleteItemSelectionTypeLeaf (allNode) {
      const allNodeLeaf = []
      for (const node of allNode) {
        if (this.$store.state.dataManager.selectedLeaf.indexOf(node.id) > -1) {
          allNodeLeaf.push(node)
        }
      }
      return allNodeLeaf
    }
  }
}
</script>

<style>
.data-list-dialog-delete .v-expansion-panel-header {
  padding: 0px;
  min-height: 20px;
}
.img-border {
  border: 2px solid #5F5CCA;
  border-radius: 3px;
}
.data-list-dialog-delete-tree .v-treeview--dense .v-treeview-node__root {
  min-height: 28px;
  padding: 0px;
}
.data-list-dialog-delete-advanced .v-expansion-panel-header {
  padding: 0px 12px;
  min-height: 28px;
}
.data-list-dialog-delete-advanced-selection{
  font-size: 12px;
  color: #000520;
}
.data-list-dialog-delete-advanced .v-expansion-panel-content__wrap {
  padding-bottom: 0px;
}
.data-list-dialog-delete-info {
  font-size: 14px;
}
.data-list-dialog-delete-item {
  font-size: 12px;
  word-break: break-all;
}
</style>
