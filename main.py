import os
import asyncio
from input.stt import SpeechToText
from processing.nlu import NLUProcessor
from processing.dispatcher import CommandDispatcher
from output.tts import TextToSpeech
from utils.logger import setup_logger
from utils.config_handler import ConfigHandler
from modules.ai_integration import AIModelManager
from utils.error_handler import with_error_handling
from utils.command_history import CommandHistory
from modules.ide_integration import IDEIntegration
from modules.code_intelligence import CodeIntelligence
from modules.workspace_manager import WorkspaceManager
from modules.task_automation import TaskAutomation
from modules.project_manager import ProjectManager
from modules.test_runner import TestRunner
from modules.code_reviewer import CodeReviewer
from modules.doc_generator import DocGenerator
from modules.debug_assistant import DebugAssistant
from modules.performance_monitor import PerformanceMonitor
from modules.code_search import CodeSearch
from modules.dependency_manager import DependencyManager
from rich.console import Console
from rich.table import Table
from datetime import datetime

class Canopus:
    def __init__(self):
        self.config = ConfigHandler()
        self.logger = setup_logger()
        self.stt = SpeechToText()
        self.nlu = NLUProcessor()
        self.dispatcher = CommandDispatcher()
        self.tts = TextToSpeech()
        self.ai_manager = AIModelManager(self.config.get('ai', {}).get('azure', {}))
        self.command_history = CommandHistory()
        workspace_path = self.config.get('workspace', {}).get('path', os.getcwd())
        self.workspace_manager = WorkspaceManager(workspace_path)
        self.ide_integration = IDEIntegration(workspace_path)
        self.code_intelligence = CodeIntelligence(workspace_path)
        self.task_automation = TaskAutomation(workspace_path)
        self.project_manager = ProjectManager(workspace_path)
        self.test_runner = TestRunner(workspace_path)
        self.code_reviewer = CodeReviewer()
        self.doc_generator = DocGenerator(workspace_path)
        self.debug_assistant = DebugAssistant()
        self.performance_monitor = PerformanceMonitor()
        self.code_search = CodeSearch(workspace_path)
        self.dependency_manager = DependencyManager(workspace_path)
        self.performance_monitor.start_monitoring()

    @with_error_handling
    async def start(self):
        self.logger.info("Starting Canopus Voice Assistant...")
        try:
            self.tts.start()
            self.stt.start_listening()
            
            # Main loop instead of GUI
            while True:
                command = await self.process_audio_queue()
                if command:
                    response = await self.process_command(command)
                    self.tts.speak(response)
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            await self.cleanup()
        except Exception as e:
            self.logger.error(f"Error starting Canopus: {e}")
            await self.cleanup()
            raise
            
    async def handle_command(self, text: str):
        try:
            response = await self.process_command(text)
            return response
        except Exception as e:
            self.logger.error(f"Error processing command: {str(e)}")
            return f"Error processing command: {str(e)}"
            
    async def process_audio_queue(self):
        # Process audio queue logic here
        return self.stt.audio_queue.get() if not self.stt.audio_queue.empty() else None
        
    @with_error_handling
    async def process_command(self, text: str):
        nlu_result = self.nlu.process(text)
        
        # Handle task automation commands
        if "run task" in text.lower():
            task_name = nlu_result.get("entities", {}).get("task_name")
            if task_name:
                result = await self.task_automation.run_task(task_name)
                return f"Task {task_name} completed with status: {result['status']}"
                
        # Handle project management commands
        if "project status" in text.lower():
            summary = self.project_manager.get_project_summary()
            return f"Project {summary['name']} has {summary['tasks_count']} tasks and {summary['coverage']}% test coverage"
            
        # Handle test commands
        if "run tests" in text.lower():
            result = await self.test_runner.run_tests()
            return f"Tests completed with {result['coverage']}% coverage"
        
        # Handle IDE-specific commands
        if "open file" in text.lower():
            filename = nlu_result.get("entities", {}).get("filename")
            if filename:
                file_path = self.workspace_manager.find_file(filename)
                if file_path:
                    self.ide_integration.open_file(str(file_path))
                    return f"Opening {filename}"
                return f"File {filename} not found"
                
        # Handle code intelligence commands
        if "find references" in text.lower():
            symbol = nlu_result.get("entities", {}).get("symbol")
            if symbol:
                refs = self.code_intelligence.find_references(symbol)
                return f"Found {len(refs)} references to {symbol}"
        
        # Handle code review commands
        if "review code" in text.lower():
            file_path = nlu_result.get("entities", {}).get("file_path")
            if file_path:
                review = self.code_reviewer.review_file(file_path)
                return f"Code review completed. Found {len(review['issues'])} issues"
                
        # Handle documentation commands
        if "generate docs" in text.lower():
            module_path = nlu_result.get("entities", {}).get("module_path")
            if module_path:
                docs = self.doc_generator.generate_docs(module_path)
                return f"Documentation generated for {module_path}"
        
        # Handle debugging commands
        if "debug error" in text.lower():
            last_exception = nlu_result.get("entities", {}).get("exception")
            if last_exception:
                analysis = self.debug_assistant.analyze_exception(last_exception)
                return f"Error analysis: {analysis['type']} - {analysis['suggestions'][0]}"
                
        # Handle performance commands
        if "system status" in text.lower():
            metrics = self.performance_monitor.collect_metrics()
            return f"CPU: {metrics['cpu']['percent']}%, Memory: {metrics['memory']['percent']}%"
        
        # Handle code search commands
        if "search code" in text.lower():
            query = nlu_result.get("entities", {}).get("query")
            if query:
                results = self.code_search.search(query)
                return f"Found {len(results)} matches. Best match: {results[0].snippet}"
                
        # Handle dependency commands
        if "check dependencies" in text.lower():
            analysis = self.dependency_manager.analyze_dependencies()
            outdated = len(analysis['outdated'])
            security = len(analysis['security_issues'])
            return f"Found {outdated} outdated packages and {security} security issues"

        response = self.dispatcher.dispatch(nlu_result)
        self.command_history.add_command(
            text,
            response,
            success=response != "No handler found for intent"
        )
        return response

    def display_command_history(self, history):
        """Display command history in a formatted table"""
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        
        table.add_column("Time", style="dim")
        table.add_column("Command")
        table.add_column("Response")
        table.add_column("Status", justify="right")
        
        for entry in history:
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%H:%M:%S')
            status_style = "green" if entry['success'] else "red"
            status = "✓" if entry['success'] else "✗"
            
            table.add_row(
                timestamp,
                entry['command'],
                entry['result'][:50] + "..." if len(entry['result']) > 50 else entry['result'],
                f"[{status_style}]{status}[/{status_style}]"
            )
        
        console.print("\n=== Command History ===")
        console.print(table)
        console.print("\n")
        
    async def cleanup(self):
        self.logger.info("Shutting down Canopus...")
        self.stt.stop_listening()
        self.tts.stop()
        self.performance_monitor.stop_monitoring()
        
if __name__ == "__main__":
    assistant = Canopus()    
    asyncio.run(assistant.start())
