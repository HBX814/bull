import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "sonner";
import Home from "@/pages/Home";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
      <Toaster
        position="bottom-right"
        theme="dark"
        toastOptions={{
          style: {
            background: "#0A111A",
            border: "1px solid rgba(255,255,255,0.1)",
            color: "#FFFFFF",
            fontFamily: "Manrope, sans-serif",
            borderRadius: 0,
          },
        }}
      />
    </div>
  );
}

export default App;
