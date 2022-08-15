<template>
  <div class="flex">
    <div :style="width"> </div>
    <div class="bg-teal-800	text-white p-1 m-2 rounded"><pre>{{ id }}</pre></div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  props: {
    id: {
      type: String,
      default: '000',
    },
    position: {
      type: Number,
      default: 0,
    }
  },
  setup(props) {

    return {
      width: `width: ${props.position}%`,
      id: props.id,
      position: props.position,
    }
  },
})
</script>
