"use client";
import { useEffect, useState } from "react";
import { DragDropContext, Droppable, Draggable, DropResult } from "@hello-pangea/dnd";
import { Task, Status, tasksApi, BOARD_ID } from "@/lib/api";
import TaskCard from "./TaskCard";

const COLUMNS: { id: Status; label: string; color: string }[] = [
  { id: "backlog",     label: "Backlog",     color: "bg-gray-400" },
  { id: "todo",        label: "To Do",       color: "bg-blue-500" },
  { id: "in_progress", label: "In Progress", color: "bg-amber-500" },
  { id: "done",        label: "Done",        color: "bg-emerald-500" },
];

export default function KanbanBoard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTasks = async () => {
    const { data } = await tasksApi.getAll();
    setTasks(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchTasks();
    // Polling каждые 10 секунд — подхватываем задачи от бота
    const interval = setInterval(fetchTasks, 10000);
    return () => clearInterval(interval);
  }, []);

  const onDragEnd = async (result: DropResult) => {
    if (!result.destination) return;
    const taskId = parseInt(result.draggableId);
    const newStatus = result.destination.droppableId as Status;

    // Оптимистичное обновление UI
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
    );
    await tasksApi.move(taskId, newStatus);
  };

  const addTask = async (title: string) => {
    const { data } = await tasksApi.create({ title, status: "todo" });
    setTasks((prev) => [...prev, data]);
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64 text-gray-400">
      Загрузка задач...
    </div>
  );

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="flex gap-4 p-4 overflow-x-auto h-full">
        {COLUMNS.map((col) => {
          const colTasks = tasks.filter((t) => t.status === col.id);
          return (
            <div key={col.id} className="flex flex-col w-52 flex-shrink-0">
              {/* Заголовок колонки */}
              <div className="flex items-center gap-2 mb-3 px-1">
                <span className={`w-2 h-2 rounded-full ${col.color}`} />
                <span className="text-sm font-medium text-gray-600">{col.label}</span>
                <span className="ml-auto text-xs bg-gray-100 text-gray-400 rounded-full px-2 py-0.5">
                  {colTasks.length}
                </span>
              </div>

              {/* Дроппабельная зона */}
              <Droppable droppableId={col.id}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`flex-1 flex flex-col gap-2 p-2 rounded-xl min-h-[200px] transition-colors
                      ${snapshot.isDraggingOver ? "bg-blue-50 border-2 border-blue-200 border-dashed" : "bg-gray-50 border border-gray-200"}`}
                  >
                    {colTasks.map((task, index) => (
                      <Draggable
                        key={task.id}
                        draggableId={String(task.id)}
                        index={index}
                      >
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                          >
                            <TaskCard
                              task={task}
                              isDragging={snapshot.isDragging}
                              onDelete={() =>
                                setTasks((prev) =>
                                  prev.filter((t) => t.id !== task.id)
                                )
                              }
                            />
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>

              {/* Быстрое добавление */}
              {col.id === "todo" && (
                <QuickAdd onAdd={addTask} />
              )}
            </div>
          );
        })}
      </div>
    </DragDropContext>
  );
}

function QuickAdd({ onAdd }: { onAdd: (title: string) => void }) {
  const [open, setOpen] = useState(false);
  const [value, setValue] = useState("");

  const submit = () => {
    if (value.trim()) {
      onAdd(value.trim());
      setValue("");
      setOpen(false);
    }
  };

  if (!open) return (
    <button
      onClick={() => setOpen(true)}
      className="mt-2 text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1 px-2"
    >
      + Добавить задачу
    </button>
  );

  return (
    <div className="mt-2 flex flex-col gap-1">
      <input
        autoFocus
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
        placeholder="Название задачи..."
        className="text-xs p-2 border border-gray-200 rounded-lg outline-none focus:border-blue-400"
      />
      <div className="flex gap-1">
        <button
          onClick={submit}
          className="flex-1 text-xs bg-emerald-500 text-white rounded-lg py-1 hover:bg-emerald-600"
        >
          Добавить
        </button>
        <button
          onClick={() => setOpen(false)}
          className="text-xs text-gray-400 px-2 hover:text-gray-600"
        >
          ✕
        </button>
      </div>
    </div>
  );
}