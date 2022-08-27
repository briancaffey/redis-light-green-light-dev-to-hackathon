<template>
  <div>
    <Title />
    <Header />

    <h1 class="header text-2xl pt-4">Game Archives ({{ roomCount }})</h1>

    <div v-for="room in rooms.reverse()" :key="room[0]">
      <nuxt-link :to="`/archives/room/${room[1].room}`">
        <div class="border-2 border-white rounded p-2 m-2 bg-orange-600 hover:bg-pink-600 header">
            #{{ room[1].room.substring(0,5) }}
            - {{ new Date(room[1].created * 1000).toLocaleDateString() }}
            - {{ new Date(room[1].created * 1000).toLocaleTimeString() }}
        </div>
      </nuxt-link>
    </div>

    <div class="flex justify-center p-2">
    <nuxt-link
      class="bg-blue-700 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded justify-center font-heading"
      to="/"
    >
      Home
    </nuxt-link>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from 'vue'

export default defineComponent({
  setup() {

    const roomList = ref([])
    const roomCount = ref(0)

    const fetchRooms = async () => {
      console.log('Loading rooms')

      fetch('http://localhost:8000/api/archives', {method: 'GET'})
        .then((response) => response.json())
        .then((data) => {
            console.log(data)
            roomList.value = data.rooms
            roomCount.value = data.count
          });
    }

    const rooms = computed(() => {
      return roomList.value
    })

    return {
      rooms,
      fetchRooms,
      roomCount
    }
  },
  created() {
    this.fetchRooms();
  }
})
</script>


