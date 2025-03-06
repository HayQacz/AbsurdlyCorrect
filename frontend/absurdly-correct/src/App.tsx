import React from "react"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import HomePage from "./pages/HomePage"
import LobbyPage from "./pages/LobbyPage"
import GamePage from "./pages/GamePage"
import PresentationPage from "./pages/PresentationPage"
import VotingPage from "./pages/VotingPage"
import ResultsPage from "./pages/ResultsPage"
import { GameProvider } from "./context/GameContext"

const App: React.FC = () => {
    return (
        <div className="min-h-screen bg-gradient-to-b from-purple-900 to-indigo-900 text-white">
            <Router>
                <GameProvider>
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/lobby/:gameId" element={<LobbyPage />} />
                        <Route path="/game/:gameId" element={<GamePage />} />
                        <Route path="/presentation/:gameId" element={<PresentationPage />} />
                        <Route path="/voting/:gameId" element={<VotingPage />} />
                        <Route path="/results/:gameId" element={<ResultsPage />} />
                    </Routes>
                </GameProvider>
            </Router>
        </div>
    )
}

export default App
