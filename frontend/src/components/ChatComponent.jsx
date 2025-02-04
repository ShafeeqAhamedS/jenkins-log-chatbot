import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { sendMessageHandler, handleInput, loadChatHistory } from "../utils/chatUtils";
import ChatMessages from "./ChatMessages";

function ChatComponent() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uniqueKey, setUniqueKey] = useState(null);
  const textareaRef = useRef(null);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    loadChatHistory(setUniqueKey, setMessages);
  }, []);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="p-8 flex flex-col h-[95vh] items-center mx-auto">
      <div ref={chatContainerRef} className="flex-1 w-[90vw] md:w-[60vw] lg:w-[67vw] xl:w-[80vw] overflow-y-auto mt-4">
        <ChatMessages messages={messages} loading={loading} />
      </div>
      <div className="w-[90vw] md:w-[60vw] rounded-3xl flex items-end sticky bottom-0 mt-4 border border-input bg-transparent">
        <Textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => handleInput(e, setInput, textareaRef)}
          className="px-4 py-4 resize-none overflow-x-hidden border-0 max-h-36 focus-visible:ring-transparent"
          onKeyDown={(e) => {
            if (e.key === "Enter" && e.shiftKey) {
              e.preventDefault();
              const { selectionStart, selectionEnd } = e.target;
              const newValue = input.substring(0, selectionStart) + "\n" + input.substring(selectionEnd);
              setInput(newValue);
              textareaRef.current.setSelectionRange(selectionStart + 1, selectionStart + 1);
            } else if (e.key === "Enter" && !loading) {
              sendMessageHandler(e, input, setInput, setMessages, setLoading, uniqueKey, setUniqueKey);
            }
          }}
          placeholder="Shoot your question..."
          disabled={loading}
        />
        <Button 
          onClick={(e) => sendMessageHandler(e, input, setInput, setMessages, setLoading, uniqueKey, setUniqueKey)}
          className="bg-transparent relative bottom-1"
          variant="ghost"
          disabled={loading}
        >
          <Send />
        </Button>
      </div>
    </div>
  );
}

export default ChatComponent;