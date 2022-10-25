from pathlib import Path
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.widgets import Header, Footer

from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static

from textual.reactive import reactive
from time import monotonic


class TimeDisplay(Static):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update the time to the current time."""
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self):
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self):
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0


class Stopwatch(Static):
    """A stopwatch widget."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00.00")


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = Path("__file__").parent / "tui.css"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_stopwatch", "Add"),
        ("r", "remove_stopwatch", "Remove"),
        ("R", "reset", "Reset"),
        ("j", "next", "Next"),
        ("j", "next", "Next"),
        ("k", "prev", "Prev"),
        ("space", "toggle", "Toggle"),
    ]

    def on_mount(self):

        try:
            self.query_one("Stopwatch").add_class("active")
        except NoMatches:
            ...

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            # Stopwatch(),
            # Stopwatch(),
            # Stopwatch(),
            id="timers",
        )
        yield Footer()

    def action_next(self):
        self.activate(1)

    def action_prev(self):
        self.activate(-1)

    def action_toggle(self):
        try:
            active = self.query_one("Stopwatch.active")
        except NoMatches:
            return
        if "started" in active.classes:
            active.query_one("#stop").press()
        else:
            active.query_one("#start").press()

    def action_reset(self):
        try:
            active = self.query_one("Stopwatch.active")
            active.query_one("#reset").press()
        except NoMatches:
            ...

    def activate(self, n=1):
        try:
            active = self.query_one("Stopwatch.active")
        except NoMatches:
            return
        stopwatches = self.query("Stopwatch").nodes
        active_index = stopwatches.index(active)
        next_index = active_index + n
        if next_index > len(stopwatches) - 1:
            next_index = 0
        if next_index < 0:
            next_index = len(stopwatches) - 1
        active.remove_class("active")
        stopwatches[next_index].add_class("active")

    def action_add_stopwatch(self) -> None:
        """An action to add a timer."""
        new_stopwatch = Stopwatch()
        try:
            active = self.query_one("Stopwatch.active")
            active.remove_class("active")
        except NoMatches:
            ...
        new_stopwatch.add_class("active")
        self.query_one("#timers").mount(new_stopwatch)
        new_stopwatch.scroll_visible()

    def action_remove_stopwatch(self) -> None:
        """Called to remove a timer."""
        timers = self.query("Stopwatch")
        if timers:
            timers.last().remove()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
        self.log("going dark")


def tui():

    from textual.features import parse_features
    import os
    import sys

    dev = "--dev" in sys.argv
    features = set(parse_features(os.environ.get("TEXTUAL", "")))
    if dev:
        features.add("debug")
        features.add("devtools")

    os.environ["TEXTUAL"] = ",".join(sorted(features))
    app = StopwatchApp()
    app.run()


if __name__ == "__main__":
    tui()
