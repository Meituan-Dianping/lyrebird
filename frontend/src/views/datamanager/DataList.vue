<template>
    <card>
        <div class="data-list">
            <table class="table">
                <thead>
                    <tr>
                        <th>
                            <input type="checkbox" v-model="selectAll">
                        </th>
                        <th>Name</th>
                    </tr>
                </thead>
                <tbody>
                    <tr is="data-list-item" 
                    v-for="(item, index) in dataItems" :key="index"
                    :item=item
                    >
                    </tr>
                </tbody>
            </table>
        </div>
    </card>
</template>

<script>
import DataListItem from '@/views/datamanager/DataListItem.vue'
export default{
    components:{
        DataListItem
    },
    computed: {
        dataItems(){
            return this.$store.state.dataManager.dataList
        },
        selectAll: {
            get(){
                return (this.$store.state.dataManager.dataList.length > 0) && (this.$store.state.dataManager.selectedData.length === this.$store.state.dataManager.dataList.length)
            },
            set(value){
                if(value){
                    this.$store.commit('selectAllData')
                }else{
                    this.$store.commit('clearSelectedData')
                }
            }
        }
    },
    methods: {
    }
}
</script>

<style>
    .data-list {
        max-height: 550px;
        overflow-y: auto;
    }
</style>
