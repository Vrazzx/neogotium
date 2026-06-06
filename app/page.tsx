import KanbanBoard from "@/components/KanbanBoard";

export default function Home() {
  return (
    <main className="flex flex-col h-screen bg-gray-50">
      {/* Шапка */}
      <header className="flex items-center gap-3 px-6 py-3 bg-white border-b border-gray-200">
        <div className="w-2 h-2 rounded-full bg-emerald-500" />
        <h1 className="text-sm font-semibold text-gray-800">AI Project Manager</h1>
        <span className="text-xs bg-amber-50 text-amber-600 px-2 py-0.5 rounded-full font-medium">
          🤖 Groq активен
        </span>
      </header>

      {/* Доска */}
      <div className="flex-1 overflow-hidden">
        <KanbanBoard />
      </div>
    </main>
  );
}