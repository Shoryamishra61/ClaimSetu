import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import { LangProvider } from "./i18n/LangProvider";
import "./styles.css";

const root = document.getElementById("root");
if (!root) throw new Error("Missing #root mount point");

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <LangProvider>
      <App />
    </LangProvider>
  </React.StrictMode>,
);
