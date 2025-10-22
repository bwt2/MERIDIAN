import { useNavigate } from "react-router";
import Logo from "../assets/MERIDIAN.svg?react";
import HomeButton from "../components/HomeButton";

export default function Home() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen flex flex-col justify-center items-center text-white select-none px-4 md:px-12">
      <div className="flex-1 flex flex-col justify-center items-center">
        <span className="flex flex-col sm:flex-row items-center gap-4 m-8 sm:m-16 md:gap-8 md:m-12">
          <Logo className="w-24 h-24 sm:w-32 sm:h-32 md:w-40 md:h-40" />
          <h1 className="text-5xl sm:text-7xl md:text-8xl lg:text-9xl font-extrabold text-center sm:text-left">
            MERIDIAN
          </h1>
        </span>
        <main className="flex gap-2 md:gap-25">
          <HomeButton
            handleClick={() => navigate("/external")}
            text="External"
          />
          <HomeButton
            handleClick={() => navigate("/internal")}
            text="Internal"
          />
        </main>
      </div>

      {/* Footer at bottom */}
      <footer className="text-white text-1xl text-center p-4">
        For best user experience: Please enable browser autoplay for audio and
        video!
      </footer>
    </div>
  );
}
