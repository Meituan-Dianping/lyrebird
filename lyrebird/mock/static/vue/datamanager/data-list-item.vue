<template>
    <tr @click="onClick" :class="foucs">
        <td>
            <input type="checkbox" v-model="selected">
        </td>
        <td>
            <span class="path">
                {{ location.pathname }}
            </span>
        </td>
        <td>
            <span class="host">
                {{ location.hostname }}
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
                    return this.$store.state.dataManager.selectedData.indexOf(this.item.name)>=0
                },
                set(value){
                    if(value){
                        this.$store.commit('addSelectedData', this.item.name)
                    }else{
                        this.$store.commit('deleteSelectedData', this.item.name)
                    }
                }
            },
            foucs(){
                return { foucs: this.$store.state.dataManager.foucsData === this.item.name}
            },
            location(){
                var l = document.createElement("a");
                l.href = this.item.url;
                return l;
            }
        },
        methods: {
            onClick(){
                this.$store.commit('setFoucsData', this.item.name)
                this.$store.dispatch({
                    type: 'loadDataDetail',
                    groupName: this.$store.state.dataManager.currentDataGroup, 
                    dataName: this.item.name
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
