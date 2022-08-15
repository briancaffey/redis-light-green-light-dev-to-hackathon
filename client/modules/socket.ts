// const API_URL = process.env.API_URL ?? 'http://localhost:8000';
const API_URL = 'http://localhost:8000'
import { io } from 'socket.io-client';

export const useSocketIO = (namespace) => {
  const NS = namespace ?? '';
  const socket = io(`${API_URL}/${NS}`, {autoConnect: false});
  return {
    socket,
  }
}
