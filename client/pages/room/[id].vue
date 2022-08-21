<template>
  <div>
    <h1 class="text-white p-2 text-2xl text-center font-bold"><pre>Redis Light, Green Light</pre></h1>
    <Light :red="red" />
    <div class="flex justify-center">
      <pre class="text-white">{{ id.substring(0,5) }}</pre>
      <div>
        <pre class="text-white"> - {{ playerNumber.substring(0, 3) }}</pre>
      </div>
    </div>

    <details class="text-white p-2">
    <div class="text-white">
      <summary class="text-white"><pre>Players:</pre></summary>
      <pre>{{ players }}</pre>

    </div>
    </details>

    <div
      @click="move(socket)"
      class="bg-amber-200 mx-4 my-4 border-8 border-r-red-500 border-l-white border-y-slate-100 rounded"
    >
      <Player
        v-for="player in players"
        :id="player.player"
        :position="player.pos"
        :key="player.player"
        :is-current-player="player.player == playerNumber"
        :state="player.state"
      />
    </div>
    <div class="flex justify-center">
      <button
        class="text-white border-2 border-white rounded p-2 hover:bg-gray-800"
        @click.prevent="leave(socket)">
        Leave Game
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { io } from 'socket.io-client';
import { defineComponent } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ref } from 'vue';
import { v4 } from 'uuid';

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
    const players = ref<PlayerType[]>([])

    const route = useRoute();
    const router = useRouter();

    const id = route.params.id as string;

    const move = (socket) => {
      socket.emit('move', {room: id, player: playerNumber.value});
    }

    const leave = (socket) => {
      socket.emit('leave', {room: id, player: playerNumber.value});
      console.log('You have been disconnected from the game')
      router.push('/')
    }

    return {
      id, playerNumber, move, socket, red, players, leave
    }
  },
  created: async function() {

    if (process.client) {

      if (!localStorage.getItem('playerNumber')) {
        // TODO: get playerNumber from session
        localStorage.setItem('playerNumber', v4());
        this.playerNumber = v4();
      } else {
        this.playerNumber = localStorage.getItem('playerNumber');
      }



      // connect with the `game` namespace
      const socket = io('http://localhost:8000/game');
      this.socket = socket;
      this.socket.once('connect', () => {
        this.status = true
        console.log('joining room with id ' + this.id);
        this.socket.emit('join', {room: this.id, player: this.playerNumber})
      });

      socket.on('update', (data) => {
        this.players = data.positions;
      });

      socket.on('update_light', (message) => {
        this.red = message.state === 'red' ? true : false;
      });
    }
  }
})
</script>


