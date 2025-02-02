const ChatMessages = ({ messages, loading }) => {
  return (
    <>
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`message ${
            msg.sender === "user"
              ? "self-end bg-gray-200 text-black  rounded-full max-w-[30vw] w-max ml-auto text-right"
              : "self-start w-1/2 mr-auto text-left"
          } rounded-lg p-2 m-2`}
        >
          <p className="whitespace-pre-wrap">{msg.text}</p>
        </div>
      ))}
      {loading && (
        <div className="self-start rounded-full max-w-[30%] mr-auto p-2 m-2">
          <div className="flex space-x-1">
            <span className="animate-bounce" style={{ animationDelay: "0s" }}>^</span>
            <span className="animate-bounce" style={{ animationDelay: "0.2s" }}>v</span>
            <span className="animate-bounce" style={{ animationDelay: "0.4s" }}>^</span>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatMessages;
