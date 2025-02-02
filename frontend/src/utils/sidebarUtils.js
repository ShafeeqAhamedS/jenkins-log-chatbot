import { getChats, searchLogs } from "@/apis/api";

export const shuffleArray = (array) => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

export const handleNewChat = (setNewChat) => {
  window.location.href = "/";
  setNewChat(prev => !prev);
};

export const fetchSearchResults = async (searchTerm, setHistory) => {
  if (searchTerm.trim() === "") {
    getChats()
      .then(data => {
        const sortedData = data.sort((a, b) => b.latest_time - a.latest_time);
        setHistory(sortedData);
      })
      .catch(error => console.error("Error fetching history:", error));
  } else {
    try {
      const results = await searchLogs(searchTerm);
      setHistory(results);
    } catch (error) {
      console.error("Error searching logs:", error);
    }
  }
};
