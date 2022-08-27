<template>
  <div>
    <Title />
    <Header />

    <h1 class="header text-2xl pt-4">Room Events for #{{ id.substring(0,5) }}</h1>

    <div class="pt-4">
      <div class="flex-grow px-4 justify-center" v-if="events">
          <Event v-for="event in allEvents" :event="event" :key="event[0]" />
      </div>
      <div v-else>
          Loading events...
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useRoute } from 'vue-router';
import { ref, computed } from 'vue';


export default defineComponent({
  setup() {

    const events = ref([])

    const route = useRoute();

    const id = route.params.id as string;

    const getEvents = fetch(`http://localhost:8000/api/rooms/${id}/events`)
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
            events.value = data.events
          });
    const allEvents = computed(() => {
      return events.value
    })

    return {
      id, events, getEvents, allEvents
    }
  },
  created: async function() {

    if (process.client) {
      this.getEvents();
    }
  }
})
</script>


