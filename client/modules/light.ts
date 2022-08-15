import useGameConnection from './gameConnection';
// import { useRoute } from 'vue-router';

import { ref, watch } from 'vue';

export default function useLight() {

  const red = ref(false);
  console.log(red.value);

  const { socket } = useGameConnection();

  console.log(socket);

  socket.socket.on('join', () => {
    console.log('connected in light.ts');
    red.value = true
    console.log(red.value);
  });

  socket.socket.connect();

  console.log(socket);
  socket.socket.on('update-light', () => console.log('got update from backend'));

  // watch(red, (newValue) => {});
  return { red };
}