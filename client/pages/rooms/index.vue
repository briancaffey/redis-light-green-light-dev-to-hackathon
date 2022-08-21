<template>
  <div>
    <Header />

    <div class="m-2 flex">
      <Room v-for="room in rooms" :room="room" :key="room" />
    </div>

    <div class="flex justify-center p-2">
      <button class="bg-blue-700 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded" @click="fetchRooms">More</button>
    </div>

    <div class="flex justify-center p-2">
    <nuxt-link class="bg-blue-700 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded justify-center" to="/">Home
    </nuxt-link>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  setup() {

    const roomList = ref([])
    const cursor = ref(0)

    const router = useRouter()

    const fetchRooms = async () => {
      console.log('Loading rooms')
      const params = new URLSearchParams({
        cursor: String(cursor.value)
      });
      fetch('http://localhost:8000/api/rooms?' + params, {method: 'GET'})
        .then((response) => response.json())
        .then((data) => {
            roomList.value = data.rooms
            cursor.value = data.cursor
          });
    }

    const rooms = computed(() => {
      return roomList.value
    })

    return {
      rooms,
      fetchRooms,
      cursor
    }
  },
  created() {
    this.fetchRooms();
  }
})
</script>


