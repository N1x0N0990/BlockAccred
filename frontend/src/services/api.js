import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || (window.location.hostname === "localhost" ? "http://localhost:8000" : window.location.origin.replace(/:\d+$/, ""));

export const api = axios.create({ baseURL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("blockaccred_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.detail || err.message || "Something went wrong";
    return Promise.reject(new Error(typeof message === "string" ? message : JSON.stringify(message)));
  }
);
