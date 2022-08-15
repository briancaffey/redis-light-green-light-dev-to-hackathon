import { useSocketIO } from './socket';

// import { ref } from 'vue';

export default function useGameConnection() {

  const socket = useSocketIO('game')

  return { socket }

}