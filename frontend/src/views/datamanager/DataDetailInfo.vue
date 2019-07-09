<template>
  <div>
    <Row v-for="(value, key) in information" :key="key" style="padding-top:10px">
      <Col span="3" offset="1">
        <span contenteditable="true">{{key}}</span>
      </Col>
      <Col span="20">
        <span>{{value}}</span>
      </Col>
    </Row>
  </div>
</template>

<script>
export default {
  props: ['information']
}
</script>
