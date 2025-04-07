#!/bin/bash
# Run script for Discreet AI Coding Assistant
# This script checks for all necessary dependencies and runs the app in the appropriate mode

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Discreet AI Coding Assistant for macOS${NC}"
echo -e "${BLUE}================================================${NC}"

# Detect OS
OS="$(uname -s)"
if [ "$OS" != "Darwin" ]; then
    echo -e "${YELLOW}Warning: This application is designed for macOS.${NC}"
    echo -e "${YELLOW}Some features may not work correctly on $OS.${NC}"
    echo ""
fi

# Check for Python
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v $cmd >/dev/null 2>&1; then
        version=$($cmd --version 2>&1 | awk '{print $2}')
        major=$(echo $version | cut -d. -f1)
        minor=$(echo $version | cut -d. -f2)
        
        if [ "$major" -ge 3 ] && [ "$minor" -ge 7 ]; then
            PYTHON_CMD=$cmd
            echo -e "${GREEN}✓ Found Python $version${NC}"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}✗ Python 3.7+ not found. Please install Python 3.7 or higher.${NC}"
    exit 1
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️ OPENAI_API_KEY environment variable not found.${NC}"
    echo -e "${YELLOW}You can set it with: export OPENAI_API_KEY=\"your-api-key-here\"${NC}"
    echo ""
    
    # Prompt for API key
    read -p "Would you like to enter your OpenAI API key now? (y/n): " ENTER_KEY
    if [ "$ENTER_KEY" = "y" ] || [ "$ENTER_KEY" = "Y" ]; then
        read -p "Enter your OpenAI API key: " API_KEY
        if [ -n "$API_KEY" ]; then
            export OPENAI_API_KEY="$API_KEY"
            echo -e "${GREEN}✓ API key set for this session${NC}"
        else
            echo -e "${RED}No API key entered. The AI assistant will not function correctly.${NC}"
        fi
    else
        echo -e "${YELLOW}Continuing without API key. The AI assistant will not function correctly.${NC}"
    fi
    echo ""
fi

# Check for dependencies
echo "Checking for required packages..."
MISSING_PACKAGES=()

check_package() {
    $PYTHON_CMD -c "import $1" 2>/dev/null
    if [ $? -ne 0 ]; then
        MISSING_PACKAGES+=("$1")
        echo -e "${YELLOW}✗ $1 not found${NC}"
    else
        echo -e "${GREEN}✓ $1 found${NC}"
    fi
}

check_package "openai"
check_package "psutil"
check_package "pynput"

if [ "$OS" = "Darwin" ]; then
    # macOS-specific packages
    check_package "PyQt5"
    check_package "PyQt5.QtWidgets"
    echo "Checking for macOS-specific packages..."
    check_package "objc"
fi

# Install missing packages if needed
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Some required packages are missing.${NC}"
    read -p "Would you like to install them now? (y/n): " INSTALL_DEPS
    
    if [ "$INSTALL_DEPS" = "y" ] || [ "$INSTALL_DEPS" = "Y" ]; then
        echo "Installing missing packages..."
        for pkg in "${MISSING_PACKAGES[@]}"; do
            echo "Installing $pkg..."
            if [ "$pkg" = "objc" ]; then
                # PyObjC needs special handling
                $PYTHON_CMD -m pip install pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz
            else
                $PYTHON_CMD -m pip install $pkg
            fi
        done
        echo -e "${GREEN}✓ Packages installed${NC}"
    else
        echo -e "${YELLOW}Continuing without installing missing packages. Some features may not work.${NC}"
    fi
    echo ""
fi

# Check for macOS permissions
if [ "$OS" = "Darwin" ]; then
    echo "Checking macOS permissions..."
    
    # Check Accessibility permissions (required for keyboard monitoring)
    echo -e "${YELLOW}The application requires Accessibility permissions for keyboard shortcuts.${NC}"
    echo -e "${YELLOW}If keyboard shortcuts don't work, allow Terminal or StealthAI.app in:${NC}"
    echo -e "${YELLOW}System Preferences > Security & Privacy > Privacy > Accessibility${NC}"
    
    # Check Screen Recording permissions (for screen sharing detection)
    echo -e "${YELLOW}For optimal screen sharing detection, allow Terminal or StealthAI.app in:${NC}"
    echo -e "${YELLOW}System Preferences > Security & Privacy > Privacy > Screen Recording${NC}"
    echo ""
fi

# Determine which mode to run
echo "The application can be run in multiple modes:"
echo "1. Standard Mode (keyboard shortcut needed to show window)"
echo "2. Debug Mode (window shows immediately)"
echo "3. CLI Fallback Mode (text-based interface)"
echo "4. Create macOS App Bundle"
echo ""
read -p "Select a mode (1-4): " MODE

case $MODE in
    1)
        echo "Starting in Standard Mode..."
        echo "Press Command+Option+C (⌘+⌥+C) to show the assistant window"
        $PYTHON_CMD main.py
        ;;
    2)
        echo "Starting in Debug Mode..."
        echo "Window will be shown immediately"
        $PYTHON_CMD debug_mode.py
        ;;
    3)
        echo "Starting in CLI Fallback Mode..."
        $PYTHON_CMD fallback_mode.py
        ;;
    4)
        echo "Creating macOS App Bundle..."
        $PYTHON_CMD create_macos_app.py
        
        if [ -d "StealthAI.app" ]; then
            echo -e "${GREEN}✓ App bundle created: StealthAI.app${NC}"
            echo ""
            read -p "Would you like to run the app now? (y/n): " RUN_APP
            if [ "$RUN_APP" = "y" ] || [ "$RUN_APP" = "Y" ]; then
                echo "Starting StealthAI.app..."
                open StealthAI.app
            fi
        else
            echo -e "${RED}Failed to create app bundle.${NC}"
        fi
        ;;
    *)
        echo -e "${RED}Invalid option. Exiting.${NC}"
        exit 1
        ;;
esac

exit 0