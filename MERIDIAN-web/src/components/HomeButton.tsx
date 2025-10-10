type HomeButtonProps = {
  handleClick: React.MouseEventHandler;
  text: string;
};

export default function HomeButton({ handleClick, text }: HomeButtonProps) {
  return (
    <button
      onClick={handleClick}
      className="p-4 w-full max-w-xs sm:max-w-[20vw] md:max-w-md h-12 sm:h-16 md:h-20 flex items-center justify-center bg-black hover:bg-gray-600 text-white text-lg sm:text-xl md:text-2xl font-semibold rounded-2xl transition border-2 border-gray-500 focus:outline-none focus:border-white focus:ring-2 focus:ring-gray-400"
    >
      {text}
    </button>
  );
}
