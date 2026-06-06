import { NextRequest, NextResponse } from "next/server";

// На сервере (внутри Docker) используем внутреннее имя "backend",
// локально — localhost
const API_BASE = process.env.API_BASE_URL || "http://localhost:8000";
const BOARD_ID = process.env.BOARD_ID || "default";

export async function GET() {
  try {
    const res = await fetch(`${API_BASE}/api/boards/${BOARD_ID}/tasks/`, {
      cache: "no-store",
    });

    if (!res.ok) {
      const text = await res.text();
      console.error("Backend GET error:", res.status, text);
      return NextResponse.json(
        { error: `Backend responded with ${res.status}` },
        { status: res.status }
      );
    }

    const tasks = await res.json();
    return NextResponse.json(tasks);
  } catch (error: any) {
    console.error("Failed to fetch tasks:", error);
    return NextResponse.json(
      { error: error.message || "Failed to fetch tasks" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const res = await fetch(`${API_BASE}/api/boards/${BOARD_ID}/tasks/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const text = await res.text();
      console.error("Backend POST error:", res.status, text);
      return NextResponse.json(
        { error: `Backend responded with ${res.status}` },
        { status: res.status }
      );
    }

    const task = await res.json();
    return NextResponse.json(task, { status: 201 });
  } catch (error: any) {
    console.error("Failed to create task:", error);
    return NextResponse.json(
      { error: error.message || "Failed to create task" },
      { status: 500 }
    );
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json();
    const { id, ...updates } = body;

    if (!id) {
      return NextResponse.json(
        { error: "Task id is required" },
        { status: 400 }
      );
    }

    const res = await fetch(
      `${API_BASE}/api/boards/${BOARD_ID}/tasks/${id}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      }
    );

    if (!res.ok) {
      const text = await res.text();
      console.error("Backend PATCH error:", res.status, text);
      return NextResponse.json(
        { error: `Backend responded with ${res.status}` },
        { status: res.status }
      );
    }

    const task = await res.json();
    return NextResponse.json(task);
  } catch (error: any) {
    console.error("Failed to update task:", error);
    return NextResponse.json(
      { error: error.message || "Failed to update task" },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get("id");

    if (!id) {
      return NextResponse.json(
        { error: "Task id is required" },
        { status: 400 }
      );
    }

    const res = await fetch(
      `${API_BASE}/api/boards/${BOARD_ID}/tasks/${id}`,
      {
        method: "DELETE",
      }
    );

    if (!res.ok) {
      const text = await res.text();
      console.error("Backend DELETE error:", res.status, text);
      return NextResponse.json(
        { error: `Backend responded with ${res.status}` },
        { status: res.status }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error("Failed to delete task:", error);
    return NextResponse.json(
      { error: error.message || "Failed to delete task" },
      { status: 500 }
    );
  }
}