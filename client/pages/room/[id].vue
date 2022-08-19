<template>
  <div>
    <Light :red="red" />
    <div class="flex justify-center">
      <pre class="text-white">{{ id.substring(0,5) }}</pre>
      <div>
        <pre class="text-white"> - {{ playerNumber.substring(0, 3) }} - {{ playerPosition }}</pre>
      </div>
    </div>

    <details class="text-white">
    <div class="text-white">
      <summary class="text-white"><pre>Players:</pre></summary>
      <pre>{{ players }}</pre>

    </div>
    </details>

    <div  @click="move(socket)" class="bg-amber-200 mx-4 my-4 border-8 border-r-red-500 border-l-white border-y-slate-100 rounded">
      <Player
        v-for="player in players"
        :id="player.player"
        :position="player.pos"
        :key="player.player"
        />
    </div>
  </div>
</template>

<script lang="ts">
import { io } from 'socket.io-client';
import { defineComponent } from 'vue';
import { useRoute } from 'vue-router';
import { ref } from 'vue';

export interface PlayerType {
  pos: string;
  state: string;
  player: string;
}

export default defineComponent({
  setup() {

    let socket = null;
    const red = ref(true);
    const playerNumber = ref('');
    const playerPosition = ref(0);
    const players = ref<PlayerType[]>([])

    const route = useRoute();

    const id = route.params.id as string;

    const move = (socket) => {
      console.log('move button clicked')
      console.log(socket);
      socket.emit('move', {room: id, player: playerNumber.value});
    }

    return {
      id, playerNumber, move, socket, red, playerPosition, players
    }
  },
  created: async function() {
    await fetch(
      'http://localhost:8000/api/session', {
        method: 'POST'
      })
      .then((res) =>  res.json())
      .then((data) => {
        console.log(data)
        this.playerNumber = data.playerNumber;
      })
      .catch((err) => {
        console.log(err);
      });

    // connect with the `game` namespace
    const socket = io('http://localhost:8000/game');
    this.socket = socket;
    this.socket.on('connect', () => {
      this.status = true
      console.log('joining room with id ' + this.id);
      this.socket.emit('join', {room: this.id, player: this.playerNumber})
    });

    socket.on('disconnect', () => {
      console.log('disconnected');
    });

    socket.on('update', (data) => {
      console.log("updating....")
      console.log(data)
      this.players = data.positions;
      // this.incrementPlayerPosition();
    });

    socket.on('update_light', (message) => {
      console.log('updating light');
      console.log(message);
      this.red = message.state === 'red' ? true : false;
    });
  }
})
</script>


