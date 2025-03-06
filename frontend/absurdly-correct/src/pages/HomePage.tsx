import React, { useState } from "react"
import { useGame } from "../context/GameContext"
import { Button } from "../components/ui/Button"
import { Input } from "../components/ui/Input"

const HomePage: React.FC = () => {
  const { createGame, joinGame, setNickname } = useGame()
  const [mode, setMode] = useState<"home" | "create" | "join">("home")
  const [nickname, setNicknameState] = useState("")
  const [gameId, setGameId] = useState("")
  const [error, setError] = useState("")

  const handleCreateGame = () => {
    if (!nickname.trim()) {
      setError("Please enter a nickname")
      return
    }
    setNickname(nickname)
    createGame(nickname)
  }

  const handleJoinGame = () => {
    if (!nickname.trim()) {
      setError("Please enter a nickname")
      return
    }
    if (!gameId.trim()) {
      setError("Please enter a game ID")
      return
    }
    setNickname(nickname)
    joinGame(gameId, nickname)
  }

  return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <div className="bg-gray-800 rounded-lg shadow-lg p-6 w-full max-w-md">
          <h1 className="text-4xl font-bold text-center mb-8 text-yellow-400">Absurdly Correct</h1>

          {mode === "home" && (
              <div className="flex flex-col gap-4">
                <Button
                    onClick={() => setMode("create")}
                    className="bg-purple-600 hover:bg-purple-700 text-white py-3 text-lg"
                >
                  Host a Game
                </Button>
                <Button
                    onClick={() => setMode("join")}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white py-3 text-lg"
                >
                  Join a Game
                </Button>
              </div>
          )}

          {mode === "create" && (
              <div className="flex flex-col gap-4">
                <h2 className="text-2xl font-semibold text-center mb-4">Host a New Game</h2>
                <Input
                    type="text"
                    placeholder="Your Nickname"
                    value={nickname}
                    onChange={(e) => setNicknameState(e.target.value)}
                    className="py-3 text-lg"
                />
                {error && <p className="text-red-500 text-center">{error}</p>}
                <Button
                    onClick={handleCreateGame}
                    className="bg-purple-600 hover:bg-purple-700 text-white py-3 text-lg"
                >
                  Create Game
                </Button>
                <Button
                    onClick={() => setMode("home")}
                    className="bg-gray-600 hover:bg-gray-700 text-white py-3 text-lg"
                >
                  Back
                </Button>
              </div>
          )}

          {mode === "join" && (
              <div className="flex flex-col gap-4">
                <h2 className="text-2xl font-semibold text-center mb-4">Join an Existing Game</h2>
                <Input
                    type="text"
                    placeholder="Your Nickname"
                    value={nickname}
                    onChange={(e) => setNicknameState(e.target.value)}
                    className="py-3 text-lg"
                />
                <Input
                    type="text"
                    placeholder="Game ID"
                    value={gameId}
                    onChange={(e) => setGameId(e.target.value)}
                    className="py-3 text-lg"
                />
                {error && <p className="text-red-500 text-center">{error}</p>}
                <Button
                    onClick={handleJoinGame}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white py-3 text-lg"
                >
                  Join Game
                </Button>
                <Button
                    onClick={() => setMode("home")}
                    className="bg-gray-600 hover:bg-gray-700 text-white py-3 text-lg"
                >
                  Back
                </Button>
              </div>
          )}
        </div>
      </div>
  )
}

export default HomePage
