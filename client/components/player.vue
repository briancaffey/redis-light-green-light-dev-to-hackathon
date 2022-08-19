<template>
  <div class="flex noselect">
    <div :style="width"> </div>
    <div class="bg-teal-800	text-white p-1 m-2 rounded"><pre>{{ id.substring(0,3) }}</pre></div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue'

export default defineComponent({
  props: {
    id: {
      type: String,
      default: '000',
    },
    position: {
      type: String,
      default: 0,
    }
  },
  setup(props) {

    const position = computed(() => {
      return props.position;
    });

    const width = computed(() => {
      return `width: ${position.value * 10}px`;
    });

    return {
      width,
      id: props.id,
      position,
    }
  },
})
</script>

<style scoped>
.noselect {
  cursor: pointer;
  -webkit-touch-callout: none; /* iOS Safari */
    -webkit-user-select: none; /* Safari */
     -khtml-user-select: none; /* Konqueror HTML */
       -moz-user-select: none; /* Old versions of Firefox */
        -ms-user-select: none; /* Internet Explorer/Edge */
            user-select: none; /* Non-prefixed version, currently
                                  supported by Chrome, Edge, Opera and Firefox */
}
</style>