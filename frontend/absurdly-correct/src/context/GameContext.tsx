import React, {
  createContext,
  useContext,
  useState,
  useRef,
  ReactNode,
} from "react";
import { useNavigate } from "react-router-dom";

// --------------------------------
// Definicje interfejsów (stan gry)
// --------------------------------
interface Player {
  id: string;
  nickname: string;
  score: number;
}

interface WhiteCard {
  id: string;
  content: string;
}

interface BlackCard {
  id: string;
  content: string;
}

interface PlayerAnswer {
  playerId: string;
  nickname: string;
  card: WhiteCard;
}

interface GameSettings {
  cardsPerPlayer: number;
  selectionTime: number;
  votingTime: number;
  maxPlayers: number;
}

interface PlayerScore {
  id: string;
  nickname: string;
  score: number;
}

interface GameState {
  gameId: string | null;
  playerId: string | null;
  nickname: string;
  isHost: boolean;
  players: Player[];
  blackCard: BlackCard | null;
  whiteCards: WhiteCard[];
  playerAnswers: PlayerAnswer[];
  currentRound: number;
  gamePhase: "lobby" | "selection" | "presentation" | "voting" | "results";
  settings: GameSettings;
  currentPresentationIndex: number;
  timeLeft: number;
  winners: PlayerScore[];
  selectedCardId: string | null;
  votedPlayerId: string | null;
  votes: Record<string, number>;
  answersCount?: number;
}

// --------------------------------
// Metody / Kontekst
// --------------------------------
interface GameContextProps {
  gameState: GameState;
  createGame: (nickname: string) => void;
  joinGame: (gameId: string, nickname: string) => void;
  startGame: () => void;
  updateSettings: (settings: Partial<GameSettings>) => void;
  kickPlayer: (playerId: string) => void;
  selectCard: (cardId: string) => void;
  voteForAnswer: (playerId: string) => void;
  restartGame: () => void;
  leaveGame: () => void;
  setNickname: (nickname: string) => void;
}

// --------------------------------
// Stan początkowy
// --------------------------------
const initialState: GameState = {
  gameId: null,
  playerId: null,
  nickname: "",
  isHost: false,
  players: [],
  blackCard: null,
  whiteCards: [],
  playerAnswers: [],
  currentRound: 0,
  gamePhase: "lobby",
  settings: {
    cardsPerPlayer: 5,
    selectionTime: 15,
    votingTime: 60,
    maxPlayers: 10,
  },
  currentPresentationIndex: 0,
  timeLeft: 0,
  winners: [],
  selectedCardId: null,
  votedPlayerId: null,
  votes: {},
};

const GameContext = createContext<GameContextProps | undefined>(undefined);


function hasOwn(obj: unknown, prop: string): boolean {
  return Object.prototype.hasOwnProperty.call(obj, prop);
}

export const GameProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [gameState, setGameState] = useState<GameState>(initialState);
  const navigate = useNavigate();
  const [playerId] = useState(() => crypto.randomUUID().slice(0, 8));
  const wsRef = useRef<WebSocket | null>(null);

  const openWebsocket = (gameId: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const base = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const wsUrl = base.replace(/^http/i, "ws") + `/ws/${gameId}/${playerId}`;
      console.log("Opening WebSocket to", wsUrl);
      const newWs = new WebSocket(wsUrl);
      wsRef.current = newWs;

      newWs.onopen = () => {
        console.log("WS connected:", wsUrl);
        resolve();
      };

      newWs.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleIncomingMessage(data);
        } catch (err) {
          console.error("Failed to parse WS message", err);
        }
      };

      newWs.onerror = (err) => {
        console.error("WebSocket error", err);
        reject(err);
      };

      newWs.onclose = () => {
        console.log("WS closed");
      };
    });
  };

  const handleIncomingMessage = (rawData: unknown) => {
    if (!rawData || typeof rawData !== "object") return;
    const data = rawData as Record<string, unknown>;
    const type = data.type as string | undefined;
    console.log("Got message from server:", data);

    if (type === "game_update") {
      setGameState((prev) => ({
        ...prev,
        gameId: hasOwn(data, "gameId") ? (data.gameId as string) : prev.gameId,
        playerId: hasOwn(data, "playerId") ? (data.playerId as string) : prev.playerId,
        nickname: prev.nickname,
        isHost: hasOwn(data, "isHost") ? (data.isHost as boolean) : false,
        players: hasOwn(data, "players") ? (data.players as Player[]) : prev.players,
        blackCard: hasOwn(data, "blackCard") ? (data.blackCard as BlackCard) : null,
        currentRound: hasOwn(data, "currentRound") ? (data.currentRound as number) : prev.currentRound,
        gamePhase: hasOwn(data, "gamePhase") ? (data.gamePhase as GameState["gamePhase"]) : prev.gamePhase,
        settings: hasOwn(data, "settings") ? (data.settings as GameSettings) : prev.settings,
        playerAnswers: hasOwn(data, "playerAnswers") ? (data.playerAnswers as PlayerAnswer[]) : prev.playerAnswers,
        currentPresentationIndex: hasOwn(data, "currentPresentationIndex")
            ? (data.currentPresentationIndex as number)
            : 0,
        timeLeft: hasOwn(data, "timeLeft") ? (data.timeLeft as number) : 0,
        winners: hasOwn(data, "winners") ? (data.winners as PlayerScore[]) : [],
        whiteCards: hasOwn(data, "whiteCards") ? (data.whiteCards as WhiteCard[]) : [],
        votedPlayerId: hasOwn(data, "votedPlayerId") ? (data.votedPlayerId as string | null) : null,
        votes: hasOwn(data, "votes") ? (data.votes as Record<string, number>) : {},
        answersCount: hasOwn(data, "answersCount") ? (data.answersCount as number) : 0,
        selectedCardId: prev.selectedCardId,
      }));
    } else if (type === "error") {
      const msg = data.message as string;
      alert(msg || "Unknown error");
    } else if (type === "navigate") {
      const route = data.route as string;
      console.log("Navigating to:", route);
      if (route) navigate(route);
    }
  };

  const sendMessage = (payload: Record<string, unknown>) => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.warn("WS not open yet, cannot send message:", payload);
      return;
    }
    console.log("Sending msg to server:", payload);
    ws.send(JSON.stringify(payload));
  };

  const createGame = (nickname: string) => {
    setGameState((prev) => ({ ...prev, nickname }));
    openWebsocket("nogame")
        .then(() => {
          sendMessage({ action: "create_game", nickname });
        })
        .catch((err) => {
          console.error("Failed to open websocket for createGame", err);
        });
  };

  const joinGame = (gameId: string, nickname: string) => {
    setGameState((prev) => ({ ...prev, nickname }));
    openWebsocket(gameId)
        .then(() => {
          sendMessage({ action: "join_game", gameId, nickname });
        })
        .catch((err) => {
          console.error("Failed to open websocket for joinGame", err);
        });
  };

  const startGame = () => {
    if (!gameState.gameId) return;
    sendMessage({ action: "start_game", gameId: gameState.gameId });
  };

  const updateSettings = (settings: Partial<GameSettings>) => {
    if (!gameState.gameId) return;
    setGameState((prev) => ({
      ...prev,
      settings: { ...prev.settings, ...settings },
    }));
    sendMessage({ action: "update_settings", gameId: gameState.gameId, settings });
  };

  const kickPlayer = (playerId: string) => {
    if (!gameState.gameId) return;
    sendMessage({ action: "kick_player", gameId: gameState.gameId, playerId });
  };

  const selectCard = (cardId: string) => {
    if (!gameState.gameId) return;
    setGameState((prev) => ({ ...prev, selectedCardId: cardId }));
    sendMessage({ action: "select_card", gameId: gameState.gameId, cardId });
  };

  const voteForAnswer = (playerId: string) => {
    if (!gameState.gameId) return;
    setGameState((prev) => ({ ...prev, votedPlayerId: playerId }));
    sendMessage({ action: "vote", gameId: gameState.gameId, votedPlayerId: playerId });
  };

  const restartGame = () => {
    if (!gameState.gameId) return;
    sendMessage({ action: "restart_game", gameId: gameState.gameId });
  };

  const leaveGame = () => {
    if (gameState.gameId) {
      sendMessage({ action: "leave_game", gameId: gameState.gameId });
    }
    setGameState(initialState);
    navigate("/");
  };

  const setNickname = (nickname: string) => {
    setGameState((prev) => ({ ...prev, nickname }));
  };

  return (
      <GameContext.Provider
          value={{
            gameState,
            createGame,
            joinGame,
            startGame,
            updateSettings,
            kickPlayer,
            selectCard,
            voteForAnswer,
            restartGame,
            leaveGame,
            setNickname,
          }}
      >
        {children}
      </GameContext.Provider>
  );
};

export const useGame = (): GameContextProps => {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error("useGame must be used within a GameProvider");
  }
  return context;
};
