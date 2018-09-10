<template>
    <tr @click="onClick">
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
            }
        },
        methods: {
            onClick(){
                this.$store.dispatch({
                    type: 'loadDataDetail',
                    groupName: this.$store.state.dataManager.currentDataGroup, 
                    dataName: this.item[0]
                    })
            }
        }
    }
</script>
