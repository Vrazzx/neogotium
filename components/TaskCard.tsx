"use client";
import { Task } from "@/lib/api";

const PRIORITY_COLOR = {
  high:   "bg-red-100 text-red-700",
  medium: "bg-amber-100 text-amber-700",
  low:    "bg-green-100 text-green-700",
};

const TAG_COLOR: Record<string, string> = {
  bug:     "bg-red-50 text-red-600",
  feat:    "bg-blue-50 text-blue-600",
  design:  "bg-purple-50 text-purple-600",
  backend: "bg-green-50 text-green-600",
  ai:      "bg-amber-50 text-amber-600",
};

const AVATAR_COLOR = ["bg-purple-100 text-purple-700", "bg-teal-100 text-teal-700",
  "bg-orange-100 text-orange-700", "bg-blue-100 text-blue-700"];

export default function TaskCard({
  task,
  isDragging,
  onDelete,
}: {
  task: Task;
  isDragging: boolean;
  onDelete: () => void;
}) {
  return (
    <div
      className={`bg-white rounded-lg border p-3 text-left group transition-shadow
        ${isDragging ? "shadow-lg border-blue-300 rotate-1" : "shadow-sm border-gray-200 hover:border-gray-300"}`}
    >
      {/* Приоритет-полоска */}
      <div className={`absolute left-0 top-2 bottom-2 w-0.5 rounded-r-full
        ${task.priority === "high" ? "bg-red-400" : task.priority === "medium" ? "bg-amber-400" : "bg-green-400"}`}
        style={{ position: "relative", width: 3, height: "100%", display: "inline-block", marginBottom: 4 }}
      />

      {/* Заголовок */}
      <div className="text-xs font-medium text-gray-800 leading-snug mb-2">
        {task.title}
      </div>

      {/* Теги и аватар */}
      <div className="flex items-center gap-1 flex-wrap">
        {task.tag && (
          <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${TAG_COLOR[task.tag] || "bg-gray-100 text-gray-600"}`}>
            {task.tag}
          </span>
        )}
        {task.created_by_ai && (
          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-50 text-amber-600 font-semibold">
            AI
          </span>
        )}
        {task.assignee && (
          <span className={`ml-auto text-[10px] w-5 h-5 rounded-full flex items-center justify-center font-medium
            ${AVATAR_COLOR[task.assignee.charCodeAt(0) % AVATAR_COLOR.length]}`}>
            {task.assignee[0].toUpperCase()}
          </span>
        )}
      </div>
    </div>
  );
}