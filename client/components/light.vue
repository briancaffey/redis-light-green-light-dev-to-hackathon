<template>
  <div class="flex justify-center">
    <img :class="redStyle" src="/redis.svg">
    <img :class="greenStyle" src="/green_redis.svg">
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue'

export default defineComponent({
  props: {
    red: {
      type: Boolean,
      default: true,
    }
  },
  setup(props) {
    const baseStyle = "h-24 p-2"
    const redStyle = computed(() => {
      return props.red ? baseStyle : `${baseStyle} grayscale brightness-150`
    });
    const greenStyle = computed(() => {
      return props.red ? `${baseStyle} grayscale brightness-150` : baseStyle
    });

    return {
      redStyle,
      greenStyle,
    }
  },
})
</script>
