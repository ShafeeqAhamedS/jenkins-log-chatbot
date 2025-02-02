import { SidebarMenuItem, SidebarMenuButton } from "@/components/ui/sidebar";

const SidebarMenuItems = ({ historyItems }) => {
  return (
    <>
      {historyItems.map((item) => (
        <SidebarMenuItem key={item.title} onClick={() => window.location.href = `?chat=${item.url.split('#/')[1]}`}>
          <SidebarMenuButton asChild>
            <a href={item.url}>
              <item.icon />
              <span>{item.title}</span>
            </a>
          </SidebarMenuButton>
        </SidebarMenuItem>
      ))}
    </>
  );
};

export default SidebarMenuItems;
