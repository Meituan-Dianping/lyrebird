<template>
    <card>
        <div class="data-list">
            <table class="table">
                <thead>
                    <tr>
                        <th>
                            <input type="checkbox">
                        </th>
                        <th>Host</th>
                        <th>Path</th>
                    </tr>
                </thead>
                <tbody>
                    <tr is="data-list-item" v-for="(item, index) in dataItems" :key="index">
                        item
                    </tr>
                </tbody>
            </table>
        </div>
    </card>
</template>

<script>
    module.exports = {
        comments: {
            'data-list-item': httpVueLoader('/static/vue/datamanager/data-list-item.vue')
        },
        computed: {
            dataItems: function(){
                return this.$store.state.dataManager.dataList
            }
        }
    }
</script>

<style>
    .data-list {
        max-height: 550px;
        overflow-y: auto;
    }
</style>
