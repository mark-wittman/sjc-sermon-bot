import { ChatInterface } from "@/components/chat/ChatInterface";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Ask a Question",
  description:
    "Ask questions about the sermons of Saint John's Cathedral and get answers grounded in real preaching.",
};

export default function ChatPage() {
  return <ChatInterface />;
}
