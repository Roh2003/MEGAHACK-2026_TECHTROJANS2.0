import axios from "axios";
import { env } from "@/config/env";

export const apiClient = axios.create({
  baseURL: env.authUrl,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});
