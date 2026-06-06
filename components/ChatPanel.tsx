"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import axios from "axios";

interface Task {
  id: string;
  title: string;
  status: string;
  priority?: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  tasks?: Task[];
}

interface ChatPanelProps {
  onTaskCreated?: () => void;
}

export default function ChatPanel({ onTaskCreated }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const API_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const sendMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmed,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Сбрасываем высоту textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    try {
      const response = await axios.post(`${API_URL}/api/chat/`, {
        message: trimmed,
      });

      const data = response.data;

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content:
          data.reply ||
          data.message ||
          (data.tasks?.length
            ? `Создано задач: ${data.tasks.length}`
            : "Готово!"),
        tasks: data.tasks,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Обновляем канбан-доску, если создались задачи
      if (data.tasks?.length && onTaskCreated) {
        onTaskCreated();
      }
    } catch (error: any) {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `❌ Ошибка: ${
          error.response?.data?.detail ||
          error.message ||
          "Не удалось обработать сообщение"
        }`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleTextareaChange = (
    e: React.ChangeEvent<HTMLTextAreaElement>
  ) => {
    setInput(e.target.value);
    // Автоматическая высота
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  const statusColors: Record<string, string> = {
    TODO: "bg-gray-100 text-gray-700",
    IN_PROGRESS: "bg-blue-100 text-blue-700",
    IN_REVIEW: "bg-yellow-100 text-yellow-700",
    DONE: "bg-green-100 text-green-700",
  };

  return (
    <div className="flex flex-col h-full bg-white border-l border-gray-200 w-96">
      {/* Заголовок */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <span className="text-2xl">🤖</span>
          AI Ассистент
        </h2>
        <p className="text-sm text-gray-500 mt-0.5">
          Опишите задачу — я создам её на доске
        </p>
      </div>

      {/* Сообщения */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-10 px-4">
            <div className="text-5xl mb-4">🤖</div>
            <p className="text-lg font-medium text-gray-500">
              Привет! Я ваш AI-помощник
            </p>
            <p className="text-sm mt-2 leading-relaxed">
              Напишите, что нужно сделать, например:
            </p>
            <div className="mt-4 space-y-2 text-left">
              {[
                "Создай задачу: настроить CI/CD, приоритет высокий",
                "Добавить задачу: написать тесты для API",
                "Новая задача: дизайн страницы логина",
              ].map((example, i) => (
                <button
                  key={i}
                  onClick={() => setInput(example)}
                  className="w-full text-left text-sm bg-gray-50 hover:bg-gray-100 rounded-lg px-3 py-2 text-gray-600 transition-colors"
                >
                  &ldquo;{example}&rdquo;
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
                msg.role === "user"
                  ? "bg-blue-600 text-white rounded-br-sm"
                  : "bg-gray-100 text-gray-800 rounded-bl-sm"
              }`}
            >
              <p className="whitespace-pre-wrap text-sm leading-relaxed">
                {msg.content}
              </p>

              {/* Список созданных задач */}
              {msg.tasks && msg.tasks.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200/40 space-y-1.5">
                  <p className="text-xs font-medium opacity-70">
                    Создано задач: {msg.tasks.length}
                  </p>
                  {msg.tasks.map((task, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-2 text-xs bg-white/50 rounded-md px-2 py-1"
                    >
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                          statusColors[task.status] || "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {task.status}
                      </span>
                      <span className="truncate">{task.title}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3">
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Поле ввода */}
      <div className="p-3 border-t border-gray-200 bg-gray-50">
        <div className="flex gap-2 items-end">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder="Опишите задачу..."
            className="flex-1 resize-none rounded-xl border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="flex-shrink-0 rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            ➤
          </button>
        </div>
        <p className="text-[11px] text-gray-400 mt-1.5 px-1">
          Enter — отправить, Shift+Enter — новая строка
        </p>
      </div>
    </div>
  );
}