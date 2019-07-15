<template>
  <div>
    <Row v-for="(value, key) in information" :key="key" style="padding-top:10px">
      <Col span="3" offset="1">
        <span contenteditable="true">{{key}}</span>
      </Col>
      <Col span="20">
        <Input v-if="readOnly.indexOf(key) === -1" v-model="information[key]" :placeholder="value" size="small" />
        <span v-else>{{value}}</span>
      </Col>
    </Row>
  </div>
</template>

<script>
export default {
  props: ['information'],
  data() {
    return {
      // RULE should not be read only, support Object later
      readOnly: ['id', 'parent_id', 'type', 'rule']
    }
  }
}
</script>
