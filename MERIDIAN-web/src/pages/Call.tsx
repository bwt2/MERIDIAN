import { useEffect } from "react";
import { useParams, useNavigate } from "react-router";
import { isNumeric } from "../utils";

export default function Call() {
  const navigate = useNavigate();
  const { callId } = useParams();
  useEffect(() => {
    if (!callId || !isNumeric(callId)) {
      navigate("/", { replace: true });
    }
  }, [callId, navigate]);

  return (
    <div className="min-h-screen flex flex-col justify-center items-center text-white select-none">
      {callId}
    </div>
  );
}
