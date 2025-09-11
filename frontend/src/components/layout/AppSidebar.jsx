"use client"

import React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useSelector } from "react-redux"
import { 
  Home, 
  User, 
  Settings, 
  Shield, 
  Brain,
  BarChart3,
  BookOpen,
  Users,
  Sliders,
  ChevronRight,
  Code,
  Briefcase,
  Target,
  Award,
  FolderOpen,
  GraduationCap
} from "lucide-react"
import { selectCurrentUser } from "@/store/slices/authSlice"
import * as Collapsible from "@radix-ui/react-collapsible"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarRail,
} from "../ui/sidebar"

export function AppSidebar({ ...props }) {
  const user = useSelector(selectCurrentUser)
  const pathname = usePathname()

  // Main navigation sections
  const overviewItems = [
    {
      name: "Dashboard",
      href: "/app/dashboard",
      icon: Home,
      description: "Overview and analytics"
    },
    {
      name: "Profile",
      href: "/app/profile",
      icon: User,
      description: "Manage your account",
      subItems: [
        {
          name: "Overview",
          href: "/app/profile",
          description: "Profile summary"
        },
        {
          name: "Personal Info",
          href: "/app/profile/info",
          description: "Edit details"
        },
        {
          name: "Actions",
          href: "/app/profile/actions",
          description: "Account actions"
        }
      ]
    }
  ]

  const learnItems = [
    {
      name: "Learning",
      href: "/app/learning",
      icon: BookOpen,
      description: "Learning paths and progress"
    },
    {
      name: "Courses",
      href: "/app/courses",
      icon: GraduationCap,
      description: "Browse course catalog"
    },
    {
      name: "Playground",
      href: "/app/playground",
      icon: Code,
      description: "Practice coding online"
    }
  ]

  const growItems = [
    {
      name: "Career",
      href: "/app/career",
      icon: Briefcase,
      description: "Career development hub"
    },
    {
      name: "Projects",
      href: "/app/projects",
      icon: FolderOpen,
      description: "Portfolio showcase"
    },
    {
      name: "Achievements",
      href: "/app/achievements",
      icon: Award,
      description: "Badges and milestones"
    }
  ]

  const connectItems = [
    {
      name: "Community",
      href: "/app/community",
      icon: Users,
      description: "Connect with learners"
    },
    {
      name: "Analytics",
      href: "/app/analytics",
      icon: BarChart3,
      description: "Learning insights"
    }
  ]

  const configItems = [
    {
      name: "Preferences",
      href: "/app/preferences",
      icon: Sliders,
      description: "Learning preferences"
    }
  ]

  const settingsItems = [
    {
      name: "Settings",
      href: "/app/settings",
      icon: Settings,
      description: "Account preferences",
      subItems: [
        {
          name: "General",
          href: "/app/settings",
          description: "Basic settings"
        },
        {
          name: "Security",
          href: "/app/settings/security",
          description: "Password & 2FA"
        },
        {
          name: "Privacy",
          href: "/app/settings/privacy",
          description: "Data settings"
        },
        {
          name: "Account",
          href: "/app/settings/account",
          description: "Account management"
        }
      ]
    }
  ]

  const isActive = (href) => {
    return pathname === href
  }

  const hasActiveChild = (item) => {
    if (!item.subItems) return false
    return item.subItems.some(subItem => isActive(subItem.href))
  }

  const NavItem = ({ item }) => {
    const Icon = item.icon
    const active = isActive(item.href)
    const hasActiveSubItem = hasActiveChild(item)

    if (item.subItems) {
      return (
        <Collapsible.Root defaultOpen={active || hasActiveSubItem}>
          <SidebarMenuItem>
            <Collapsible.Trigger asChild>
              <SidebarMenuButton
                isActive={active}
                className="w-full"
              >
                <Icon className="size-4" />
                <span>{item.name}</span>
                <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]:rotate-90" />
              </SidebarMenuButton>
            </Collapsible.Trigger>
            <Collapsible.Content>
              <SidebarMenuSub>
                {item.subItems.map((subItem) => (
                  <SidebarMenuSubItem key={subItem.href}>
                    <SidebarMenuSubButton asChild isActive={isActive(subItem.href)}>
                      <Link href={subItem.href}>
                        <span>{subItem.name}</span>
                      </Link>
                    </SidebarMenuSubButton>
                  </SidebarMenuSubItem>
                ))}
              </SidebarMenuSub>
            </Collapsible.Content>
          </SidebarMenuItem>
        </Collapsible.Root>
      )
    }

    return (
      <SidebarMenuItem>
        <SidebarMenuButton asChild isActive={active}>
          <Link href={item.href}>
            <Icon className="size-4" />
            <span>{item.name}</span>
          </Link>
        </SidebarMenuButton>
      </SidebarMenuItem>
    )
  }

  return (
    <Sidebar variant="inset" {...props}>
      <SidebarHeader className="border-b border-sidebar-border">
        <div className="flex items-center gap-2 px-2 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-r from-blue-600 to-blue-500">
            <Brain className="h-5 w-5 text-white" />
          </div>
          <div className="grid flex-1 text-left text-sm leading-tight">
            <span className="truncate font-bold text-xl">Gradvy</span>
          </div>
        </div>
        
        {/* User Profile Section */}
        <div className="flex items-center gap-2 px-2 py-2 bg-sidebar-accent rounded-lg">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100">
            <span className="text-sm font-semibold text-blue-700">
              {user?.first_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
            </span>
          </div>
          <div className="grid flex-1 text-left text-sm leading-tight">
            <span className="truncate font-medium">
              {user?.first_name && user?.last_name 
                ? `${user.first_name} ${user.last_name}`
                : user?.email || 'User'}
            </span>
            <span className="truncate text-xs text-sidebar-foreground/70">
              {user?.email}
            </span>
            {user?.is_mfa_enabled && (
              <div className="flex items-center gap-1 mt-1">
                <Shield className="h-3 w-3 text-green-600" />
                <span className="text-xs text-green-600">2FA Active</span>
              </div>
            )}
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        {/* Overview */}
        <SidebarGroup>
          <SidebarGroupLabel>Overview</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {overviewItems.map((item) => (
                <NavItem key={item.href} item={item} />
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Learn */}
        <SidebarGroup>
          <SidebarGroupLabel>Learn</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {learnItems.map((item) => (
                <NavItem key={item.href} item={item} />
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Grow */}
        <SidebarGroup>
          <SidebarGroupLabel>Grow</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {growItems.map((item) => (
                <NavItem key={item.href} item={item} />
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Connect */}
        <SidebarGroup>
          <SidebarGroupLabel>Connect</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {connectItems.map((item) => (
                <NavItem key={item.href} item={item} />
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Configuration */}
        <SidebarGroup>
          <SidebarGroupLabel>Configuration</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {configItems.map((item) => (
                <NavItem key={item.href} item={item} />
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Settings */}
        <SidebarGroup>
          <SidebarGroupLabel>Settings</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {settingsItems.map((item) => (
                <NavItem key={item.href} item={item} />
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border">
        <div className="px-2 py-2 text-center">
          <p className="text-xs text-sidebar-foreground/70">Gradvy v1.0</p>
        </div>
      </SidebarFooter>
      
      <SidebarRail />
    </Sidebar>
  )
}