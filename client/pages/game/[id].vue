<template>
  <div>
    <Light :red="red" /> {{ red }}
    <!-- <div class="flex justify-center">
      <pre v-if="id">{{ id.substring(0,5) }}</pre>
    </div>

    <div  @click="move(socket)" class="bg-amber-200 mx-4 my-4 border-8 border-r-red-500 border-l-white border-y-slate-100 rounded">
      <Player :id="playerNumber.substring(0,3)"/>
    </div> -->

  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import useLight from '../../modules/light';

export default defineComponent({
  setup() {

    const { red } = useLight();

    return {
      red: red.value,
    }
  }
})
</script>


