#!/usr/bin/env python3
"""
Test suite for Seldon features
Test-first approach - write tests before implementation
"""

import os
import sys
import json
import tempfile
import shutil
import subprocess
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Import Seldon by executing the file
exec(open('./seldon').read(), globals())
# Now Seldon class is available


class TestSeldonAnalyze(unittest.TestCase):
    """Test the analyze command functionality"""
    
    def setUp(self):
        """Create temporary Seldon directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize Seldon
        self.seldon = Seldon()
        self.seldon.init()
        
        # Create test data
        self._create_test_execution_history()
    
    def tearDown(self):
        """Clean up test directory"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def _create_test_execution_history(self):
        """Create test execution history with patterns"""
        # Add multiple async failures
        self.seldon.execute("Add async function")
        self.seldon.reflect(
            failure=True,
            context="Added async function without await",
            error="TypeError: Cannot read property 'data' of undefined - missing await",
            execution_id="test_exec_1"
        )
        
        self.seldon.execute("Fix async error handling")
        self.seldon.reflect(
            failure=True,
            context="Forgot await in try block",
            error="Unhandled promise rejection - await missing",
            execution_id="test_exec_2"
        )
        
        # Add null errors
        self.seldon.execute("Process user data")
        self.seldon.reflect(
            failure=True,
            context="Accessing nested property",
            error="Cannot read property 'name' of null",
            execution_id="test_exec_3"
        )
        
        self.seldon.execute("Display user info")
        self.seldon.reflect(
            failure=True,
            context="No null check",
            error="TypeError: Cannot read property 'email' of undefined",
            execution_id="test_exec_4"
        )
        
        # Add successes
        self.seldon.execute("Add logging")
        self.seldon.reflect(
            failure=False,
            context="Added console logging",
            execution_id="test_exec_5"
        )
    
    def test_analyze_finds_async_patterns(self):
        """Test that analyze correctly identifies async/await patterns"""
        analysis = self.seldon.analyze_patterns(apply=False)
        
        # Check that async pattern was found
        async_patterns = [p for p in analysis['pattern_generalizations'] 
                         if 'async' in p['pattern'].lower()]
        self.assertEqual(len(async_patterns), 1)
        
        # Check confidence and rule quality
        async_pattern = async_patterns[0]
        self.assertGreaterEqual(async_pattern['confidence'], 0.8)
        self.assertIn('await', async_pattern['rule'])
        self.assertIn('2 async-related failures', async_pattern['based_on'])
    
    def test_analyze_finds_null_patterns(self):
        """Test that analyze correctly identifies null checking patterns"""
        analysis = self.seldon.analyze_patterns(apply=False)
        
        # Check that null pattern was found
        null_patterns = [p for p in analysis['pattern_generalizations'] 
                        if 'null' in p['pattern'].lower()]
        self.assertEqual(len(null_patterns), 1)
        
        # Check the pattern details
        null_pattern = null_patterns[0]
        self.assertIn('optional chaining', null_pattern['rule'])
        self.assertIn('2 null-related failures', null_pattern['based_on'])
    
    def test_analyze_applies_generalizations(self):
        """Test that --apply flag correctly updates the prompt"""
        # Get initial pattern count
        with open(self.seldon.seldon_dir / 'learnings' / 'history.json', 'r') as f:
            initial_patterns = len(json.load(f)['patterns'])
        
        # Apply generalizations
        self.seldon.analyze_patterns(apply=True)
        
        # Check patterns were added
        with open(self.seldon.seldon_dir / 'learnings' / 'history.json', 'r') as f:
            final_patterns = len(json.load(f)['patterns'])
        
        self.assertGreater(final_patterns, initial_patterns)
        self.assertGreaterEqual(final_patterns - initial_patterns, 2)  # At least 2 generalizations


class TestSeldonEvolution(unittest.TestCase):
    """Test the evolution command functionality"""
    
    def setUp(self):
        """Create temporary Seldon directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize Seldon
        self.seldon = Seldon()
        self.seldon.init()
        
        # Create evolution history
        self._create_evolution_history()
    
    def tearDown(self):
        """Clean up test directory"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def _create_evolution_history(self):
        """Create prompt evolution history"""
        # Simulate multiple prompt evolutions
        for i in range(3):
            self.seldon.execute(f"Task {i}")
            self.seldon.reflect(
                failure=True,
                context=f"Failed task {i}",
                error=f"Error {i}",
                execution_id=f"exec_{i}"
            )
    
    def test_evolution_shows_all_versions(self):
        """Test that evolution shows all prompt versions"""
        # Capture output
        from io import StringIO
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.seldon.show_evolution()
            output = mock_stdout.getvalue()
        
        # Check that multiple versions are shown
        self.assertIn("Version 1:", output)
        self.assertIn("Version 2:", output)
        self.assertIn("Total versions:", output)
        
        # Check version details
        self.assertIn("Created:", output)
        self.assertIn("Patterns:", output)
        self.assertIn("Changes from previous:", output)
    
    def test_evolution_tracks_pattern_growth(self):
        """Test that evolution correctly tracks pattern count growth"""
        tracking_file = self.seldon.seldon_dir / 'executions' / 'tracking.json'
        with open(tracking_file, 'r') as f:
            tracking = json.load(f)
        
        # Get pattern counts from versions
        pattern_counts = []
        for version in tracking['prompt_versions'].values():
            pattern_counts.append(version.get('patterns_count', 0))
        
        # Pattern count should generally increase (or stay same)
        sorted_counts = sorted(pattern_counts)
        self.assertEqual(pattern_counts[0], sorted_counts[0])  # First should be minimum


class TestSeldonCodeCommand(unittest.TestCase):
    """Test the code command with VCS integration"""
    
    def setUp(self):
        """Create temporary Seldon directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize Seldon
        self.seldon = Seldon()
        self.seldon.init()
        
        # Initialize git repo for testing
        subprocess.run(['git', 'init'], capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], capture_output=True)
    
    def tearDown(self):
        """Clean up test directory"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_code_detects_git(self):
        """Test that code command correctly detects git"""
        vcs_type = self.seldon._detect_vcs()
        self.assertEqual(vcs_type, 'git')
    
    def test_code_command_with_failing_test(self):
        """Test code command behavior with failing tests"""
        # Create a test file that will fail
        with open('failing_test.py', 'w') as f:
            f.write('assert False, "This test always fails"')
        
        # Run code command
        success, message = self.seldon.code_with_reversion(
            task="Fix the failing test",
            test_cmd="python3 failing_test.py",
            no_revert=False
        )
        
        # Should fail and learn from it
        self.assertFalse(success)
        self.assertIn("Tests failed", message)
        
        # Check that a pattern was learned
        with open(self.seldon.seldon_dir / 'learnings' / 'history.json', 'r') as f:
            learnings = json.load(f)
            self.assertGreater(len(learnings['failures']), 0)
    
    def test_code_command_with_passing_test(self):
        """Test code command behavior with passing tests"""
        # Create a test file that will pass
        with open('passing_test.py', 'w') as f:
            f.write('assert True, "This test always passes"')
        
        # Run code command
        success, message = self.seldon.code_with_reversion(
            task="Run the passing test",
            test_cmd="python3 passing_test.py",
            no_revert=False
        )
        
        # Should succeed
        self.assertTrue(success)
        self.assertIn("Tests passed", message)
        
        # Check that success was recorded
        with open(self.seldon.seldon_dir / 'learnings' / 'history.json', 'r') as f:
            learnings = json.load(f)
            self.assertGreater(len(learnings['successes']), 0)


class TestPromptEvolutionStorage(unittest.TestCase):
    """Test prompt version storage and retrieval"""
    
    def setUp(self):
        """Create temporary Seldon directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize Seldon
        self.seldon = Seldon()
        self.seldon.init()
    
    def tearDown(self):
        """Clean up test directory"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_prompt_hash_generation(self):
        """Test that prompt hashes are generated correctly"""
        # Get initial hash
        hash1 = self.seldon._get_prompt_hash()
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 12)  # We truncate to 12 chars
        
        # Modify prompt and check hash changes
        self.seldon.reflect(True, "Test", "Error")
        hash2 = self.seldon._get_prompt_hash()
        self.assertNotEqual(hash1, hash2)
    
    def test_prompt_version_archiving(self):
        """Test that prompt versions are archived correctly"""
        # Create some prompt evolution
        self.seldon.execute("Test task")
        self.seldon.reflect(True, "Failed", "Error", "test_exec")
        
        # Check that versions were archived
        tracking_file = self.seldon.seldon_dir / 'executions' / 'tracking.json'
        with open(tracking_file, 'r') as f:
            tracking = json.load(f)
        
        self.assertIn('prompt_versions', tracking)
        self.assertGreater(len(tracking['prompt_versions']), 0)
        
        # Check version content
        for version in tracking['prompt_versions'].values():
            self.assertIn('content', version)
            self.assertIn('created', version)
            self.assertIn('patterns_count', version)


class TestSeldonHelperMethods(unittest.TestCase):
    """Test helper methods and utilities"""
    
    def setUp(self):
        """Create temporary Seldon directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize Seldon
        self.seldon = Seldon()
        self.seldon.init()
    
    def tearDown(self):
        """Clean up test directory"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_add_pattern_if_new(self):
        """Test that patterns are only added if they're new"""
        pattern = "Test pattern: always do X"
        
        # Add pattern first time
        self.seldon._add_pattern_if_new(pattern)
        
        with open(self.seldon.seldon_dir / 'learnings' / 'history.json', 'r') as f:
            patterns1 = json.load(f)['patterns']
        
        # Try to add same pattern again
        self.seldon._add_pattern_if_new(pattern)
        
        with open(self.seldon.seldon_dir / 'learnings' / 'history.json', 'r') as f:
            patterns2 = json.load(f)['patterns']
        
        # Should not duplicate
        self.assertEqual(len(patterns1), len(patterns2))
        self.assertEqual(patterns1.count(pattern), 1)
    
    def test_get_pattern_effectiveness(self):
        """Test pattern effectiveness calculation"""
        # Create executions with attributions
        tracking_file = self.seldon.seldon_dir / 'executions' / 'tracking.json'
        with open(tracking_file, 'r') as f:
            tracking = json.load(f)
        
        # Add test execution with attribution
        tracking['executions'].append({
            'id': 'test_1',
            'attribution': {'pattern1': 1.0, 'pattern2': -1.0}
        })
        tracking['executions'].append({
            'id': 'test_2', 
            'attribution': {'pattern1': 1.0}
        })
        
        with open(tracking_file, 'w') as f:
            json.dump(tracking, f)
        
        # Get effectiveness
        effectiveness = self.seldon.get_pattern_effectiveness()
        
        self.assertIn('pattern1', effectiveness)
        self.assertIn('pattern2', effectiveness)
        self.assertEqual(effectiveness['pattern1']['success_rate'], 1.0)
        self.assertEqual(effectiveness['pattern2']['success_rate'], 0.0)


if __name__ == '__main__':
    unittest.main()