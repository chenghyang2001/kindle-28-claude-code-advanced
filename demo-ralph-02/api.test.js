import { describe, it, expect, beforeEach } from "vitest";
import {
  createTodo,
  listTodos,
  getTodo,
  updateTodo,
  deleteTodo,
} from "./api.js";

let store;
beforeEach(() => {
  store = { todos: [], nextId: 1 };
});

describe("createTodo", () => {
  it("建立成功回 201 與新 todo", () => {
    const res = createTodo(store, { title: "買牛奶" });
    expect(res.status).toBe(201);
    expect(res.body).toEqual({ id: 1, title: "買牛奶", done: false });
    expect(store.todos).toHaveLength(1);
    expect(store.nextId).toBe(2);
  });
  it("title 為空回 400", () => {
    const res = createTodo(store, { title: "" });
    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: "title required" });
  });
});

describe("listTodos", () => {
  it("回 200 與所有 todos", () => {
    createTodo(store, { title: "a" });
    createTodo(store, { title: "b" });
    const res = listTodos(store);
    expect(res.status).toBe(200);
    expect(res.body).toHaveLength(2);
  });
});

describe("getTodo", () => {
  it("找到回 200", () => {
    createTodo(store, { title: "a" });
    const res = getTodo(store, 1);
    expect(res.status).toBe(200);
    expect(res.body.title).toBe("a");
  });
  it("找不到回 404", () => {
    const res = getTodo(store, 999);
    expect(res.status).toBe(404);
    expect(res.body).toEqual({ error: "not found" });
  });
});

describe("updateTodo", () => {
  it("更新 done 回 200", () => {
    createTodo(store, { title: "a" });
    const res = updateTodo(store, 1, { done: true });
    expect(res.status).toBe(200);
    expect(res.body.done).toBe(true);
  });
  it("找不到回 404", () => {
    const res = updateTodo(store, 999, { done: true });
    expect(res.status).toBe(404);
  });
});

describe("deleteTodo", () => {
  it("刪除回 200 並移除", () => {
    createTodo(store, { title: "a" });
    const res = deleteTodo(store, 1);
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ deleted: true });
    expect(store.todos).toHaveLength(0);
  });
  it("找不到回 404", () => {
    const res = deleteTodo(store, 999);
    expect(res.status).toBe(404);
  });
});
