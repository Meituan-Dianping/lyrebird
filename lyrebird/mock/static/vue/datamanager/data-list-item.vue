<template>
    <tr @click="onClick" :class="foucs">
        <td>
            <input type="checkbox" v-model="selected">
        </td>
        <td>
            <span class="path">
                {{ item.name }}
            </span>
        </td>
    </tr>
</template>

<script>
    module.exports = {
        props: ['item'],
        computed: {
            selected: {
                get(){
                    return this.$store.state.dataManager.selectedData.indexOf(this.item.id)>=0
                },
                set(value){
                    if(value){
                        this.$store.commit('addSelectedData', this.item.id)
                    }else{
                        this.$store.commit('deleteSelectedData', this.item.id)
                    }
                }
            },
            foucs(){
                return { foucs: this.$store.state.dataManager.foucsData === this.item.id}
            }
        },
        methods: {
            onClick(){
                this.$store.commit('setFoucsData', this.item.id)
                this.$store.dispatch({
                    type: 'loadDataDetail',
                    groupId: this.$store.state.dataManager.currentDataGroup, 
                    dataId: this.item.id
                    })
            }
        }
    }
</script>

<style>
.foucs{
  background-color: rgb(217, 239, 252)
}
.path{
  color: darkgreen
}
.host{
  color: darkgrey
}
</style>
