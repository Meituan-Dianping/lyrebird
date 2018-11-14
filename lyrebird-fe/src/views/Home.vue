<template>
    <grid-layout :layout="layout"
                 :col-num="12"
                 :row-height="30"
                 :is-draggable="true"
                 :is-resizable="true"
                 :vertical-compact="true"
                 :use-css-transforms="true">
        <grid-item v-for="(widget,index) in widgets"
                   :key="widget"
                   :x="layout[index].x"
                   :y="layout[index].y"
                   :w="layout[index].w"
                   :h="layout[index].h"
                   :i="layout[index].i"
                   drag-allow-from=".vue-draggable-handle"
                   drag-ignore-from=".no-drag">
            <div class="text">
                <div class="vue-draggable-handle"></div>
                <div class="no-drag">
                    <component :is="widget"></component>
                </div>
            </div>
        </grid-item>
    </grid-layout>

</template>

<script>
import VueGridLayout from "vue-grid-layout";
// import Vue from 'vue'

var layout_config = {
  widget1: { x: 0, y: 0, w: 2, h: 2, i: "0" },
  widget2: { x: 2, y: 0, w: 4, h: 12, i: "1" },
  widget3: { x: 6, y: 0, w: 4, h: 4, i: "2" }
};

var layout = [];
var widget_namelist = [];

var widgets = {
  widget1: "1.vue",
  widget2: "2.vue",
  widget3: "3.vue"
};
for (var widget in widgets) {
  // Vue.component(widget, widgets[widget]);
  layout.push(layout_config[widget]);

  widget_namelist.push(widget);
}

export default {
  name: 'Home',
  data: function() {
    return {
      layout: layout,
      widgets: widget_namelist
    };
  },
  components: {
    GridLayout: VueGridLayout.GridLayout,
    GridItem: VueGridLayout.GridItem
  }
};
</script>

<style scoped>
.vue-grid-item:not(.vue-grid-placeholder) {
  background: #ccc;
  border: 1px solid black;
}

.vue-grid-item.resizing {
  opacity: 0.9;
}

.vue-grid-item.static {
  background: #cce;
}

.vue-grid-item .text {
  font-size: 24px;
  text-align: center;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  margin: auto;
  height: 100%;
  width: 100%;
}

.vue-grid-item .no-drag {
  height: 100%;
  width: 100%;
}

.vue-grid-item .minMax {
  font-size: 12px;
}

.vue-grid-item .add {
  cursor: pointer;
}

.vue-draggable-handle {
  position: absolute;
  width: 20px;
  height: 20px;
  top: 0;
  left: 0;
  background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'><circle cx='5' cy='5' r='5' fill='#999999'/></svg>")
    no-repeat;
  background-position: bottom right;
  padding: 0 8px 8px 0;
  background-repeat: no-repeat;
  background-origin: content-box;
  box-sizing: border-box;
  cursor: pointer;
}
</style>