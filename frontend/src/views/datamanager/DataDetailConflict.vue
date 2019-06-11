<template>
  <div>
    <Row v-for="(value, index) in information" :key="index" style="padding-top:10px;word-break:break-all">
      <Col span="2" offset="1">
        <p>NO.{{index + 1}}</p>
        <p>{{value.data.name}}</p>
      </Col>
      <Col span="20" offset="1">
        <Row>
          <Col span="7">
            <b>Name</b>
          </Col>
          <Col span="16" offset="1">
            <b>Path</b>
          </Col>
        </Row>
        <Row v-for="item in value.conflict_data" :key="item.id" style="padding-bottom:10px">
          <Col span="7">
            <span>{{item.name}}</span>
          </Col>
          <Col span="16" offset="1">
            <span>{{item.abs_parent_path}}</span>
          </Col>
        </Row>
      </Col>
    </Row>
  </div>
</template>

<script>
export default {
  props: ['information']
}
</script>
