# Core-Framework Guidelines

# Documentation Compilation

## Python Command Line Interface (CLI)

[What are CLI's](https://realpython.com/command-line-interfaces-python-argparse/)

[Argparse or Click CLI](https://towardsdatascience.com/how-to-write-user-friendly-command-line-interfaces-in-python-cc3a6444af8e)

### Git / GitHub

[Git Refresher](https://www.theodinproject.com/lessons/foundations-setting-up-git)

### APIS

[Writing an API in Python](https://towardsdatascience.com/the-right-way-to-build-an-api-with-python-cd08ab285f8f)

## Youtube Videos for Easier Understanding

[Click-Based CLI](https://www.youtube.com/watch?v=TVFO2ABZqK8&t=996s)

[Git Tutorial](https://www.youtube.com/watch?v=RGOj5yH7evk)

[Intro to PyBind (Python -> C++)](https://www.youtube.com/watch?v=_5T70cAXDJ0)

# Goals

The main goal of the Core-Framework team is to deal with information management. We need to keep track of trades, balances, and holdings taken from teams across the board.

# IMPORTANT: do this through the api response calls, to ensure that inter-language data management is not required.

# Broad Steps

1. Build in data storage and variables w/ local storage as well.
2. Analyze and store server health data vs. time.
3. Generate time series data about server health metrics
4. Analyze and store Jenkins time series as well.
5. Build structures to route data through the system.
6. Network w/ Data Sockets team to move data through mp queue.
7. Work with Execution Platform to get data logged
8. Work with Backtesters to store and move logs.

### Initial Steps

1. While we're waiting for the rest of the teams, start work on the CLI, build the data offboarding from data, constant state things, and essentially everything that you can while waiting on the others.
2. Put a team onto hooking onto a simple add script in C++ with Python.
3. Prioritize I/O before everything else, work with other PMs to get that out.
4. Build out from there - allocate devs into what is falling behind, build the central script as it goes.
5. Implement connections between Data and the rest of the files through your central script.

### Beneficial Practices

1. Write documentation!!!
   - Include this before every function: """_description of what function does_"""
   - Don't make it too long though; Ethan will slaughter us
2. Create unit tests that ensure the code doesn't break Prod env
3. Ask me if you have any info-framework-related questions. Even the most basic clarification ones! If I don't know it, we can figure it out together!
