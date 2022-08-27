<template>
  <div>
    <Title />
    <Light :red="red" />
    <div class="flex justify-center">
      <div @click="copyLink">
        <pre class="p-1 m-2 rounded border-2	text-teal-800 border-teal-800 bg-white uppercase cursor-pointer">game #{{ id.substring(0,5) }} 🔗</pre>
      </div>
      <div>
        <pre class="p-1 m-2 rounded border-2 bg-teal-800	text-white border-white uppercase cursor-pointer">player #{{ playerNumber.substring(0, 3) }}</pre>
      </div>
    </div>
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
        class="text-white border-2 border-white rounded p-2 hover:bg-gray-800 font-body m-2"
        @click.prevent="leave(socket)">
        Leave Game
      </button>
      <nuxt-link class="text-white border-2 border-white rounded p-2 hover:bg-gray-800 font-body m-2" :to="'/archives/' + id">Event Stream</nuxt-link>
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

    const copyLink = () => {
      navigator.clipboard.writeText(window.location.href);
      alert("Game Link Copied to Clipboard")
    }

    return {
      id, playerNumber, move, socket, red, players, leave, copyLink
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


