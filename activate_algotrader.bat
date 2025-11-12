@echo off
echo.
echo ========================================
echo   Activating Moon Dev AI Agents
echo   Environment: algotrader (Python 3.10.9)
echo ========================================
echo.

call conda activate algotrader

if errorlevel 1 (
    echo Error: Could not activate algotrader environment
    echo Please make sure conda is installed and run: conda init
    pause
    exit /b 1
)

echo Environment activated successfully!
echo.
echo You can now run the agents, for example:
echo   python src/agents/rbi_agent_pp_multi.py
echo.
echo Type 'deactivate' to exit the environment
echo.

cd /d "G:\Drive'ım\Moondev_AI_agents\moon-dev-ai-agents"
cmd /k
