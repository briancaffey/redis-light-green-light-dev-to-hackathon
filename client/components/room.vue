<template>
  <nuxt-link
    class="text-white rounded border-2 border-white p-2 m-2 hover:bg-blue-700"
    :to="link"
  >
    <pre class="uppercase">{{ room.substring(0,5) }}</pre>
  </nuxt-link>
</template>

<script>
import { defineComponent, ref } from 'vue'

export default defineComponent({
  props: {
    room: {
      type: String,
      default: '',
    }
  },
  setup(props) {
    const room = ref('');

    room.value = props.room;
    const link = `/room/${room.value}`;

    return {
      room,
      link
    }
  },
})
</script>
