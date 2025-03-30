import React from "react";
import { useParams } from "react-router-dom";
import { useGame } from "../context/GameContext";
import { Card } from "../components/Card";
import { Timer } from "../components/Timer";

const VotingPage: React.FC = () => {
    const { gameState, voteForAnswer } = useGame();
    const { gameId: _gameId } = useParams<{ gameId: string }>();

    const handleVote = (playerId: string) => {
        if (gameState.votedPlayerId) return;
        voteForAnswer(playerId);
    };

    const votesCount = Object.keys(gameState.votes || {}).length;

    return (
        <div className="min-h-screen flex flex-col p-4 pb-20">
            <div className="flex justify-between items-center mb-4">
                <h1 className="text-2xl font-bold">Vote for Best Answer</h1>
                <Timer time={gameState.timeLeft} />
            </div>

            {gameState.blackCard && (
                <div className="mb-6 max-w-lg mx-auto w-full">
                    <Card
                        content={gameState.blackCard.content}
                        type="black"
                        className="w-full"
                    />
                </div>
            )}

            <h2 className="text-xl font-semibold mb-4 max-w-lg mx-auto w-full">
                Choose the best answer:
            </h2>

            <div className="max-w-lg mx-auto w-full space-y-4 mb-8">
                {gameState.playerAnswers.map((answer) => {
                    const isVoted = gameState.votedPlayerId === answer.playerId;

                    return (
                        <div
                            key={answer.playerId}
                            onClick={() => handleVote(answer.playerId)}
                            className={`bg-gray-800 rounded-lg p-6 shadow-lg transition-all hover:bg-gray-700 cursor-pointer ${
                                isVoted ? "border-2 border-yellow-400" : ""
                            }`}
                        >
                            <p className="text-lg text-yellow-400 mb-2 font-semibold">
                                {answer.nickname}:
                            </p>
                            <Card
                                content={answer.card.content}
                                type="white"
                                className="w-full"
                            />
                        </div>
                    );
                })}
            </div>

            {gameState.votedPlayerId && (
                <div className="text-center text-green-400 font-semibold">
                    Vote submitted! Waiting for other players...
                </div>
            )}

            <div className="fixed bottom-0 left-0 right-0 bg-gray-900 p-4">
                <div className="flex justify-between items-center max-w-lg mx-auto">
                    <div>
                        <span className="font-semibold">Votes Cast:</span>{" "}
                        <span className="text-green-400">
                            {votesCount}/{gameState.players.length}
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

export default VotingPage;
