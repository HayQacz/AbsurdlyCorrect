import React from "react";
import { useGame } from "../context/GameContext";
import { Card } from "../components/Card";
import { Motion } from "../components/Motion";

const PresentationPage: React.FC = () => {
  const { gameState } = useGame();

  return (
      <div className="min-h-screen flex flex-col items-center p-4">
        <div className="w-full max-w-lg mb-6">
          <h1 className="text-2xl font-bold text-center mb-6">
            Round {gameState.currentRound + 1} Answers
          </h1>
          {gameState.blackCard && (
              <Card
                  content={gameState.blackCard.content}
                  type="black"
                  className="w-full mb-8"
              />
          )}
          <div className="space-y-4">
            {gameState.playerAnswers.map((answer, index) => (
                <Motion key={index} delay={index * 800}>
                  <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
                    {/* Najpierw cała karta z nagłówkiem */}
                    <div className="mb-4">
                      <p className="text-xl text-yellow-400 font-semibold">
                        {answer.nickname} answered:
                      </p>
                    </div>
                    {/* Po krótkim opóźnieniu pojawia się treść (animacja z dołu) */}
                    <Motion delay={300}>
                      <Card
                          content={answer.card.content}
                          type="white"
                          className="w-full"
                      />
                    </Motion>
                  </div>
                </Motion>
            ))}
          </div>
        </div>
      </div>
  );
};

export default PresentationPage;
