<template>
    <tr @click="onClick" :class="foucs">
        <td>
            <input type="checkbox" v-model="selected">
        </td>
        <td>
            <strong>
                {{item[0]}}
            </strong>
        </td>
        <td>
            -
        </td>
    </tr>
</template>

<script>
    module.exports = {
        props: ['item'],
        computed: {
            selected: function(){
                return false
            },
            foucs: function(){
                return { foucs: this.$store.state.dataManager.foucsData === this.item[0]}
            }
        },
        methods: {
            onClick(){
                this.$store.commit('setFoucsData', this.item[0])
                this.$store.dispatch({
                    type: 'loadDataDetail',
                    groupName: this.$store.state.dataManager.currentDataGroup, 
                    dataName: this.item[0]
                    })
            }
        }
    }
</script>

<style>
.foucs{
  background-color: rgb(217, 239, 252)
}
</style>
