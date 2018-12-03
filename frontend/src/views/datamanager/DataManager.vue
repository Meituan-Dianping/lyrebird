<template>
    <div>
        <row class="button-bar">
            <button-bar></button-bar>
        </row>
        <row>
        <i-col span="12">
            <data-list class="container-left"></data-list>
        </i-col>
        <i-col span="12">
            <data-detail class="container-right"></data-detail> 
        </i-col>
        </row>
    </div>
</template>

<script>
import ButtonBar from '@/views/datamanager/ButtonBar.vue'
import DataList from '@/views/datamanager/DataList.vue'
import DataDetail from '@/views/datamanager/DataDetail.vue'
export default {
    components:{
        ButtonBar,
        DataList,
        DataDetail
    }
}
</script>

<style>
  .button-bar {
    margin-bottom: 5px
  }

  .container-left {
    margin-right: 5px
  }

  .container-right {
    margin-left: 5px
  }
</style>
