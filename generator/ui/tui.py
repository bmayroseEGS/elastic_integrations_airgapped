"""
Terminal User Interface for the data generator.
Simple curses-based TUI for selecting and managing integrations.
"""

import curses
import time
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from main import DataGenerator

from integrations import AVAILABLE_INTEGRATIONS


class IntegrationTUI:
    """Terminal UI for managing integrations."""

    def __init__(self, generator: 'DataGenerator'):
        self.generator = generator
        self.screen = None
        self.current_view = "integrations"  # integrations, datasets, config, status
        self.selected_integration = None
        self.selected_dataset = None
        self.cursor_pos = 0
        self.eps_value = 1.0
        self.scroll_offset = 0

        # Get sorted list of integrations
        self.integration_list = sorted(AVAILABLE_INTEGRATIONS.keys())

    def run(self):
        """Run the TUI."""
        curses.wrapper(self._main)

    def _main(self, screen):
        """Main curses loop."""
        self.screen = screen
        curses.curs_set(0)  # Hide cursor

        # Setup colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)   # Enabled/success
        curses.init_pair(2, curses.COLOR_RED, -1)     # Disabled/error
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Warning/highlight
        curses.init_pair(4, curses.COLOR_CYAN, -1)    # Info
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Selected

        while True:
            self.screen.clear()
            self._draw_header()

            if self.current_view == "integrations":
                self._draw_integrations()
            elif self.current_view == "datasets":
                self._draw_datasets()
            elif self.current_view == "config":
                self._draw_config()
            elif self.current_view == "status":
                self._draw_status()

            self._draw_footer()
            self.screen.refresh()

            # Handle input
            key = self.screen.getch()
            if not self._handle_input(key):
                break

    def _draw_header(self):
        """Draw the header bar."""
        height, width = self.screen.getmaxyx()
        title = " Elastic Integration Data Generator "
        subtitle = "Air-Gapped Edition - All data embedded"

        # Title
        self.screen.attron(curses.A_BOLD)
        self.screen.addstr(0, (width - len(title)) // 2, title)
        self.screen.attroff(curses.A_BOLD)

        # Subtitle
        self.screen.attron(curses.color_pair(4))
        self.screen.addstr(1, (width - len(subtitle)) // 2, subtitle)
        self.screen.attroff(curses.color_pair(4))

        # Navigation tabs
        tabs = ["[I]ntegrations", "[S]tatus", "[Q]uit"]
        tab_str = "  ".join(tabs)
        self.screen.addstr(3, 2, tab_str)
        self.screen.addstr(4, 0, "─" * width)

    def _draw_footer(self):
        """Draw the footer with help."""
        height, width = self.screen.getmaxyx()

        if self.current_view == "integrations":
            help_text = "↑↓:Navigate  Enter:Select  S:Status  Q:Quit"
        elif self.current_view == "datasets":
            help_text = "↑↓:Navigate  Enter:Configure  Esc:Back  Q:Quit"
        elif self.current_view == "config":
            help_text = "↑↓:Adjust EPS  Enter:Start  Esc:Back  Q:Quit"
        elif self.current_view == "status":
            help_text = "↑↓:Navigate  Enter:Stop  I:Integrations  Q:Quit"
        else:
            help_text = "Q:Quit"

        self.screen.addstr(height - 2, 0, "─" * width)
        self.screen.attron(curses.color_pair(4))
        self.screen.addstr(height - 1, 2, help_text[:width-4])
        self.screen.attroff(curses.color_pair(4))

    def _draw_integrations(self):
        """Draw the integrations list."""
        height, width = self.screen.getmaxyx()
        start_y = 6
        max_items = height - 10

        # Title
        self.screen.attron(curses.A_BOLD)
        self.screen.addstr(start_y - 1, 2, f"Available Integrations ({len(self.integration_list)})")
        self.screen.attroff(curses.A_BOLD)

        # Adjust scroll
        if self.cursor_pos >= self.scroll_offset + max_items:
            self.scroll_offset = self.cursor_pos - max_items + 1
        elif self.cursor_pos < self.scroll_offset:
            self.scroll_offset = self.cursor_pos

        # Draw list
        for i, integration in enumerate(self.integration_list[self.scroll_offset:self.scroll_offset + max_items]):
            y = start_y + i
            idx = self.scroll_offset + i

            # Check if any datasets are running
            running_count = 0
            integration_info = AVAILABLE_INTEGRATIONS[integration]
            for dataset in integration_info["datasets"]:
                key = f"{integration}:{dataset}"
                if key in self.generator.integrations and self.generator.integrations[key].running:
                    running_count += 1

            # Format line
            if running_count > 0:
                status = f"[{running_count} running]"
                status_color = curses.color_pair(1)
            else:
                status = ""
                status_color = 0

            # Highlight selected
            if idx == self.cursor_pos:
                self.screen.attron(curses.color_pair(5))
                self.screen.addstr(y, 2, " " * (width - 4))
                self.screen.addstr(y, 2, f" ▶ {integration}")
                if status:
                    self.screen.addstr(y, 40, status)
                self.screen.attroff(curses.color_pair(5))
            else:
                self.screen.addstr(y, 2, f"   {integration}")
                if status:
                    self.screen.attron(status_color)
                    self.screen.addstr(y, 40, status)
                    self.screen.attroff(status_color)

        # Scroll indicator
        if len(self.integration_list) > max_items:
            indicator = f" [{self.scroll_offset + 1}-{min(self.scroll_offset + max_items, len(self.integration_list))}/{len(self.integration_list)}]"
            self.screen.addstr(start_y - 1, width - len(indicator) - 2, indicator)

    def _draw_datasets(self):
        """Draw datasets for selected integration."""
        height, width = self.screen.getmaxyx()
        start_y = 6

        if not self.selected_integration:
            return

        integration_info = AVAILABLE_INTEGRATIONS[self.selected_integration]
        datasets = list(integration_info["datasets"].keys())

        # Title
        self.screen.attron(curses.A_BOLD)
        self.screen.addstr(start_y - 1, 2, f"{self.selected_integration} - Select Dataset")
        self.screen.attroff(curses.A_BOLD)

        # Description
        desc = integration_info.get("description", "")[:width-6]
        self.screen.attron(curses.color_pair(4))
        self.screen.addstr(start_y, 2, desc)
        self.screen.attroff(curses.color_pair(4))

        # Draw datasets
        for i, dataset in enumerate(datasets):
            y = start_y + 2 + i
            dataset_info = integration_info["datasets"][dataset]

            # Check if running
            key = f"{self.selected_integration}:{dataset}"
            if key in self.generator.integrations and self.generator.integrations[key].running:
                status = "[RUNNING]"
                status_color = curses.color_pair(1)
            else:
                status = ""
                status_color = 0

            # Highlight selected
            if i == self.cursor_pos:
                self.screen.attron(curses.color_pair(5))
                self.screen.addstr(y, 2, " " * (width - 4))
                self.screen.addstr(y, 2, f" ▶ {dataset}")
                if status:
                    self.screen.addstr(y, 30, status)
                self.screen.attroff(curses.color_pair(5))
            else:
                self.screen.addstr(y, 2, f"   {dataset}")
                if status:
                    self.screen.attron(status_color)
                    self.screen.addstr(y, 30, status)
                    self.screen.attroff(status_color)

            # Dataset description
            ds_desc = dataset_info.get("description", "")[:width-40]
            self.screen.attron(curses.color_pair(4))
            self.screen.addstr(y, 50, ds_desc[:width-52])
            self.screen.attroff(curses.color_pair(4))

    def _draw_config(self):
        """Draw configuration screen for starting an integration."""
        height, width = self.screen.getmaxyx()
        start_y = 6

        # Title
        self.screen.attron(curses.A_BOLD)
        self.screen.addstr(start_y, 2, f"Configure: {self.selected_integration} / {self.selected_dataset}")
        self.screen.attroff(curses.A_BOLD)

        # EPS setting
        self.screen.addstr(start_y + 3, 4, "Events per second:")
        self.screen.attron(curses.color_pair(3) | curses.A_BOLD)
        self.screen.addstr(start_y + 3, 25, f"< {self.eps_value:.1f} >")
        self.screen.attroff(curses.color_pair(3) | curses.A_BOLD)

        # Data stream info
        integration_info = AVAILABLE_INTEGRATIONS[self.selected_integration]
        dataset_info = integration_info["datasets"][self.selected_dataset]
        data_stream = dataset_info.get("data_stream", "logs-*")

        self.screen.addstr(start_y + 5, 4, "Data stream:")
        self.screen.attron(curses.color_pair(4))
        self.screen.addstr(start_y + 5, 18, data_stream)
        self.screen.attroff(curses.color_pair(4))

        # Start button
        self.screen.attron(curses.color_pair(1) | curses.A_BOLD)
        self.screen.addstr(start_y + 8, 4, "[ Press ENTER to START ]")
        self.screen.attroff(curses.color_pair(1) | curses.A_BOLD)

    def _draw_status(self):
        """Draw status of running integrations."""
        height, width = self.screen.getmaxyx()
        start_y = 6

        # Title
        self.screen.attron(curses.A_BOLD)
        self.screen.addstr(start_y - 1, 2, "Running Integrations")
        self.screen.attroff(curses.A_BOLD)

        # Get running integrations
        running = [(k, v) for k, v in self.generator.integrations.items() if v.running]

        if not running:
            self.screen.attron(curses.color_pair(3))
            self.screen.addstr(start_y + 1, 4, "No integrations running")
            self.screen.addstr(start_y + 2, 4, "Press 'I' to go to Integrations and start one")
            self.screen.attroff(curses.color_pair(3))
            return

        # Header
        self.screen.addstr(start_y, 4, "Integration")
        self.screen.addstr(start_y, 30, "Dataset")
        self.screen.addstr(start_y, 50, "EPS")
        self.screen.addstr(start_y, 58, "Events")
        self.screen.addstr(start_y, 70, "Status")
        self.screen.addstr(start_y + 1, 2, "─" * (width - 4))

        # List running integrations
        for i, (key, state) in enumerate(running):
            y = start_y + 2 + i

            # Highlight selected
            if i == self.cursor_pos:
                self.screen.attron(curses.color_pair(5))
                self.screen.addstr(y, 2, " " * (width - 4))

            self.screen.addstr(y, 4, state.name[:24])
            self.screen.addstr(y, 30, state.dataset[:18])
            self.screen.addstr(y, 50, f"{state.events_per_second:.1f}")
            self.screen.addstr(y, 58, f"{state.total_events:,}")

            if state.running:
                self.screen.attron(curses.color_pair(1))
                self.screen.addstr(y, 70, "● Running")
                self.screen.attroff(curses.color_pair(1))
            else:
                self.screen.attron(curses.color_pair(2))
                self.screen.addstr(y, 70, "○ Stopped")
                self.screen.attroff(curses.color_pair(2))

            if i == self.cursor_pos:
                self.screen.attroff(curses.color_pair(5))

        # Total events
        total = sum(s.total_events for _, s in running)
        self.screen.addstr(height - 4, 4, f"Total events generated: {total:,}")

    def _handle_input(self, key) -> bool:
        """Handle keyboard input. Returns False to exit."""
        if key == ord('q') or key == ord('Q'):
            self.generator.stop_all()
            return False

        elif key == ord('i') or key == ord('I'):
            self.current_view = "integrations"
            self.cursor_pos = 0
            self.scroll_offset = 0

        elif key == ord('s') or key == ord('S'):
            self.current_view = "status"
            self.cursor_pos = 0

        elif key == 27:  # Escape
            if self.current_view == "config":
                self.current_view = "datasets"
                self.cursor_pos = 0
            elif self.current_view == "datasets":
                self.current_view = "integrations"
                self.cursor_pos = 0
                self.selected_integration = None

        elif key == curses.KEY_UP:
            if self.current_view == "config":
                self.eps_value = min(100.0, self.eps_value + 0.5)
            else:
                self.cursor_pos = max(0, self.cursor_pos - 1)

        elif key == curses.KEY_DOWN:
            if self.current_view == "config":
                self.eps_value = max(0.1, self.eps_value - 0.5)
            else:
                max_pos = self._get_max_cursor_pos()
                self.cursor_pos = min(max_pos, self.cursor_pos + 1)

        elif key == curses.KEY_LEFT and self.current_view == "config":
            self.eps_value = max(0.1, self.eps_value - 0.5)

        elif key == curses.KEY_RIGHT and self.current_view == "config":
            self.eps_value = min(100.0, self.eps_value + 0.5)

        elif key == 10 or key == curses.KEY_ENTER:  # Enter
            self._handle_enter()

        return True

    def _get_max_cursor_pos(self) -> int:
        """Get maximum cursor position for current view."""
        if self.current_view == "integrations":
            return len(self.integration_list) - 1
        elif self.current_view == "datasets":
            if self.selected_integration:
                return len(AVAILABLE_INTEGRATIONS[self.selected_integration]["datasets"]) - 1
        elif self.current_view == "status":
            running = [k for k, v in self.generator.integrations.items() if v.running]
            return max(0, len(running) - 1)
        return 0

    def _handle_enter(self):
        """Handle Enter key press."""
        if self.current_view == "integrations":
            # Select integration, go to datasets
            self.selected_integration = self.integration_list[self.cursor_pos]
            self.current_view = "datasets"
            self.cursor_pos = 0

        elif self.current_view == "datasets":
            # Select dataset, go to config
            datasets = list(AVAILABLE_INTEGRATIONS[self.selected_integration]["datasets"].keys())
            self.selected_dataset = datasets[self.cursor_pos]
            self.current_view = "config"
            self.eps_value = 1.0

        elif self.current_view == "config":
            # Start the integration
            success = self.generator.start_integration(
                self.selected_integration,
                self.selected_dataset,
                self.eps_value
            )
            if success:
                self.current_view = "status"
                self.cursor_pos = 0

        elif self.current_view == "status":
            # Stop the selected integration
            running = [(k, v) for k, v in self.generator.integrations.items() if v.running]
            if running and self.cursor_pos < len(running):
                key, state = running[self.cursor_pos]
                self.generator.stop_integration(state.name, state.dataset)
