<template>
  <div class="flex noselect uppercase ">
    <div :style="width"> </div>
    <div :class="playerClass"><pre>{{ id.substring(0,3) }}</pre></div>
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
    },
    isCurrentPlayer: {
      type: Boolean,
      default: false
    },
    state: {
      type: String,
      default: 'alive'
    }
  },
  setup(props) {

    const position = computed(() => {
      return props.position;
    });

    const state = computed(() => {
      return props.state;
    })

    const width = computed(() => {
      return `width: ${position.value}%`;
    });

    const playerClass = computed(() => {
      const baseClasses = "p-1 m-2 rounded border-2"
      if (state.value == 'alive') {
        if (props.isCurrentPlayer) {
          return `bg-teal-800	text-white border-white ${baseClasses}`
        } else {
          return `bg-white text-teal-800 border-teal-800 ${baseClasses}`
        }
      } else if (state.value == 'dead') {
        if (props.isCurrentPlayer) {
          return `bg-red-800	text-white border-red ${baseClasses}`
        } else {
          return `bg-white text-red-800 border-red-800 ${baseClasses}`
        }
      }
    });

    return {
      width,
      id: props.id,
      position,
      playerClass
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