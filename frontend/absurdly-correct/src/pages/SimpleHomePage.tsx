import React from "react"

const SimpleHomePage: React.FC = () => {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-4">
            <div className="bg-gray-800 rounded-lg shadow-lg p-6 w-full max-w-md">
                <h1 className="text-4xl font-bold text-center mb-8 text-yellow-400">Absurdly Correct</h1>
                <div className="flex flex-col gap-4">
                    <button className="bg-purple-600 hover:bg-purple-700 text-white py-3 text-lg rounded-lg">
                        Host a Game
                    </button>
                    <button className="bg-indigo-600 hover:bg-indigo-700 text-white py-3 text-lg rounded-lg">
                        Join a Game
                    </button>
                </div>
            </div>
        </div>
    )
}

export default SimpleHomePage
