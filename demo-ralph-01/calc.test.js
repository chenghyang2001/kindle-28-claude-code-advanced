import { describe, it, expect } from "vitest";
import { add, subtract, multiply, divide, percent } from "./calc.js";

describe("add", () => {
  it("2 + 3 = 5", () => expect(add(2, 3)).toBe(5));
  it("-1 + 1 = 0", () => expect(add(-1, 1)).toBe(0));
});

describe("subtract", () => {
  it("5 - 3 = 2", () => expect(subtract(5, 3)).toBe(2));
});

describe("multiply", () => {
  it("4 * 3 = 12", () => expect(multiply(4, 3)).toBe(12));
});

describe("divide", () => {
  it("10 / 2 = 5", () => expect(divide(10, 2)).toBe(5));
  it("除以 0 會丟錯", () =>
    expect(() => divide(1, 0)).toThrow("Cannot divide by zero"));
});

describe("percent", () => {
  it("200 的 10% = 20", () => expect(percent(200, 10)).toBe(20));
});
