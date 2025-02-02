import { sendMessage, getChatHistory, sendMessagetoSpecificChat } from "../apis/api";

export const handleInput = (e, setInput, textareaRef) => {
  setInput(e.target.value);
  if (textareaRef.current) {
    textareaRef.current.style.height = "auto";
    textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
  }
};

export const sendMessageHandler = async (e, input, setInput, setMessages, setLoading, uniqueKey, setUniqueKey) => {
  if (e) e.preventDefault();
  if (input.trim() === "") return;
  const userMessage = { sender: "user", text: input };
  setMessages((prevMessages) => [...prevMessages, userMessage]);
  setInput("");
  setLoading(true);
  try {
    let data;
    if (uniqueKey) {
      data = await sendMessagetoSpecificChat(uniqueKey, input);
    } else {
      data = await sendMessage(input);
      setUniqueKey(data.unique_key);
      window.history.pushState(null, '', `/?chat=${data.unique_key}`);
    }
    const botMessage = { sender: "bot", text: data.response };
    setMessages((prevMessages) => [...prevMessages, botMessage]);
  } catch (error) {
    console.error("Error sending message:", error);
  } finally {
    setLoading(false);
  }
};

export const loadChatHistory = async (setUniqueKey, setMessages) => {
  const urlParams = new URLSearchParams(window.location.search);
  const chatKey = urlParams.get('chat');
  if (chatKey) {
    setUniqueKey(chatKey);
    try {
      const history = await getChatHistory(chatKey);
      const formattedMessages = Object.values(history).map(entry => [
        { sender: "user", text: entry.user },
        { sender: "bot", text: entry.gemini }
      ]).flat();
      setMessages(formattedMessages);
    } catch (error) {
      console.error("Error loading chat history:", error);
    }
  }
};
