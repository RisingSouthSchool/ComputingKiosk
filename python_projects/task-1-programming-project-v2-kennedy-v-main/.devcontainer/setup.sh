#!/bin/sh
# Post-create setup for GitHub Classroom Codespace

# Simple, clean shell prompt
echo 'PS1="\$ "' >> ~/.bashrc

# Apply machine-scope VS Code settings so they take precedence
mkdir -p ~/.vscode-remote/data/Machine
cp .devcontainer/settings.json ~/.vscode-remote/data/Machine/settings.json
