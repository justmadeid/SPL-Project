import React, { useEffect } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import "./index.css";
import Layout from "./components/Layout";
import Beranda from "./pages/Beranda";
import Cek from "./pages/Cek";
import Hasil from "./pages/Hasil";
import Aturan from "./pages/Aturan";

function KeAtas() {
  const { pathname, hash } = useLocation();
  useEffect(() => {
    if (hash) setTimeout(() => document.getElementById(hash.slice(1))?.scrollIntoView({ block: "center" }), 400);
    else window.scrollTo(0, 0);
  }, [pathname, hash]);
  return null;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <KeAtas />
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Beranda />} />
          <Route path="cek" element={<Cek />} />
          <Route path="hasil/:id" element={<Hasil />} />
          <Route path="aturan" element={<Aturan />} />
          <Route path="asisten" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
