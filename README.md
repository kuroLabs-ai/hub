# 🧩 KuroLabs Capability Hub

Welcome to the official **Kuro Capability Hub** repository hosted by [@kuroLabs-ai](https://github.com/kuroLabs-ai).

This repository serves as the **Central Online Catalog** for the KuroCode AI Agent ecosystem, providing plug-and-play **Tools**, **Plugins**, **Skills**, and **Integrations**.

---

## ⚡ How KuroCode Uses This Hub

Every KuroCode user can instantly discover, sync, and install capabilities from this hub directly in their terminal:

### 1. Sync the Latest Online Catalog
```bash
/store update
```
*KuroCode reaches this repository (`kuroLabs-ai/hub`) and synchronizes newly published puzzle pieces.*

### 2. Search & Browse Capabilities
```bash
/store list
/store search crypto
/store search metrics
```

### 3. Install Any Puzzle Piece
```bash
/store install regex_tester
/store install dependency_guard
/store install gitlab
```

### 4. Install Directly from URL
```bash
/store install https://raw.githubusercontent.com/kuroLabs-ai/hub/main/tools/regex_tester.py
```

---

## 📂 Repository Structure

```
hub/
├── catalog.json          # Master index of approved puzzle pieces
├── tools/                # Standalone Python tool scripts
├── plugins/              # Modular multi-file plugins
└── skills/               # Procedural workflow routines (SKILL.md)
```

---

## 🤝 Contributing a New Puzzle Piece

We welcome community puzzle pieces! To submit your tool, plugin, skill, or integration:

1. **Fork** this repository.
2. Add your puzzle piece entry into [`catalog.json`](catalog.json) following this schema:
   ```json
   {
     "id": "tool_your_tool_name",
     "name": "your_tool_name",
     "item_type": "tool",
     "description": "Clear explanation of what this tool does.",
     "version": "1.0.0",
     "author": "YourGitHubUsername",
     "tags": ["tag1", "tag2"],
     "payload": {
       "code": "def your_tool_name(...) -> dict:\n    ...",
       "entrypoint": "your_tool_name"
     }
   }
   ```
3. Submit a **Pull Request**. Once merged, your puzzle piece is immediately available to every KuroCode agent worldwide!

---

*Maintained with ❤️ by [KuroLabs](https://github.com/kuroLabs-ai).*
