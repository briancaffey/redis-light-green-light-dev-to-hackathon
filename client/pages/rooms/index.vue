<template>
  <div>
    <Title />
    <Header />

    <h1 class="header">Active Rooms</h1>

    <div v-if="rooms" class="m-2 flex flex-wrap">
      <Room v-for="room in rooms" :room="room.room" :key="room.room" />
    </div>

    <div v-else>
      Loading rooms
    </div>

    <div class="flex justify-center p-2">
    <nuxt-link
      class="bg-blue-700 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded justify-center"
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

    const fetchRooms = async () => {
      console.log('Loading rooms')

      fetch('http://localhost:8000/api/rooms?', {method: 'GET'})
        .then((response) => response.json())
        .then((data) => {
            roomList.value = data.rooms
          });
    }

    const rooms = computed(() => {
      return roomList.value
    })

    return {
      rooms,
      fetchRooms
    }
  },
  created() {
    this.fetchRooms();
  }
})
</script>


