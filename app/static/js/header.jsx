// static/js/header.jsx
import React from "react";
import { Link } from "react-router-dom";
import ThemeToggle from "../constants/ThemeToggle.jsx";

function Header({ headerRef }) {
  return (
    <div
      ref={headerRef}
      className="w-full flex items-center justify-between shadow-sm p-3 md:px-40 border-b"
    >
      <Link to="/">
        <div className="logo flex gap-2 items-center justify-between">
          <div className="img inline-block h-5 w-5 md:h-10 md:w-10">
            <img src="/logo.png" alt="Logo" />
          </div>
          <h1 className="text-lg md:text-3xl font-bold bg-gradient-to-b from-blue-400 to-blue-700 bg-clip-text text-transparent">
            Pocket Traveller
          </h1>
        </div>
      </Link>
      <div className="flex items-center">
        <ThemeToggle />
      </div>
    </div>
  );
}

export default Header;
