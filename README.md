<div align="left" style="position: relative;">
<h1>OLLAMA-GUI-PYTHON</h1>
<p align="left">
	<em><code>❯ GUI WITH OLLAMA</code></em>
</p>
<p align="left">
	<img src="https://camo.githubusercontent.com/9c890a042106e0f2dbc2129dc31941ea8d53449e567aa028532d51316a8b7820/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f6368796f6b2f6f6c6c616d612d677569" alt="license">
	<img src="https://img.shields.io/github/last-commit/alhmoraansel/Ollama-GUI-Py?style=flat-square&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/alhmoraansel/Ollama-GUI-Py?style=flat-square&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/alhmoraansel/Ollama-GUI-Py?style=flat-square&color=0080ff" alt="repo-language-count">
</p>
<p align="left">Built with the tools and technologies:</p>
<p align="left">
	<img src="https://img.shields.io/badge/HTML5-E34F26.svg?style=flat-square&logo=HTML5&logoColor=white" alt="HTML5">
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python">
</p>
</div>
<br clear="right">

## 🔗 Table of Contents

- [📍 Overview](#-overview)
- [👾 Features](#-features)
- [📁 Project Structure](#-project-structure)
  - [📂 Project Index](#-project-index)
- [🚀 Getting Started](#-getting-started)
  - [☑️ Prerequisites](#-prerequisites)
  - [⚙️ Installation](#-installation)
  - [🤖 Usage](#🤖-usage)
  - [🧪 Testing](#🧪-testing)
- [📌 Project Roadmap](#-project-roadmap)
- [🔰 Contributing](#-contributing)
- [🎗 License](#-license)
- [🙌 Acknowledgments](#-acknowledgments)

---

## 📍 Overview

- Ollama is messy with commandline
- How to use ollama? - [Read this guide made by me](https://docs.google.com/document/d/1Qn2j3qRyU1Mjof-7TCX9Y4QjOosOogjCr1NzjuIS8rg/edit?usp=sharing) (for an extremely useful tool (Hint:Uncensor Deepseek) and installation steps)
- No option to store history of chats for further referneces
- Therefore, I forked a repo (https://github.com/chyok/ollama-gui) and modified it to have commonly used functions. This app comes with built in global shortcuts, easy to modify code, and chat history management at user's disposal. Add this to your arsenal to enhance ollama experience.

---

## 👾 Features

1. Chatbox in notepad-like editor format
2. Edit any message and requestion the downloaded AI
3. Export to PDF option
4. Completely manage all of the Model related stuff in-app
5. Download models
6. check currently loaded models in memory
7. Automatic cleanup on exit the program
8. Automatic Startup ollama on start of program
9. Global shortcuts for managements
10. No installation needed, no telemetry, privacy kept in mind.
11. Automatic backup of chat history in human-readable JSON file format.
12. Restore chat history in standard JSON format.


## 📁 Project Structure

```sh
└── ollama-gui-python/
    ├── build
    │   └── exe.win-amd64-3.13
    │   |     └── main_logic.exe
    ├── gui.py
    ├── icon.ico
    ├── main_logic.py
    └── shared_globals.py
```
---
## 🚀 Getting Started

### ☑️ Prerequisites

Before getting started with ollama-gui-python, ensure your runtime environment meets the following requirements:

- **Programming Language:** Required for development ->Python 3.13, and pip dependencies as => bs4, reportlab,markdown,json,keyboard, AppOpener, and cxfreeze for building the executable

- _NOTE_: for running executable, Python is not required but recommended


### ⚙️ Installation

Install ollama-gui-python using one of the following methods:

**Direct download from release**
1. extract the zip file and run main_logic.exe.
2. _chats folder shall display history of chats

**Build from source:**

1. Clone the ollama-gui-python repository:
```sh
git clone https://github.com/alhmoraansel/ollama-gui-python
```

2. Navigate to the project directory:
```sh
cd ollama-gui-python
```

3. Install the project dependencies:
```sh
pip install bs4; reportlab; keyboard; AppOpener
```

### 🤖 Usage
Run ollama-gui-python using the following command:
```sh
py main_logic.py
```
---
## 📌 Project Roadmap

- [X] **`Task 1`**: <strike>BASIC chat feature with PDF Export and storing history option</strike>
- [ ] **`Task 2`**: Loading Pictures with chats
- [ ] **`Task 3`**: Expanding it to use GGUF models too, expanding horizons.

---

## 🔰 Contributing

- **💬 [Join the Discussions](https://github.com/alhmoraansel/ollama-gui-python/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/alhmoraansel/ollama-gui-python/issues)**: Submit bugs found or log feature requests for the `ollama-gui-python` project.
- **💡 [Submit Pull Requests](https://github.com/alhmoraansel/ollama-gui-python/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.
- **Contact Developer: (detgdaac@pm.me)**

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/alhmoraansel/ollama-gui-python
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/alhmoraansel/ollama-gui-python/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=alhmoraansel/ollama-gui-python">
   </a>
</p>
</details>

---

## 🎗 License

This project is protected under the [MIT](https://mit-license.org/) License. For more details, refer to the [LICENSE](https://mit-license.org/) file.

---

## 🙌 Acknowledgments
---
- [Ollama](https://github.com/ollama/ollama)
- [Appopener](https://github.com/athrvvvv/AppOpener)
- [Reportlab JSON2PDF](https://docs.reportlab.com/json2pdf/)
- [tkinter](https://docs.python.org/3/library/tkinter.html)
- [chyok](https://github.com/chyok/ollama-gui)

---
