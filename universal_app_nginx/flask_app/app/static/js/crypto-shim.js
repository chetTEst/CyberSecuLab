// crypto-shim.js

// 1) randomBytes(n): возвращает Uint8Array длины n
export function randomBytes(n) {
  const arr = new Uint8Array(n);
  // Web Crypto API: крипто-надёжный генератор
  window.crypto.getRandomValues(arr);
  return arr;
}

// 2) timingSafeEqual(a, b): константное сравнение массивов
export function timingSafeEqual(a, b) {
  if (!(a instanceof Uint8Array && b instanceof Uint8Array)) {
    throw new TypeError("Inputs must be Uint8Array");
  }
  if (a.byteLength !== b.byteLength) return false;
  // Булева аккумуляция без ветвлений — защита от тайминга
  let diff = 0;
  for (let i = 0; i < a.byteLength; i++) {
    diff |= a[i] ^ b[i];
  }
  return diff === 0;
}
