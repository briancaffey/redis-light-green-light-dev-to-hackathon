<template>
  <div>
    <Title />
    <Header />

    <div class="flex justify-center pt-4">
      <button class="bg-blue-700 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded uppercase font-body" @click="newRoom">new game</button>
    </div>

    <div class="flex justify-center pt-4">
      <nuxt-link class="bg-pink-700 hover:bg-pink-600 text-white font-bold py-2 px-4 rounded uppercase font-body" to="/rooms">
        active games
      </nuxt-link>
    </div>

    <div class="flex justify-center pt-4">
      <nuxt-link class="bg-zinc-700 hover:bg-zinc-600 text-white font-bold py-2 px-4 rounded uppercase font-body" to="/about">
        about
      </nuxt-link>
    </div>

  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  props: {
    room: {
      type: String,
      default: '',
    },
  },
  setup() {

    const router = useRouter()

    const newRoom = async () => {
      console.log('New Room button clicked')
      fetch('http://localhost:8000/api/new', {method: 'POST'})
        .then((response) => response.json())
        .then((data) => {
          router.push(`/room/${data.id}`)
          });
    }

    return {
      newRoom
    }
  }
})
</script>


