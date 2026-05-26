/** 全局 z-index 计数器，供跨模块 GuaCiFloat 实例共用 */
let counter = 100
export function nextZIndex() { return ++counter }
