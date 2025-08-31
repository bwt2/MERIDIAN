import { BrowserRouter, Routes, Route, Navigate } from "react-router";
import { createRoot } from "react-dom/client";
import App from "./pages/App.tsx";
import Call from "./pages/Call.tsx";
import "./styles/global.css";

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/call" element={<Navigate to="/" replace />} />
      <Route path="/call/:callId" element={<Call />} />
    </Routes>
  </BrowserRouter>,
);
