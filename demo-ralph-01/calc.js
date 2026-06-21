// 計算機核心函式 — Ralph 練習用空殼
// 一開始所有函式都未實作，calc.test.js 會全部失敗（紅燈）。
// 練習目標：用 Ralph Loop 逐一實作，讓 npm test 全綠。

export function add(a, b) {
  return a + b;
}

export function subtract(a, b) {
  return a - b;
}

export function multiply(a, b) {
  return a * b;
}

export function divide(a, b) {
  if (b === 0) {
    throw new Error("Cannot divide by zero");
  }
  return a / b;
}

export function percent(a, b) {
  return (a * b) / 100;
}
