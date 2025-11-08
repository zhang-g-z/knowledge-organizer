// 简单的 WebSocket 管理器，连接到 /api/ws 并触发回调
export default function createWS(onMessage) {
  const ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/api/ws');
  ws.onopen = () => {
    console.log('ws opened');
  };
  ws.onmessage = (evt) => {
    try {
      const data = JSON.parse(evt.data);
      onMessage && onMessage(data);
    } catch(e) {
      console.warn('invalid ws message', evt.data);
    }
  };
  ws.onclose = () => console.log('ws closed');
  ws.onerror = (e) => console.error('ws error', e);
  return ws;
}