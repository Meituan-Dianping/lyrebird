<template>
  <div v-if="information && information.length" style="margin:0px 5px 10px 10px">
    <Row v-for="(value, index) in information" :key="index" style="margin-top:10px;word-break:break-all;border:1px solid #ddd;">
      <Row style="background-color:#f8f8f9;padding:5px 0px 5px 0px">
        <Col span="18">
          <b style="padding:0px 5px 0px 10px">{{index + 1}}. {{value.data.name}}</b>
        </Col>
        <Col span="5" offset="1" align="right">
          <p style="padding:0px 10px 0px 5px"><b>{{value.conflict_data.length}}</b> conflicts</p>
        </Col>
      </Row>
      <Row v-for="item in value.conflict_data" :key="item.id" style="padding:5px 0px 5px 0px">
        <p style="padding:0px 10px 0px 30px"><b>Path</b>: {{item.abs_parent_path}}</p>
      </Row>
    </Row>
  </div>
  <div v-else class="data-detail-empty">
    No data
  </div>
</template>

<script>
export default {
  props: ['information']
}
</script>

<style>
.data-detail-empty {
  position: absolute; 
  top:20%;
  left:50%;
  transform:translate(-50%,-50%);
  text-align: center;
}
</style>
