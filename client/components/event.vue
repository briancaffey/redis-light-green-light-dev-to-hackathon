<template>

    <!-- created -->
    <div class="event bg-yellow-500" v-if="body.event == 'created'">new game created</div>

    <!-- Red Light Event -->
    <div class="event bg-red-500" v-if="body.event == 'light' && body.light == 'red'">
        {{ body.light }} light
    </div>

    <!-- Green Light Event -->
    <div class="event bg-green-500" v-if="body.event == 'light' && body.light == 'green'">
        {{ body.light }} light
    </div>

    <!-- light -->
    <div class="event bg-teal-800" v-if="body.event == 'move'">
      <span>#{{ body.player.substring(0,3) }} 👟 @ {{ body.pos }}</span>
    </div>

    <div class="event bg-gray-800" v-if="body.event == 'die'">
      #{{ body.player.substring(0,3) }} 💀 @ {{ body.pos }}
    </div>

    <div class="event bg-pink-500" v-if="body.event == 'join'">
      👋 #{{ body.player.substring(0,3) }} joined @ {{ body.pos }}
    </div>

    <div class="event bg-amber-500" v-if="body.event == 'leave'">
      #{{ body.player.substring(0,3) }} left @ {{ body.pos }}
    </div>

    <div class="event bg-zinc-800" v-if="body.event == 'end'">
      GAME ENDED
    </div>


</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  props: {
    event: {
      type: Object,
      default: () => {},
    }
  },
  setup(props) {

    const baseClass = "font-heading noselect border-2 border-teal-800 rounded p-2 m-1";

    return {
      timestamp: props.event[0],
      body: props.event[1]
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