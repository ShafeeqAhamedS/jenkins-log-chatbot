import { useEffect, useState } from "react";
import { getChats, searchLogs } from "@/apis/api";
import { ModeToggle } from "@/components/mode-toggle";
import { Github, Computer, Activity, Code, SquareTerminal, ServerCrash, DatabaseZap, Cloud, Bot, SquarePlus } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { SidebarHeader } from "./ui/sidebar";
import { Input } from "./ui/input";
import { shuffleArray, handleNewChat, fetchSearchResults } from "../utils/sidebarUtils";
import SidebarMenuItems from "./SidebarMenuItems";

export function AppSidebar() {
  const [history, setHistory] = useState({});
  const [newChat, setNewChat] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    getChats()
      .then(data => {
        const sortedData = data.sort((a, b) => b.latest_time - a.latest_time);
        setHistory(sortedData);
      })
      .catch(error => console.error("Error fetching history:", error));
  }, [newChat]);

  useEffect(() => {
    fetchSearchResults(searchTerm, setHistory);
  }, [searchTerm]);

  const icons = [Github, Computer, Activity, Code, SquareTerminal, ServerCrash, DatabaseZap, Cloud, Bot];
  const shuffledIcons = shuffleArray(icons);

  const historyItems = Object.entries(history).map(([key, value], index) => {
    const Icon = shuffledIcons[index % shuffledIcons.length];
    return {
      title: `${value.job_name} - ${value.build_number}`,
      url: `#/${value.uniqueKey}`,
      icon: Icon,
    };
  });

  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex justify-between">
          <div className="flex items-center px-3">
            <p>Chats</p>
          </div>
          <ModeToggle />
        </div>
        <div className="flex items-center px-3 mt-2">
          <Input
            type="text"
            placeholder=" Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-4 py-4 resize-none overflow-x-hidden focus-visible:ring-transparent"
          />
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>New Chat</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <a onClick={() => handleNewChat(setNewChat)}>
                    <SquarePlus />
                    <span>New Chat</span>
                  </a>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
          <SidebarGroupLabel>Chats</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItems historyItems={historyItems} />
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
