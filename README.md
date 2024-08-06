# Ping Management App

## Description

**Ping Management App** is a desktop application built with Python that provides real-time monitoring of network latency to game servers. Utilizing `tkinter` for the graphical user interface and `ttkbootstrap` for enhanced styling, this application is designed to help users keep track of their connection quality to gaming servers.

### Key Features

- **Executable File Selection:** Users can select the executable file of the game they wish to monitor. This allows the app to identify the process and start monitoring the server ping associated with that game.

- **Real-Time Ping Monitoring:** The application continuously monitors the ping time to the game server, displaying the average response time in milliseconds. It updates this information in real-time, allowing users to keep track of their network performance.

- **Customizable Display Settings:** Users can personalize the appearance of the ping display:
  - **Text Color:** Choose a color for the ping text to match their preferences or UI theme.
  - **Font Size:** Adjust the font size of the displayed ping information for better readability.
  - **Window Transparency:** Modify the transparency of the ping window to blend with the desktop environment or reduce visual distraction.

- **Settings Management:** The app supports saving and loading of user settings. All configuration options, including the selected game file, text color, font size, and window transparency, are saved in a JSON file. This ensures that preferences are retained across sessions.

- **Movable Window:** The ping display window can be freely moved around the screen. This feature enables users to position the window in a convenient spot, ensuring it does not obstruct their view of the game or other applications.

This application is ideal for gamers who want to monitor their connection quality without interrupting their gameplay experience. Its easy-to-use interface and customizable settings make it a versatile tool for managing and optimizing network performance.
