<template>
    <div>
        <Row class="button-bar">
            <button-bar></button-bar>
        </Row>
        <div class="divider"></div>
        <Row>
            <i-col span="12">
                <data-list class="container-left"></data-list>
            </i-col>
            <div class="split"></div>
            <i-col span="12">
                <data-detail class="container-right"></data-detail> 
            </i-col>
        </Row>
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

<style scoped>
  .button-bar {
    height: 38px;
    display: flex;
    align-items: center;
  }
  .container-left {
    margin-right: 0px
  }
  .container-right {
    margin-left: 5px
  }
  .divider{
    display: block;
    width: 100%;
    height: 1px;
    background: #eee;
    top: 0;
    left: 0;
  }
  .split{
    display: block;
    position: absolute;
    top: 0;
    bottom: 0;
    left: 50%;
    border: 1px dashed #eee;
  }
</style>
