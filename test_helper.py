#!/usr/bin/env python3
"""
Test helper for Seldon - creates isolated test environments
Preserves learning continuity by never touching production .seldon directory
"""

import tempfile
import shutil
import os
from pathlib import Path

class SeldonTestEnvironment:
    """Context manager for isolated Seldon testing"""
    
    def __init__(self, copy_learnings=False):
        """
        Create isolated test environment
        
        Args:
            copy_learnings: If True, copies current learning data to test env
        """
        self.copy_learnings = copy_learnings
        self.original_dir = None
        self.test_dir = None
        
    def __enter__(self):
        # Save current directory
        self.original_dir = os.getcwd()
        
        # Create temporary directory
        self.test_dir = tempfile.mkdtemp(prefix='seldon_test_')
        os.chdir(self.test_dir)
        
        # Copy seldon executable
        shutil.copy(Path(self.original_dir) / 'seldon', self.test_dir)
        os.chmod('seldon', 0o755)
        
        # Optionally copy learning data
        if self.copy_learnings and (Path(self.original_dir) / '.seldon').exists():
            shutil.copytree(
                Path(self.original_dir) / '.seldon',
                Path(self.test_dir) / '.seldon'
            )
            print(f"✓ Copied learning data to test environment")
        
        print(f"✓ Created test environment in {self.test_dir}")
        return self.test_dir
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Return to original directory
        os.chdir(self.original_dir)
        
        # Clean up test directory
        shutil.rmtree(self.test_dir)
        print("✓ Cleaned up test environment")


# Example usage:
if __name__ == '__main__':
    print("Testing Seldon in isolated environment...\n")
    
    # Test without copying learnings (fresh start)
    with SeldonTestEnvironment(copy_learnings=False) as test_dir:
        os.system('./seldon init')
        os.system('./seldon stats')
    
    print("\nOriginal .seldon directory remains untouched!")
    
    # Test with copied learnings (preserve knowledge)
    print("\nTesting with copied learnings...")
    with SeldonTestEnvironment(copy_learnings=True) as test_dir:
        os.system('./seldon stats')