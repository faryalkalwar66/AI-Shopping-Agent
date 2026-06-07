import customtkinter as ctk
import threading
import webbrowser
from collections import defaultdict
from scraper import search_all_websites, add_to_favorites, get_comparison, get_best
from database import (get_all_searches, get_all_favorites,
                      delete_all_searches, delete_all_favorites,
                      get_stats, get_best_deals_all, get_savings_comparison,
                      get_website_stats, count_products_per_website,
                      get_all_products, get_products_by_category,
                      delete_favorite)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---- COLORS ----
BG_MAIN    = "#F0F4FF"
BG_CARD    = "#FFFFFF"
BG_HEADER  = "#1E1B4B"
CLR_PURPLE = "#7C3AED"
CLR_PINK   = "#DB2777"
CLR_BLUE   = "#2563EB"
CLR_GREEN  = "#059669"
CLR_ORANGE = "#D97706"
CLR_RED    = "#DC2626"
CLR_CYAN   = "#0891B2"
CLR_WHITE  = "#FFFFFF"
CLR_DARK   = "#1E1B4B"
CLR_GRAY   = "#6B7280"
CLR_LIGHT  = "#E0E7FF"

WEBSITE_COLORS = {
    "Daraz":    "#D97706",
    "Goto":     "#2563EB",
    "Shophive": "#7C3AED",
}
WEBSITE_BG = {
    "Daraz":    "#FEF3C7",
    "Goto":     "#DBEAFE",
    "Shophive": "#EDE9FE",
}


class ShoppingAgent(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("AI Shopping Agent — 3 Website Price Comparator")
        self.geometry("1150x750")
        self.resizable(True, True)
        self.configure(fg_color=BG_MAIN)
        # BUG FIX: removed self.results — was written from background thread
        # and read from GUI thread unsafely. Results are now passed directly
        # via self.after() callback instead.
        self.build_ui()

    # ==========================================
    #           BUILD UI
    # ==========================================

    def build_ui(self):

        # ---- HEADER ----
        header = ctk.CTkFrame(self, fg_color=BG_HEADER, corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(left, text="🛍️  AI Shopping Agent",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color="#A5B4FC").pack(anchor="w")

        ctk.CTkLabel(left, text="Compare prices across Daraz • Goto • Shophive",
                     font=ctk.CTkFont(size=12),
                     text_color="#C7D2FE").pack(anchor="w")

        badge_frame = ctk.CTkFrame(header, fg_color="transparent")
        badge_frame.pack(side="left", padx=20)
        for text, color in [("🟠 Daraz", "#FCD34D"),
                             ("🔵 Goto",  "#93C5FD"),
                             ("🟣 Shophive", "#C4B5FD")]:
            ctk.CTkLabel(badge_frame, text=text,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=color).pack(side="left", padx=10)

        ctk.CTkLabel(header, text="🍃 Powered by MongoDB",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#6EE7B7").pack(side="right", padx=20)

        # ---- SEARCH BAR ----
        search_outer = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0, height=75)
        search_outer.pack(fill="x")
        search_outer.pack_propagate(False)

        search_frame = ctk.CTkFrame(search_outer, fg_color="#EEF2FF", corner_radius=20)
        search_frame.pack(padx=30, pady=12, fill="x")

        ctk.CTkLabel(search_frame, text="🔍",
                     font=ctk.CTkFont(size=20)).pack(side="left", padx=15, pady=10)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search any product — mobile, laptop, headphones, AC...",
            font=ctk.CTkFont(size=14), height=40, width=560,
            fg_color=CLR_WHITE, border_color="#A5B4FC",
            text_color=CLR_DARK, placeholder_text_color=CLR_GRAY)
        self.search_entry.pack(side="left", padx=8, pady=10)
        self.search_entry.bind("<Return>", lambda e: self.start_search())

        ctk.CTkButton(search_frame, text="🔎  Search All Sites",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      height=40, width=160, fg_color=CLR_PURPLE,
                      hover_color="#6D28D9", corner_radius=12,
                      text_color=CLR_WHITE,
                      command=self.start_search).pack(side="left", padx=8)

        ctk.CTkButton(search_frame, text="✖ Clear",
                      font=ctk.CTkFont(size=13), height=40, width=80,
                      fg_color="#E5E7EB", hover_color="#D1D5DB",
                      corner_radius=12, text_color=CLR_DARK,
                      command=self.clear_all).pack(side="left", padx=4)

        # ---- STATUS ----
        self.status_label = ctk.CTkLabel(
            self, text="✨  Enter a product name to search across all 3 websites",
            font=ctk.CTkFont(size=12), text_color=CLR_GRAY, fg_color=BG_MAIN)
        self.status_label.pack(pady=4)

        # ---- TABS ----
        self.tabs = ctk.CTkTabview(
            self, fg_color=BG_CARD,
            segmented_button_fg_color=CLR_LIGHT,
            segmented_button_selected_color=CLR_PURPLE,
            segmented_button_selected_hover_color="#6D28D9",
            segmented_button_unselected_color=CLR_LIGHT,
            segmented_button_unselected_hover_color="#C7D2FE",
            text_color=CLR_DARK, corner_radius=15)
        self.tabs.pack(padx=20, pady=5, fill="both", expand=True)

        self.tabs.add("🛒  Results")
        self.tabs.add("⚖️  Compare")
        self.tabs.add("🏆  Best Deals")
        self.tabs.add("📜  History")
        self.tabs.add("⭐  Favorites")
        self.tabs.add("📊  Statistics")

        self._build_results_tab()
        self._build_compare_tab()
        self._build_bestdeals_tab()
        self._build_history_tab()
        self._build_favorites_tab()
        self._build_stats_tab()

    # ==========================================
    #       RESULTS TAB
    # ==========================================

    def _build_results_tab(self):
        tab = self.tabs.tab("🛒  Results")
        self.results_frame = ctk.CTkScrollableFrame(
            tab, fg_color="transparent",
            scrollbar_button_color=CLR_PURPLE)
        self.results_frame.pack(padx=5, pady=5, fill="both", expand=True)

    def start_search(self):
        product = self.search_entry.get().strip()
        if not product:
            self.status_label.configure(
                text="⚠️  Please enter a product name!", text_color=CLR_RED)
            return
        self.status_label.configure(
            text=f"🔄  Searching '{product}' on Daraz, Goto & Shophive...",
            text_color=CLR_ORANGE)
        self.clear_results()
        # BUG FIX: daemon thread — no longer writes to self.results
        thread = threading.Thread(target=self._run_search, args=(product,))
        thread.daemon = True
        thread.start()

    def _run_search(self, product):
        # BUG FIX: results are passed directly to show_results via after()
        # instead of being stored in self.results (thread-safety fix)
        results = search_all_websites(product)
        self.after(0, lambda: self.show_results(results))

    def show_results(self, results):
        for w in self.results_frame.winfo_children():
            w.destroy()

        if not results:
            self.status_label.configure(
                text="❌  No products found. Try a different search.", text_color=CLR_RED)
            return

        self.status_label.configure(
            text=f"✅  Found {len(results)} products — saved to MongoDB!",
            text_color=CLR_GREEN)
        self.tabs.set("🛒  Results")

        for i, item in enumerate(results, 1):
            website = item.get("website", "")
            color   = WEBSITE_COLORS.get(website, CLR_GRAY)
            bg      = WEBSITE_BG.get(website, "#F9FAFB")

            card = ctk.CTkFrame(self.results_frame, fg_color=bg,
                                corner_radius=12, border_width=1,
                                border_color=color)
            card.pack(fill="x", padx=8, pady=4)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=15, pady=10)

            ctk.CTkLabel(info,
                         text=f"{i}.  {item['name'][:70]}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=CLR_DARK, anchor="w").pack(fill="x")

            ctk.CTkLabel(info,
                         text=f"💰  {item.get('price_display', item.get('price',''))}   ●  {website}",
                         font=ctk.CTkFont(size=12),
                         text_color=color, anchor="w").pack(fill="x")

            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.pack(side="right", padx=10, pady=8)

            # BUG FIX: guard against empty link before opening browser
            link = item.get('link', '')
            ctk.CTkButton(btns, text="🌐 Open",
                          width=90, height=30, fg_color=CLR_BLUE,
                          corner_radius=8, text_color=CLR_WHITE,
                          command=lambda l=link: webbrowser.open(l) if l else
                              self.status_label.configure(
                                  text="⚠️  No link available for this product.",
                                  text_color=CLR_ORANGE)
                          ).pack(pady=2)

            # BUG FIX: pass price_numeric (int) alongside price_display (string)
            price_display = item.get('price_display', str(item.get('price', '')))
            price_numeric = item.get('price', 0)
            ctk.CTkButton(btns, text="⭐ Save",
                          width=90, height=30, fg_color=CLR_ORANGE,
                          corner_radius=8, text_color=CLR_WHITE,
                          command=lambda n=item['name'],
                                         pd=price_display,
                                         pn=price_numeric,
                                         w=website,
                                         l=link: self.save_favorite(n, pd, pn, w, l)
                          ).pack(pady=2)

    def save_favorite(self, name, price_display, price_numeric, website, link):
        # BUG FIX: passes price_numeric so both display and sortable int are saved
        success = add_to_favorites(name, price_display, price_numeric, website, link)
        if success:
            self.status_label.configure(
                text=f"⭐  Saved to favorites: {name[:45]}", text_color=CLR_GREEN)
        else:
            self.status_label.configure(
                text=f"⚠️  Already in favorites: {name[:45]}", text_color=CLR_ORANGE)

    def clear_results(self):
        for w in self.results_frame.winfo_children():
            w.destroy()

    def clear_all(self):
        self.search_entry.delete(0, "end")
        self.clear_results()
        self.status_label.configure(
            text="✨  Enter a product name to search", text_color=CLR_GRAY)

    # ==========================================
    #       COMPARE TAB
    # ==========================================

    def _build_compare_tab(self):
        tab = self.tabs.tab("⚖️  Compare")
        top = ctk.CTkFrame(tab, fg_color="#EEF2FF", corner_radius=12)
        top.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(top, text="⚖️  Compare prices for your search query:",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=CLR_DARK).pack(side="left", padx=10, pady=8)

        ctk.CTkButton(top, text="⚖️  Load Comparison",
                      fg_color=CLR_BLUE, hover_color="#1D4ED8",
                      height=36, corner_radius=10, text_color=CLR_WHITE,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self.load_comparison).pack(side="left", padx=5, pady=8)

        self.compare_frame = ctk.CTkScrollableFrame(
            tab, fg_color="transparent",
            scrollbar_button_color=CLR_BLUE)
        self.compare_frame.pack(padx=5, pady=5, fill="both", expand=True)

    def load_comparison(self):
        for w in self.compare_frame.winfo_children():
            w.destroy()

        query = self.search_entry.get().strip()
        if not query:
            ctk.CTkLabel(self.compare_frame,
                         text="Enter a product name in the search bar first.",
                         text_color=CLR_GRAY).pack(pady=20)
            return

        comparison = get_comparison(query)
        if not comparison:
            ctk.CTkLabel(self.compare_frame,
                         text="No comparison data. Search a product first.",
                         text_color=CLR_GRAY).pack(pady=20)
            return

        for website, items in comparison.items():
            color = WEBSITE_COLORS.get(website, CLR_GRAY)
            bg    = WEBSITE_BG.get(website, "#F9FAFB")

            section = ctk.CTkFrame(self.compare_frame, fg_color=bg,
                                   corner_radius=12, border_width=2,
                                   border_color=color)
            section.pack(fill="x", padx=8, pady=6)

            ctk.CTkLabel(section, text=f"● {website} — {len(items)} products",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=color).pack(anchor="w", padx=15, pady=(10,4))

            for item in items[:5]:
                row = ctk.CTkFrame(section, fg_color=BG_CARD, corner_radius=8)
                row.pack(fill="x", padx=15, pady=3)
                ctk.CTkLabel(row, text=item["name"][:60],
                             font=ctk.CTkFont(size=12), text_color=CLR_DARK,
                             anchor="w").pack(side="left", padx=10, pady=6, fill="x", expand=True)
                ctk.CTkLabel(row, text=item.get("price_display", ""),
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=CLR_GREEN).pack(side="right", padx=15)

    # ==========================================
    #       BEST DEALS TAB
    # ==========================================

    def _build_bestdeals_tab(self):
        tab = self.tabs.tab("🏆  Best Deals")
        top = ctk.CTkFrame(tab, fg_color="#FEF3C7", corner_radius=12)
        top.pack(fill="x", padx=10, pady=8)

        ctk.CTkButton(top, text="🏆  Find Best Deal for Search",
                      fg_color=CLR_ORANGE, hover_color="#B45309",
                      height=36, corner_radius=10, text_color=CLR_WHITE,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self.load_best_deals).pack(side="left", padx=10, pady=8)

        self.bestdeals_frame = ctk.CTkScrollableFrame(
            tab, fg_color="transparent",
            scrollbar_button_color=CLR_ORANGE)
        self.bestdeals_frame.pack(padx=5, pady=5, fill="both", expand=True)

    def load_best_deals(self):
        for w in self.bestdeals_frame.winfo_children():
            w.destroy()

        query = self.search_entry.get().strip()

        # BUG FIX: show a clear message when search bar is empty
        if not query:
            ctk.CTkLabel(self.bestdeals_frame,
                         text="⚠️  Enter a product name in the search bar first, then click Best Deals.",
                         font=ctk.CTkFont(size=13),
                         text_color=CLR_ORANGE).pack(pady=20)
        else:
            best = get_best(query)
            if best:
                website = best.get("website", "")
                color   = WEBSITE_COLORS.get(website, CLR_ORANGE)
                bg      = WEBSITE_BG.get(website, "#FEF3C7")

                card = ctk.CTkFrame(self.bestdeals_frame, fg_color=bg,
                                    corner_radius=15, border_width=2,
                                    border_color=color)
                card.pack(fill="x", padx=15, pady=10)

                ctk.CTkLabel(card, text="🏆  BEST DEAL FOUND!",
                             font=ctk.CTkFont(size=16, weight="bold"),
                             text_color=color).pack(pady=(12,4))

                ctk.CTkLabel(card, text=best.get("name", ""),
                             font=ctk.CTkFont(size=13), text_color=CLR_DARK,
                             wraplength=700).pack(padx=20)

                ctk.CTkLabel(card,
                             text=f"💰  {best.get('price_display','')}   ●   {website}",
                             font=ctk.CTkFont(size=14, weight="bold"),
                             text_color=CLR_GREEN).pack(pady=8)

                # BUG FIX: guard against empty link
                best_link = best.get("link", "")
                ctk.CTkButton(card, text="🌐 Open Product",
                              fg_color=color, corner_radius=10,
                              text_color=CLR_WHITE, height=36,
                              command=lambda l=best_link: webbrowser.open(l) if l else
                                  self.status_label.configure(
                                      text="⚠️  No link available.", text_color=CLR_ORANGE)
                              ).pack(pady=(4,12))
            else:
                ctk.CTkLabel(self.bestdeals_frame,
                             text=f"No results found for '{query}'. Try searching first.",
                             font=ctk.CTkFont(size=13),
                             text_color=CLR_GRAY).pack(pady=20)

        # Also show all-site best deals from MongoDB
        ctk.CTkLabel(self.bestdeals_frame,
                     text="📊  Best Deal Per Website (from all stored data)",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=CLR_DARK).pack(anchor="w", padx=15, pady=(15,5))

        for bd in get_best_deals_all():
            website = bd.get("_id", "")
            color   = WEBSITE_COLORS.get(website, CLR_GRAY)
            bg      = WEBSITE_BG.get(website, "#F9FAFB")

            row = ctk.CTkFrame(self.bestdeals_frame, fg_color=bg,
                               corner_radius=10, border_width=1,
                               border_color=color)
            row.pack(fill="x", padx=10, pady=4)

            ctk.CTkLabel(row, text=f"● {website}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=color, width=100).pack(side="left", padx=15, pady=10)

            ctk.CTkLabel(row, text=bd.get("product", "")[:50],
                         font=ctk.CTkFont(size=12),
                         text_color=CLR_DARK).pack(side="left", padx=10)

            ctk.CTkLabel(row, text=f"Rs. {int(bd.get('min_price',0)):,}",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=CLR_GREEN).pack(side="right", padx=15)

    # ==========================================
    #       HISTORY TAB
    # ==========================================

    def _build_history_tab(self):
        tab = self.tabs.tab("📜  History")
        top = ctk.CTkFrame(tab, fg_color="#EEF2FF", corner_radius=12)
        top.pack(fill="x", padx=10, pady=8)

        ctk.CTkButton(top, text="🔄 Refresh",
                      fg_color=CLR_BLUE, hover_color="#1D4ED8",
                      width=120, height=36, corner_radius=10,
                      text_color=CLR_WHITE,
                      command=self.load_history).pack(side="left", padx=5, pady=8)

        ctk.CTkButton(top, text="🗑️ Clear All",
                      fg_color=CLR_RED, hover_color="#B91C1C",
                      width=120, height=36, corner_radius=10,
                      text_color=CLR_WHITE,
                      command=self.clear_history).pack(side="left", padx=5)

        self.history_frame = ctk.CTkScrollableFrame(
            tab, fg_color="transparent",
            scrollbar_button_color=CLR_BLUE)
        self.history_frame.pack(padx=5, pady=5, fill="both", expand=True)
        self.load_history()

    def load_history(self):
        for w in self.history_frame.winfo_children():
            w.destroy()

        history = get_all_searches()
        if not history:
            ctk.CTkLabel(self.history_frame,
                         text="📭  No search history found.",
                         font=ctk.CTkFont(size=14),
                         text_color=CLR_GRAY).pack(pady=30)
            return

        for i, item in enumerate(history, 1):
            card = ctk.CTkFrame(self.history_frame, fg_color=BG_CARD,
                                corner_radius=10, border_width=1,
                                border_color="#C7D2FE")
            card.pack(fill="x", padx=8, pady=3)

            ctk.CTkLabel(card,
                         text=f"🔍  {i}.  {item['product']}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=CLR_DARK,
                         anchor="w").pack(side="left", padx=15, pady=8)

            ctk.CTkLabel(card,
                         text=f"📅 {item.get('date','')}  🕐 {item.get('time','')}",
                         font=ctk.CTkFont(size=11),
                         text_color=CLR_GRAY).pack(side="right", padx=15)

    def clear_history(self):
        delete_all_searches()
        self.load_history()
        self.status_label.configure(
            text="🗑️  Search history cleared from MongoDB!", text_color=CLR_ORANGE)

    # ==========================================
    #       FAVORITES TAB
    # ==========================================

    def _build_favorites_tab(self):
        tab = self.tabs.tab("⭐  Favorites")
        top = ctk.CTkFrame(tab, fg_color="#FEF3C7", corner_radius=12)
        top.pack(fill="x", padx=10, pady=8)

        ctk.CTkButton(top, text="🔄 Refresh",
                      fg_color=CLR_ORANGE, hover_color="#B45309",
                      width=120, height=36, corner_radius=10,
                      text_color=CLR_WHITE,
                      command=self.load_favorites).pack(side="left", padx=5, pady=8)

        ctk.CTkButton(top, text="🗑️ Clear All",
                      fg_color=CLR_RED, hover_color="#B91C1C",
                      width=120, height=36, corner_radius=10,
                      text_color=CLR_WHITE,
                      command=self.clear_favorites).pack(side="left", padx=5)

        self.favorites_frame = ctk.CTkScrollableFrame(
            tab, fg_color="transparent",
            scrollbar_button_color=CLR_ORANGE)
        self.favorites_frame.pack(padx=5, pady=5, fill="both", expand=True)
        self.load_favorites()

    def load_favorites(self):
        for w in self.favorites_frame.winfo_children():
            w.destroy()

        favorites = get_all_favorites()
        if not favorites:
            ctk.CTkLabel(self.favorites_frame,
                         text="📭  No favorites saved yet.",
                         font=ctk.CTkFont(size=14),
                         text_color=CLR_GRAY).pack(pady=30)
            return

        for i, item in enumerate(favorites, 1):
            website = item.get("website", "")
            color   = WEBSITE_COLORS.get(website, CLR_GRAY)
            bg      = WEBSITE_BG.get(website, "#F9FAFB")

            card = ctk.CTkFrame(self.favorites_frame, fg_color=bg,
                                corner_radius=12, border_width=1,
                                border_color=color)
            card.pack(fill="x", padx=8, pady=4)

            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True, padx=15, pady=10)

            ctk.CTkLabel(left,
                         text=f"⭐  {item.get('product','')}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=CLR_DARK, anchor="w").pack(fill="x")

            ctk.CTkLabel(left,
                         text=f"💰  {item.get('price','')}   ●  {website}   📅  {item.get('date','')}",
                         font=ctk.CTkFont(size=11),
                         text_color=CLR_GRAY, anchor="w").pack(fill="x")

            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.pack(side="right", padx=10)

            # BUG FIX: guard against empty link before opening browser
            fav_link = item.get("link", "")
            ctk.CTkButton(btns, text="🌐 Open",
                          width=85, height=30, fg_color=color,
                          corner_radius=8, text_color=CLR_WHITE,
                          command=lambda l=fav_link: webbrowser.open(l) if l else
                              self.status_label.configure(
                                  text="⚠️  No link available for this product.",
                                  text_color=CLR_ORANGE)
                          ).pack(pady=2)

            ctk.CTkButton(btns, text="🗑️ Remove",
                          width=85, height=30, fg_color=CLR_RED,
                          corner_radius=8, text_color=CLR_WHITE,
                          command=lambda n=item.get("product",""): self._remove_favorite(n)
                          ).pack(pady=2)

    def _remove_favorite(self, name):
        delete_favorite(name)
        self.load_favorites()
        self.status_label.configure(
            text=f"🗑️  Removed from favorites: {name[:40]}", text_color=CLR_ORANGE)

    def clear_favorites(self):
        delete_all_favorites()
        self.load_favorites()
        self.status_label.configure(
            text="🗑️  All favorites cleared from MongoDB!", text_color=CLR_ORANGE)

    # ==========================================
    #       STATISTICS TAB
    # ==========================================

    def _build_stats_tab(self):
        tab = self.tabs.tab("📊  Statistics")
        top = ctk.CTkFrame(tab, fg_color="#ECFDF5", corner_radius=12)
        top.pack(fill="x", padx=10, pady=8)

        ctk.CTkButton(top, text="📊  Load Statistics",
                      fg_color=CLR_GREEN, hover_color="#047857",
                      width=160, height=36, corner_radius=10,
                      text_color=CLR_WHITE,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self.load_stats).pack(side="left", padx=10, pady=8)

        self.stats_frame = ctk.CTkScrollableFrame(
            tab, fg_color="transparent",
            scrollbar_button_color=CLR_GREEN)
        self.stats_frame.pack(padx=5, pady=5, fill="both", expand=True)

    def load_stats(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()

        stats    = get_stats()
        counts   = count_products_per_website()
        ws_stats = get_website_stats()

        # Summary cards
        cards_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=5, pady=10)

        for icon, label, value, color, bg in [
            ("🗄️", "Total Products",  str(stats["total_products"]),  CLR_PURPLE, "#EDE9FE"),
            ("🔍", "Total Searches",  str(stats["total_searches"]),  CLR_BLUE,   "#DBEAFE"),
            ("⭐", "Total Favorites", str(stats["total_favorites"]), CLR_ORANGE, "#FEF3C7"),
            ("🌐", "Websites",        "3",                           CLR_GREEN,  "#DCFCE7"),
        ]:
            card = ctk.CTkFrame(cards_frame, fg_color=bg, corner_radius=15,
                                border_width=2, border_color=color,
                                width=210, height=95)
            card.pack(side="left", padx=8, pady=5)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=icon,  font=ctk.CTkFont(size=22)).pack(pady=(8,0))
            ctk.CTkLabel(card, text=value,
                         font=ctk.CTkFont(size=24, weight="bold"),
                         text_color=color).pack()
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=11),
                         text_color=CLR_GRAY).pack()

        # Per-website product counts
        ctk.CTkLabel(self.stats_frame, text="📊  Products per Website",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=CLR_DARK).pack(anchor="w", padx=15, pady=(15,5))

        web_row = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        web_row.pack(fill="x", padx=10, pady=5)

        for website, color in WEBSITE_COLORS.items():
            count = counts.get(website, 0)
            bg    = WEBSITE_BG.get(website, "#F9FAFB")
            wcard = ctk.CTkFrame(web_row, fg_color=bg, corner_radius=12,
                                 border_width=2, border_color=color,
                                 width=210, height=80)
            wcard.pack(side="left", padx=8)
            wcard.pack_propagate(False)
            ctk.CTkLabel(wcard, text=website,
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=color).pack(pady=(10,0))
            ctk.CTkLabel(wcard, text=f"{count} products",
                         font=ctk.CTkFont(size=18, weight="bold"),
                         text_color=CLR_DARK).pack()

        # Aggregate price analysis
        ctk.CTkLabel(self.stats_frame,
                     text="📈  Price Analysis (MongoDB Aggregation)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=CLR_DARK).pack(anchor="w", padx=15, pady=(15,5))

        for ws in ws_stats:
            website = ws.get("_id", "")
            color   = WEBSITE_COLORS.get(website, CLR_GRAY)
            bg      = WEBSITE_BG.get(website, "#F9FAFB")

            row = ctk.CTkFrame(self.stats_frame, fg_color=bg,
                               corner_radius=10, border_width=1,
                               border_color=color)
            row.pack(fill="x", padx=10, pady=4)

            ctk.CTkLabel(row, text=f"● {website}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=color, width=110).pack(side="left", padx=15, pady=10)

            for label, clr in [
                (f"Avg: Rs. {int(ws.get('avg_price',0)):,}",       CLR_CYAN),
                (f"Min: Rs. {int(ws.get('cheapest',0)):,}",        CLR_GREEN),
                (f"Max: Rs. {int(ws.get('most_expensive',0)):,}",  CLR_RED),
                (f"Total: {int(ws.get('total_products',0))} items", CLR_GRAY),
            ]:
                ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12),
                             text_color=clr, width=190).pack(side="left")

        # MongoDB info footer
        mongo = ctk.CTkFrame(self.stats_frame, fg_color="#DCFCE7",
                             corner_radius=12, border_width=1,
                             border_color=CLR_GREEN)
        mongo.pack(fill="x", padx=10, pady=15)
        ctk.CTkLabel(mongo,
                     text="🍃  MongoDB  |  DB: shopping_agent  |  "
                          "Collections: all_products • search_history • favorite_products",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_GREEN).pack(pady=12)


# ---- RUN ----
if __name__ == "__main__":
    app = ShoppingAgent()
    app.mainloop()