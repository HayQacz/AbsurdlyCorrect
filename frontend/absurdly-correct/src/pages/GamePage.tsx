import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useGame } from "../context/GameContext";
import { Card } from "../components/Card";
import { Timer } from "../components/Timer";

const GamePage: React.FC = () => {
    const { gameState, selectCard } = useGame();
    const { gameId: _gameId } = useParams<{ gameId: string }>();
    const [selectedCard, setSelectedCard] = useState<string | null>(null);

    useEffect(() => {
        setSelectedCard(null);
    }, [gameState.currentRound]);

    const handleSelectCard = (cardId: string) => {
        if (selectedCard || !gameState.timeLeft) return;
        setSelectedCard(cardId);
        selectCard(cardId);
    };

    return (
        <div className="min-h-screen flex flex-col p-4 pb-20">
            <div className="flex justify-between items-center mb-4">
                <h1 className="text-2xl font-bold">Round {gameState.currentRound + 1}</h1>
                <Timer time={gameState.timeLeft} />
            </div>

            {gameState.blackCard && (
                <div className="mb-6">
                    <Card
                        content={gameState.blackCard.content}
                        type="black"
                        className="w-full max-w-lg mx-auto"
                    />
                </div>
            )}

            <h2 className="text-xl font-semibold mb-3">Your Cards</h2>
            <p className="text-gray-300 mb-4">Select a card to answer the question</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-8">
                {gameState.whiteCards.map((card) => (
                    <Card
                        key={card.id}
                        content={card.content}
                        type="white"
                        onClick={() => handleSelectCard(card.id)}
                        selected={selectedCard === card.id}
                        disabled={!!selectedCard || !gameState.timeLeft}
                        className="cursor-pointer transform transition-transform hover:scale-105"
                    />
                ))}
            </div>

            {selectedCard && (
                <div className="text-center text-green-400 font-semibold">
                    Card selected! Waiting for other players...
                </div>
            )}

            <div className="fixed bottom-0 left-0 right-0 bg-gray-900 p-4">
                <div className="flex justify-between items-center max-w-lg mx-auto">
                    <div>
                        <span className="font-semibold">Players Ready:</span>{" "}
                        <span className="text-green-400">
                            {gameState.answersCount !== undefined ? gameState.answersCount : gameState.playerAnswers.length}/{gameState.players.length}
                        </span>
                    </div>
                    <div className="flex items-center">
                        <span className="mr-2">Time Left:</span>
                        <Timer time={gameState.timeLeft} compact />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default GamePage;
