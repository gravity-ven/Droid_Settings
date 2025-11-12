#!/usr/bin/env python3
"""
Claude Watcher System Agent
Extracted from gravity-ven/Claude_Code repository

Advanced monitoring and response system for Claude Code operations.
Handles build results, test results, process completion, and output parsing.
"""

import json
import logging
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class WatcherEvent:
    """Watcher system event structure"""
    event_type: str
    timestamp: datetime
    source: str
    data: Dict
    status: str = "pending"
    action_required: bool = False

class ClaudeWatcherSystemAgent:
    """
    Claude Watcher System Agent for monitoring and response automation
    Features:
    - Build result monitoring and parsing
    - Test result analysis and reporting
    - Process completion tracking
    - Claude output parsing for structured data extraction
    - Automated response actions
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.events = []
        self.active_watchers = {}
        self.response_handlers = {}
        
        # Initialize watcher handlers
        self._initialize_handlers()
        
    def _initialize_handlers(self):
        """Initialize specialized handlers for different event types"""
        self.response_handlers = {
            "build_result": self._handle_build_result,
            "test_results": self._handle_test_results,
            "process_completion": self._handle_process_completion,
            "claude_output": self._handle_claude_output
        }
    
    def parse_claude_output(self, output_text: str) -> Dict:
        """
        Parse Claude Code output for structured information
        Based on parse_claude_output.py from Claude_Code repository
        """
        result = {
            "status": "unknown",
            "success": False,
            "errors": [],
            "warnings": [],
            "actions_needed": [],
            "completions": [],
            "metadata": {
                "parse_time": datetime.now().isoformat(),
                "text_length": len(output_text)
            }
        }
        
        # Check for completion markers
        if "<<COMPLETE>>" in output_text or "Task completed" in output_text:
            result["status"] = "complete"
            result["success"] = True
        elif "<<ERROR>>" in output_text or "Error:" in output_text:
            result["status"] = "error"
            result["success"] = False
        elif "<<PENDING>>" in output_text:
            result["status"] = "pending"
            result["success"] = False
        else:
            result["status"] = "in_progress"
            result["success"] = False
        
        # Extract errors with multiple patterns
        error_patterns = [
            r'Error:\s*(.+)',
            r'ERROR:\s*(.+)',
            r'<<ERROR>>\s*(.+)',
            r'Failed:\s*(.+)',
            r'Exception:\s*(.+)'
        ]
        
        import re
        for pattern in error_patterns:
            matches = re.findall(pattern, output_text, re.MULTILINE | re.DOTALL)
            result["errors"].extend([m.strip() for m in matches])
        
        # Extract warnings
        warning_patterns = [
            r'Warning:\s*(.+)',
            r'WARNING:\s*(.+)',
            r'<<WARNING>>\s*(.+)',
            r'Caution:\s*(.+)'
        ]
        
        for pattern in warning_patterns:
            matches = re.findall(pattern, output_text, re.MULTILINE | re.DOTALL)
            result["warnings"].extend([m.strip() for m in matches])
        
        # Extract action items
        action_patterns = [
            r'Action needed:\s*(.+)',
            r'To do:\s*(.+)',
            r'Next steps?:\s*(.+)',
            r'<<ACTION>>\s*(.+)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, output_text, re.MULTILINE | re.DOTALL)
            result["actions_needed"].extend([m.strip() for m in matches])
        
        # Extract completion items
        completion_patterns = [
            r'Completed:\s*(.+)',
            r'Finished:\s*(.+)',
            r'Done:\s*(.+)',
            r'<<COMPLETED>>\s*(.+)'
        ]
        
        for pattern in completion_patterns:
            matches = re.findall(pattern, output_text, re.MULTILINE | re.DOTALL)
            result["completions"].extend([m.strip() for m in matches])
        
        # Extract metadata
        if "File:" in output_text:
            file_matches = re.findall(r'File:\s*(.+)', output_text)
            if file_matches:
                result["metadata"]["files"] = [f.strip() for f in file_matches]
        
        if "Line:" in output_text:
            line_matches = re.findall(r'Line:\s*(\d+)', output_text)
            if line_matches:
                result["metadata"]["line_numbers"] = [int(l) for l in line_matches]
        
        return result
    
    def parse_build_output(self, build_log: str) -> Dict:
        """
        Parse build output for errors, warnings, and success indicators
        Based on parse_build_output.py from Claude_Code repository
        """
        result = {
            "build_status": "unknown",
            "success": False,
            "errors": [],
            "warnings": [],
            "compilation_errors": [],
            "linkage_errors": [],
            "files_processed": [],
            "build_time": None,
            "metadata": {}
        }
        
        lines = build_log.split('\n')
        total_lines = len(lines)
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Detect build status markers
            if "BUILD SUCCESS" in line.upper() or "Build succeeded" in line:
                result["build_status"] = "success"
                result["success"] = True
            elif "BUILD FAILED" in line.upper() or "Build failed" in line:
                result["build_status"] = "failed"
                result["success"] = False
            
            # Extract compilation errors
            if "error:" in line.lower() or "fatal error:" in line.lower():
                # Extract file and line if available
                file_match = line.split(':')[0] if ':' in line else "unknown"
                line_match = line.split(':')[1] if line.count(':') > 1 else "unknown"
                
                error_info = {
                    "message": line,
                    "file": file_match,
                    "line": line_match if line_match.isdigit() else None,
                    "line_number": line_num
                }
                result["compilation_errors"].append(error_info)
            
            # Extract warnings
            if "warning:" in line.lower() and "error:" not in line.lower():
                result["warnings"].append({
                    "message": line,
                    "line_number": line_num
                })
            
            # Extract linkage errors
            if "undefined reference" in line.lower() or "linker error" in line.lower():
                result["linkage_errors"].append({
                    "message": line,
                    "line_number": line_num
                })
            
            # Track files being processed
            if line.endswith(".c") or line.endswith(".cpp") or line.endswith(".h"):
                result["files_processed"].append(line)
        
        result["metadata"]["total_lines"] = total_lines
        result["metadata"]["error_count"] = len(result["compilation_errors"])
        result["metadata"]["warning_count"] = len(result["warnings"])
        result["metadata"]["files_count"] = len(result["files_processed"])
        
        return result
    
    def parse_test_results(self, test_output: str) -> Dict:
        """
        Parse test output for results, failures, and coverage
        Based on parse_test_results.py from Claude_Code repository
        """
        result = {
            "test_status": "unknown",
            "success": False,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "test_suites": {},
            "failures": [],
            "coverage": {},
            "execution_time": None
        }
        
        lines = test_output.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract test counts
            import re
            
            # Pattern for "X tests ran, Y passed, Z failed"
            count_match = re.search(r'(\d+)\s+tests?.*?(\d+)\s+passed.*?(\d+)\s+failed', line, re.IGNORECASE)
            if count_match:
                result["total_tests"] = int(count_match.group(1))
                result["passed_tests"] = int(count_match.group(2))
                result["failed_tests"] = int(count_match.group(3))
            
            # Pattern for "OK" or "PASS"
            if "OK" in line.upper() or "PASS" in line.upper() and result["test_status"] != "failed":
                result["test_status"] = "passed"
                result["success"] = True
            
            # Pattern for "FAIL" or "FAILED"
            if "FAIL" in line.upper() and "PASS" not in line.upper():
                result["test_status"] = "failed"
                result["success"] = False
            
            # Extract execution time
            time_match = re.search(r'(\d+(?:\.\d+)?)\s*[^a-z]*?(s|seconds?|ms|milliseconds?)', line, re.IGNORECASE)
            if time_match:
                time_value = float(time_match.group(1))
                time_unit = time_match.group(2).lower()
                if time_unit.startswith('ms'):
                    result["execution_time"] = time_value / 1000.0  # Convert to seconds
                else:
                    result["execution_time"] = time_value
            
            # Extract failures details
            if "FAIL:" in line or "FAILURE:" in line:
                result["failures"].append(line)
        
        # Calculate skipped tests
        result["skipped_tests"] = result["total_tests"] - result["passed_tests"] - result["failed_tests"]
        
        return result
    
    def _handle_build_result(self, event: WatcherEvent) -> Dict:
        """Handle build result event"""
        build_data = event.data.get("build_log", "")
        parsed = self.parse_build_output(build_data)
        
        response = {
            "action": "review_build",
            "build_analysis": parsed,
            "next_steps": []
        }
        
        if not parsed["success"]:
            response["next_steps"] = [
                "Review compilation errors",
                "Fix syntax issues",
                "Rebuild project"
            ]
        else:
            response["next_steps"] = [
                "Run tests",
                "Continue with deployment"
            ]
        
        return response
    
    def _handle_test_results(self, event: WatcherEvent) -> Dict:
        """Handle test results event"""
        test_data = event.data.get("test_output", "")
        parsed = self.parse_test_results(test_data)
        
        response = {
            "action": "review_tests",
            "test_analysis": parsed,
            "next_steps": []
        }
        
        if not parsed["success"] or parsed["failed_tests"] > 0:
            response["next_steps"] = [
                f"Fix {parsed['failed_tests']} failing tests",
                "Investigate test failures",
                "Re-run test suite"
            ]
        else:
            response["next_steps"] = [
                "Update documentation",
                "Prepare for release"
            ]
        
        return response
    
    def _handle_process_completion(self, event: WatcherEvent) -> Dict:
        """Handle process completion event"""
        process_data = event.data
        exit_code = process_data.get("exit_code", 0)
        
        response = {
            "action": "process_completed",
            "exit_code": exit_code,
            "success": exit_code == 0,
            "next_steps": []
        }
        
        if exit_code == 0:
            response["next_steps"] = [
                "Log success",
                "Continue workflow"
            ]
        else:
            response["next_steps"] = [
                "Investigate failure",
                "Check error logs",
                "Restart process if needed"
            ]
        
        return response
    
    def _handle_claude_output(self, event: WatcherEvent) -> Dict:
        """Handle Claude output event"""
        output_data = event.data.get("output", "")
        parsed = self.parse_claude_output(output_data)
        
        response = {
            "action": "process_claude_output",
            "output_analysis": parsed,
            "next_steps": []
        }
        
        # Determine actions based on status
        if parsed["status"] == "complete":
            response["next_steps"] = [
                "Archive completed work",
                "Update progress tracking"
            ]
        elif parsed["status"] == "error":
            response["next_steps"] = [
                f"Address {len(parsed['errors'])} errors",
                "Retry task if appropriate"
            ]
            response["action_required"] = True
        elif parsed["status"] == "pending":
            response["next_steps"] = [
                f"Complete {len(parsed['actions_needed'])} action items",
                "Continue working on task"
            ]
            response["action_required"] = True
        
        return response
    
    def add_event(self, event_type: str, source: str, data: Dict) -> str:
        """Add a new event to the watcher system"""
        event = WatcherEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            source=source,
            data=data
        )
        
        self.events.append(event)
        
        # Process event through appropriate handler
        if event_type in self.response_handlers:
            response = self.response_handlers[event_type](event)
            event.action_required = response.get("action_required", False)
            return response
        else:
            return {"action": "unknown_event_type", "event": event.__dict__}
    
    def get_active_events(self) -> List[Dict]:
        """Get all active events needing attention"""
        return [
            {
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source,
                "action_required": event.action_required
            }
            for event in self.events
            if event.action_required or event.status == "pending"
        ]
    
    def get_system_status(self) -> Dict:
        """Get overall watcher system status"""
        total_events = len(self.events)
        pending_events = len([e for e in self.events if e.status == "pending"])
        action_required_events = len([e for e in self.events if e.action_required])
        
        return {
            "total_events": total_events,
            "pending_events": pending_events,
            "action_required_events": action_required_events,
            "active_watchers": list(self.active_watchers.keys()),
            "event_types": list(self.response_handlers.keys()),
            "last_update": datetime.now().isoformat()
        }

# Export for Factory Droid integration
def create_claude_watcher_system(config_path: Optional[str] = None):
    """Factory function to create Claude Watcher System Agent"""
    config = None
    if config_path:
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    return ClaudeWatcherSystemAgent(config)

if __name__ == "__main__":
    # Demo usage
    watcher = ClaudeWatcherSystemAgent()
    
    # Test Claude output parsing
    sample_output = """
    <<COMPLETE>> Task completed successfully
    File: src/main.py
    Line: 42
    
    Warning: Variable 'x' is unused
    Error: Division by zero in line 15
    Action needed: Add error handling for division
    """
    
    parsed = watcher.parse_claude_output(sample_output)
    print("Parsed Claude Output:", json.dumps(parsed, indent=2))
    
    # Add event
    response = watcher.add_event("claude_output", "demo", {"output": sample_output})
    print("\nEvent Response:", json.dumps(response, indent=2))
    
    print("\nSystem Status:", json.dumps(watcher.get_system_status(), indent=2))
