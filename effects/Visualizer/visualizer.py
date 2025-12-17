import pygame
import socket

class Visualizer:
    def __init__(self, width=19, height=7, pixel_size=40, port=50555):
        self.width = width
        self.height = height
        self.pixel_size = pixel_size

        # Visualization state
        self.enabled = False
        self.window = None
        self.running = True

        # UDP command server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", port))
        self.sock.setblocking(False)

    # -----------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------
    def update(self, positions, colors):
        """Call this once per frame from your main loop."""

        # 1. Handle UDP commands
        self._poll_commands()

        # 2. If window is closed or disabled, do nothing else
        if not self.enabled:
            return

        # 3. Create window if needed
        if self.window is None:
            self._open_window()

        # 4. Process pygame events
        if not self._process_events():
            # Window was closed
            self.enabled = False
            self.window = None
            pygame.display.quit()
            return

        # 5. Draw frame
        self._draw(positions, colors)

    # -----------------------------------------------------------
    # INTERNAL HELPERS
    # -----------------------------------------------------------

    def _poll_commands(self):
        """Non-blocking UDP command handler."""
        try:
            data, addr = self.sock.recvfrom(1024)
            cmd = data.decode().strip()

            if cmd == "toggle_visualizer":
                if not self.enabled:
                    self.enabled = True
                else:
                    self.enabled = False
                    if self.window:
                        pygame.display.quit()
                        self.window = None

        except BlockingIOError:
            pass

    def _open_window(self):
        pygame.init()
        self.window = pygame.display.set_mode(
            (self.width * self.pixel_size, self.height * self.pixel_size)
        )
        pygame.display.set_caption("LED Visualizer")

    def _process_events(self):
        """Returns False if window should close."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Optional window-only hotkeys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    return False

        return True

    def _draw(self, positions, colors):
        self.window.fill((20, 20, 20))

        for (x, y), c in zip(positions, colors):
            gx = int(round(x))
            gy = int(round(y))

            if 0 <= gx < self.width and 0 <= gy < self.height:
                rect = pygame.Rect(
                    gx * self.pixel_size,
                    gy * self.pixel_size,
                    self.pixel_size - 2,
                    self.pixel_size - 2
                )
                pygame.draw.rect(
                    self.window,
                    (c.red, c.green, c.blue),
                    rect
                )

        pygame.display.flip()

    def _force_stop_server(self):
        self.sock.close()