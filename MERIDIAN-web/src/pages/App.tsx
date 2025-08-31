import { useRef, useState } from "react";
import { useNavigate } from "react-router";
import Logo from "../assets/MERIDIAN.svg?react";
import { isNumeric } from "../utils";

export default function App() {
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const [isInvalidInput, setIsInvalidInput] = useState<boolean>(false);

  const handleClick = () => {
    const code = inputRef.current?.value || "";
    if (!isNumeric(code)) {
      setIsInvalidInput(true);
      return;
    }
    navigate(`/Call/${encodeURIComponent(code)}`);
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center text-white select-none px-4 md:px-12">
      <span className="flex flex-col sm:flex-row items-center gap-4 m-8 sm:m-16 md:gap-8 md:m-24">
        <Logo className="w-24 h-24 sm:w-32 sm:h-32 md:w-40 md:h-40" />
        <h1 className="text-5xl sm:text-7xl md:text-8xl lg:text-9xl font-extrabold text-center sm:text-left">
          MERIDIAN
        </h1>
      </span>
      <input
        ref={inputRef}
        className="bg-gray-700 text-white placeholder-gray-400 m-4 w-full max-w-xs sm:max-w-[20vw] md:max-w-md h-12 sm:h-16 md:h-20 px-4 sm:px-6 md:px-8 rounded-2xl border-2 border-gray-500 focus:border-white focus:ring-2 outline-none transition text-base sm:text-lg md:text-xl"
        placeholder="Enter code..."
      />
      <button
        onClick={handleClick}
        className="mt-4 w-full max-w-xs sm:max-w-[20vw] md:max-w-md h-12 sm:h-16 md:h-20 flex items-center justify-center bg-gray-700 hover:bg-gray-600 text-white text-lg sm:text-xl md:text-2xl font-semibold rounded-2xl transition border-2 border-gray-500 focus:outline-none focus:border-white focus:ring-2 focus:ring-gray-400"
      >
        Create / Join
      </button>
      <span
        className={`mt-4 text-red-500 text-sm sm:text-base md:text-lg transition-all duration-200 ${
          isInvalidInput ? "visible" : "invisible"
        }`}
      >
        Please enter a valid numeric code.
      </span>
    </div>
  );
}
