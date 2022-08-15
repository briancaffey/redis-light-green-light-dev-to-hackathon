<template>
  <div>
    <Light :red="red" />
    <div class="flex justify-center">
      <pre>{{ id.substring(0,5) }}</pre>
    </div>

    <div  @click="move(socket)" class="bg-amber-200 mx-4 my-4 border-8 border-r-red-500 border-l-white border-y-slate-100 rounded">
      <Player :id="playerNumber.substring(0,3)"/>
    </div>


  </div>
</template>

<script lang="ts">
import { io } from 'socket.io-client';
import { defineComponent } from 'vue';
import { useRoute } from 'vue-router';
import { ref } from 'vue';
import { v4 } from 'uuid';

export default defineComponent({
  setup() {

    let socket = null;
    const red = ref(true);
    const playerNumber = ref('');

    const route = useRoute();

    const id = route.params.id as string;

    const move = (socket) => {
      console.log('move button clicked')
      console.log(socket);
      socket.emit('move', {room: id, player: playerNumber.value});
    }

    return {
      id, playerNumber, move, socket, red
    }
  },
  created: function() {
    this.playerNumber = v4()
    // connect with the `game` namespace
    const socket = io('http://localhost:8000/game');
    this.socket = socket;
    this.socket.on('connect', () => {
      this.status = true
      console.log('joining room');
      this.socket.emit('join', {room: this.id, player: this.playerNumber})
    });

    socket.on('disconnect', () => {
      console.log('disconnected');
    });

    socket.on('update', (data) => {
      console.log('getting update');
      console.log("data is...")
      console.log(data)
    });
  }
})
</script>


