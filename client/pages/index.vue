<template>
  <div>
    <Header />

    <div class="flex justify-center pt-4">
      <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" @click="newRoom">Start a new game</button>
    </div>

    <div class="flex justify-center pt-4">
      <nuxt-link class="bg-zinc-500 hover:bg-zinc-700 text-white font-bold py-2 px-4 rounded" to="/about">
        About
      </nuxt-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  setup() {

    const router = useRouter()

    const newRoom = async () => {
      console.log('New Room button clicked')
      fetch('http://localhost:8000/new', {method: 'POST'})
        .then((response) => response.json())
        .then((data) => {
          router.push(`/game/${data.id}`)
          });

      // console.log(id);



    }

    return {
      newRoom
    }
  },
})
</script>


