import { BrowserRouter, Routes, Route } from "react-router";
import { createRoot } from "react-dom/client";
import App from "./pages/App.tsx";
import Client from "./pages/Client.tsx";
import "./styles/global.css";

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/client/:clientId" element={<Client />} />
    </Routes>
  </BrowserRouter>,
);
