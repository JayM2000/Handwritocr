"use client";

import React, { useCallback } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAppSelector, useAppDispatch } from "@/store/hooks";
import { toggleNav, closeNav } from "@/store/slices/uiSlice";
import { Menu, X, PenLine } from "lucide-react";

const NAV_LINKS = [
  { href: "/", label: "Home" },
  { href: "/generate", label: "Generate" },
];

function NavbarInner() {
  const pathname = usePathname();
  const dispatch = useAppDispatch();
  const isNavOpen = useAppSelector((state) => state.ui.isNavOpen);

  const handleToggle = useCallback(() => {
    dispatch(toggleNav());
  }, [dispatch]);

  const handleClose = useCallback(() => {
    dispatch(closeNav());
  }, [dispatch]);

  return (
    <nav
      className={cn(
        "fixed top-0 left-0 right-0 z-50",
        "glass-strong",
        "border-b border-white/[0.06]"
      )}
    >
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link
            href="/"
            className="flex items-center gap-2 group"
            onClick={handleClose}
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/[0.08] border border-white/[0.12] transition-all duration-300 group-hover:bg-white/[0.14] group-hover:shadow-[0_0_12px_rgba(255,255,255,0.08)]">
              <PenLine className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight gradient-text">
              HandwritOCR
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden sm:flex items-center gap-1">
            {NAV_LINKS.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    "relative px-4 py-2 text-sm font-medium rounded-xl transition-all duration-300",
                    isActive
                      ? "text-white bg-white/[0.08] border border-white/[0.12] shadow-[0_0_12px_rgba(255,255,255,0.04)]"
                      : "text-white/60 hover:text-white hover:bg-white/[0.04]"
                  )}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* Mobile hamburger */}
          <button
            className="sm:hidden flex items-center justify-center h-9 w-9 rounded-xl glass-button"
            onClick={handleToggle}
            aria-label="Toggle menu"
          >
            {isNavOpen ? (
              <X className="h-4 w-4 text-white" />
            ) : (
              <Menu className="h-4 w-4 text-white" />
            )}
          </button>
        </div>

        {/* Mobile dropdown */}
        <div
          className={cn(
            "sm:hidden overflow-hidden transition-all duration-300 ease-out",
            isNavOpen ? "max-h-40 opacity-100 pb-4" : "max-h-0 opacity-0"
          )}
        >
          <div className="flex flex-col gap-1 pt-2 border-t border-white/[0.06]">
            {NAV_LINKS.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={handleClose}
                  className={cn(
                    "px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-300",
                    isActive
                      ? "text-white bg-white/[0.08]"
                      : "text-white/60 hover:text-white hover:bg-white/[0.04]"
                  )}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}

export const Navbar = React.memo(NavbarInner);
