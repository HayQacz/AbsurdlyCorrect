import React, { useState } from "react"
import { useParams } from "react-router-dom"
import { useGame } from "../context/GameContext"
import { Button } from "../components/ui/Button"
import { Slider } from "../components/ui/Slider"

const LobbyPage: React.FC = () => {
  const { gameState, startGame, updateSettings, kickPlayer, leaveGame } = useGame()
  const { gameId: _gameId } = useParams<{ gameId: string }>()
  const [showSettings, setShowSettings] = useState(false)

  const handleStartGame = () => {
    startGame()
  }

  const handleKickPlayer = (playerId: string) => {
    kickPlayer(playerId)
  }

  const handleUpdateSettings = (key: keyof typeof gameState.settings, value: number) => {
    updateSettings({ [key]: value })
  }

  const copyGameIdToClipboard = () => {
    if (gameState.gameId) {
      navigator.clipboard.writeText(gameState.gameId)
    }
  }

  return (
      <div className="min-h-screen flex flex-col items-center p-4">
        <div className="bg-gray-800 rounded-lg shadow-lg p-6 w-full max-w-md mb-4">
          <h1 className="text-3xl font-bold text-center mb-6">Game Lobby</h1>

          <div className="flex justify-between items-center mb-4">
            <span className="text-gray-300">Game ID:</span>
            <div className="flex items-center">
              <span className="font-mono mr-2">{gameState.gameId}</span>
              <button onClick={copyGameIdToClipboard} className="text-yellow-400 hover:text-yellow-300">
                {/* Ikonka Copy */}
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                  <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 16H6a2
                     2 0 01-2-2V6a2 2 0 012-2h8a2 2
                     0 012 2v2m-6
                     12h8a2 2 0 002-2v-8a2
                     2 0 00-2-2h-8a2 2 0
                     00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
              </button>
            </div>
          </div>

          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">
              Players ({gameState.players.length}/{gameState.settings.maxPlayers})
            </h2>
            <div className="bg-gray-900 rounded-lg p-3">
              {gameState.players.map((player) => (
                  <div
                      key={player.id}
                      className="flex justify-between items-center py-2 border-b border-gray-700 last:border-0"
                  >
                <span>
                  {player.nickname}{" "}
                  {player.id === gameState.playerId ? "(You)" : ""}{" "}
                  {player.id === gameState.players[0]?.id ? "(Host)" : ""}
                </span>
                    {gameState.isHost && player.id !== gameState.playerId && (
                        <button onClick={() => handleKickPlayer(player.id)} className="text-red-500 hover:text-red-400">
                          {/* Ikonka Kick (X) */}
                          <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-5 w-5"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                  d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                    )}
                  </div>
              ))}
            </div>
          </div>

          {gameState.isHost && (
              <div className="mb-6">
                <div className="flex justify-between items-center mb-2">
                  <h2 className="text-xl font-semibold">Game Settings</h2>
                  <button
                      onClick={() => setShowSettings(!showSettings)}
                      className="text-yellow-400 hover:text-yellow-300"
                  >
                    {showSettings ? "Hide" : "Show"}
                  </button>
                </div>

                {showSettings && (
                    <div className="bg-gray-900 rounded-lg p-4 space-y-4">
                      <div>
                        <label className="block mb-2 text-sm font-medium">
                          Cards per player: {gameState.settings.cardsPerPlayer}
                        </label>
                        <Slider
                            min={3}
                            max={10}
                            value={gameState.settings.cardsPerPlayer}
                            onChange={(value) => handleUpdateSettings("cardsPerPlayer", value)}
                        />
                      </div>

                      <div>
                        <label className="block mb-2 text-sm font-medium">
                          Selection time (seconds): {gameState.settings.selectionTime}
                        </label>
                        <Slider
                            min={10}
                            max={60}
                            value={gameState.settings.selectionTime}
                            onChange={(value) => handleUpdateSettings("selectionTime", value)}
                        />
                      </div>

                      <div>
                        <label className="block mb-2 text-sm font-medium">
                          Voting time (seconds): {gameState.settings.votingTime}
                        </label>
                        <Slider
                            min={30}
                            max={120}
                            value={gameState.settings.votingTime}
                            onChange={(value) => handleUpdateSettings("votingTime", value)}
                        />
                      </div>

                      <div>
                        <label className="block mb-2 text-sm font-medium">
                          Max players: {gameState.settings.maxPlayers}
                        </label>
                        <Slider
                            min={2}
                            max={10}
                            value={gameState.settings.maxPlayers}
                            onChange={(value) => handleUpdateSettings("maxPlayers", value)}
                        />
                      </div>
                    </div>
                )}
              </div>
          )}

          <div className="flex flex-col gap-3">
            {gameState.isHost ? (
                <Button
                    onClick={handleStartGame}
                    disabled={gameState.players.length < 2}
                    className={`py-3 text-lg ${
                        gameState.players.length < 2
                            ? "bg-gray-600 cursor-not-allowed"
                            : "bg-green-600 hover:bg-green-700"
                    }`}
                >
                  {gameState.players.length < 2 ? "Need at Least 2 Players" : "Start Game"}
                </Button>
            ) : (
                <p className="text-center text-gray-300">Waiting for host to start the game...</p>
            )}

            <Button onClick={leaveGame} className="bg-red-600 hover:bg-red-700 py-3 text-lg">
              Leave Game
            </Button>
          </div>
        </div>
      </div>
  )
}

export default LobbyPage
