<template>
    <Card> 
        <div class="data-list">
            <Table highlight-row 
                size='small'
                ref="selection" 
                :columns="columns" 
                :data="dataItems"
                @on-row-click="onClickRow" 
                @on-selection-change="onClickSelect" 
            >
            </Table>
        </div>
    </Card>
</template>

<script>
export default{
    data: function () {
      return {
        columns: [
            {
                type: 'selection',
                width: 50,
                align: 'center'
            },
            {
                title: 'Name',
                key: 'name'
            }
        ],
      };
    },
    computed: {
        dataItems(){
            return this.$store.state.dataManager.dataList
        }
    },
    methods: {
        onClickRow(data){
            this.$store.commit('setFoucsData', data.id)
            this.$store.dispatch({
                type: 'loadDataDetail',
                groupId: this.$store.state.dataManager.currentDataGroup, 
                dataId: data.id
                })
        },
        onClickSelect(data){
            this.$store.commit('setSelectedData', data)
        }
    }
}
</script>

<style>
    .data-list {
        height: calc(100vh - 166px);
        /* total:100vh
        header: 38px
        padding: 5px + 5px
        buttonBar: 48px
        card-padding: 16px
        table
        card-padding: 16px
        padding: 5px
        footer: 28px
         */
        overflow-y: auto;
    }
</style>
