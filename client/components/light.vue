<template>
  <div class="flex justify-center">
    <img :class="redStyle" src="/redis.svg">
    <img :class="greenStyle" src="/green_redis.svg">
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  props: {
    red: {
      type: Boolean,
      default: true,
    }
  },
  setup(props) {
    const baseStyle = "h-24 p-2"
    const redStyle = props.red ? baseStyle : `${baseStyle} grayscale opacity-50`
    const greenStyle = props.red ? `${baseStyle} grayscale opacity-50` : baseStyle

    return {
      redStyle,
      greenStyle,
    }
  },
})
</script>
