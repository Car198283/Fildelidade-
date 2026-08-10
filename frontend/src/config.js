// API Configuration
const API_URL =
  import.meta.env.VITE_API_URL ||
  `${window.location.protocol}//${window.location.hostname}:8000`;

export const PUBLIC_APP_URL = import.meta.env.VITE_PUBLIC_APP_URL || "";

export default API_URL;
