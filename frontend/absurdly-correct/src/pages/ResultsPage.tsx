import React, { useEffect } from "react";
import { useGame } from "../context/GameContext";
import { Button } from "../components/ui/Button";
import confetti from "canvas-confetti";
import { useNavigate } from "react-router-dom";

const ResultsPage: React.FC = () => {
  const { gameState, restartGame, leaveGame } = useGame();
  const navigate = useNavigate();

  useEffect(() => {
    const duration = 3000;
    const end = Date.now() + duration;
    const interval = setInterval(() => {
      const timeLeft = end - Date.now();
      if (timeLeft <= 0) {
        clearInterval(interval);
      }
      confetti({
        particleCount: 50,
        spread: 70,
        origin: { y: 0.6 },
      });
    }, 250);

    return () => clearInterval(interval);
  }, []);

  const handlePlayAgain = () => {
    restartGame();
    navigate(`/lobby/${gameState.gameId}`);
  };

  return (
      <div className="min-h-screen flex flex-col items-center p-4">
        <div className="bg-gray-800 rounded-lg shadow-lg p-6 w-full max-w-md">
          <h1 className="text-3xl font-bold text-center mb-8 text-yellow-400">
            Game Results
          </h1>

          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-center mb-6">Podium</h2>
            <div className="flex justify-center items-end h-64 gap-4">
              {/* Second Place */}
              {gameState.winners[1] && (
                  <div className="flex flex-col items-center">
                    <div className="bg-gray-600 w-24 h-32 flex items-center justify-center rounded-t-lg">
                      <span className="text-4xl font-bold">2</span>
                    </div>
                    <div className="bg-gray-700 w-24 p-2 rounded-b-lg text-center">
                      <p className="font-semibold truncate">
                        {gameState.winners[1].nickname}
                      </p>
                      <p className="text-yellow-400">
                        {gameState.winners[1].score} pts
                      </p>
                    </div>
                  </div>
              )}

              {/* First Place */}
              {gameState.winners[0] && (
                  <div className="flex flex-col items-center">
                    <div className="bg-yellow-600 w-24 h-40 flex items-center justify-center rounded-t-lg">
                      <span className="text-4xl font-bold">1</span>
                    </div>
                    <div className="bg-yellow-700 w-24 p-2 rounded-b-lg text-center">
                      <p className="font-semibold truncate">
                        {gameState.winners[0].nickname}
                      </p>
                      <p className="text-yellow-400">
                        {gameState.winners[0].score} pts
                      </p>
                    </div>
                  </div>
              )}

              {/* Third Place */}
              {gameState.winners[2] && (
                  <div className="flex flex-col items-center">
                    <div className="bg-amber-700 w-24 h-24 flex items-center justify-center rounded-t-lg">
                      <span className="text-4xl font-bold">3</span>
                    </div>
                    <div className="bg-amber-800 w-24 p-2 rounded-b-lg text-center">
                      <p className="font-semibold truncate">
                        {gameState.winners[2].nickname}
                      </p>
                      <p className="text-yellow-400">
                        {gameState.winners[2].score} pts
                      </p>
                    </div>
                  </div>
              )}
            </div>
          </div>

          <div className="flex flex-col gap-3">
            {gameState.isHost && (
                <Button
                    onClick={handlePlayAgain}
                    className="bg-green-600 hover:bg-green-700 py-3 text-lg"
                >
                  Play Again
                </Button>
            )}
            <Button onClick={leaveGame} className="bg-red-600 hover:bg-red-700 py-3 text-lg">
              Leave Game
            </Button>
          </div>
        </div>
      </div>
  );
};

export default ResultsPage;
