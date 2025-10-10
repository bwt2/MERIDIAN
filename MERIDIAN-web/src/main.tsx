import { BrowserRouter, Routes, Route } from "react-router";
import { createRoot } from "react-dom/client";
import "./styles/global.css";

import Home from "./pages/Home.tsx";
import External from "./pages/External.tsx";
import Internal from "./pages/Internal.tsx";

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/internal" element={<Internal />} />
      <Route path="/external" element={<External />} />
    </Routes>
  </BrowserRouter>,
);
