"""
ResilienceAI - Async Task Executor
Priority-based async execution with dependency management.
"""
import asyncio
from typing import Dict, List, Any, Optional, Callable, Coroutine
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import time
import uuid


@dataclass
class Task:
    """Async task definition."""
    task_id: str
    coro: Coroutine
    priority: int = 5  # 1-10, lower = higher priority
    timeout: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    callback: Optional[Callable] = None


@dataclass
class TaskResult:
    """Task execution result."""
    task_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0


class AsyncExecutor:
    """
    Async task executor with priority queue and dependency management.
    
    Features:
    - Priority-based execution
    - Dependency resolution
    - Timeout handling
    - Concurrent execution limits
    - Progress tracking
    """
    
    def __init__(
        self,
        max_workers: int = 10,
        max_concurrent: int = 5,
        thread_pool_size: int = 4
    ):
        self.max_workers = max_workers
        self.max_concurrent = max_concurrent
        
        # Task queues
        self._pending: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._running: Dict[str, asyncio.Task] = {}
        self._completed: Dict[str, TaskResult] = {}
        self._failed: Dict[str, TaskResult] = {}
        
        # Thread pool for sync functions
        self._thread_pool = ThreadPoolExecutor(max_workers=thread_pool_size)
        
        # Semaphore for concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
        # Execution control
        self._running_flag = False
        self._main_task: Optional[asyncio.Task] = None
        
    async def start(self) -> None:
        """Start the executor."""
        self._running_flag = True
        self._main_task = asyncio.create_task(self._run_loop())
        
    async def stop(self) -> None:
        """Stop the executor."""
        self._running_flag = False
        if self._main_task:
            self._main_task.cancel()
            try:
                await self._main_task
            except asyncio.CancelledError:
                pass
        
    async def submit(
        self,
        task_id: str,
        coro: Coroutine,
        priority: int = 5,
        timeout: Optional[float] = None,
        dependencies: Optional[List[str]] = None,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Submit a task for execution.
        
        Args:
            task_id: Unique task identifier
            coro: Coroutine to execute
            priority: Task priority (1-10)
            timeout: Timeout in seconds
            dependencies: List of task IDs that must complete first
            callback: Callback function on completion
            
        Returns:
            Task ID
        """
        task = Task(
            task_id=task_id,
            coro=coro,
            priority=priority,
            timeout=timeout,
            dependencies=dependencies or [],
            callback=callback
        )
        
        # Add to priority queue (lower priority number = higher priority)
        await self._pending.put((priority, time.time(), task))
        
        return task_id
    
    async def submit_sync(
        self,
        task_id: str,
        func: Callable,
        args: tuple = (),
        kwargs: Optional[Dict] = None,
        priority: int = 5,
        timeout: Optional[float] = None
    ) -> str:
        """Submit a synchronous function for execution."""
        async def wrapper():
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self._thread_pool,
                lambda: func(*args, **(kwargs or {}))
            )
        
        return await self.submit(task_id, wrapper(), priority, timeout)
    
    async def _run_loop(self) -> None:
        """Main execution loop."""
        while self._running_flag:
            try:
                # Get next task with timeout
                _, _, task = await asyncio.wait_for(
                    self._pending.get(),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            
            # Check dependencies
            if task.dependencies:
                deps_complete = all(
                    dep in self._completed or dep in self._failed
                    for dep in task.dependencies
                )
                if not deps_complete:
                    # Re-queue with same priority
                    await self._pending.put((task.priority, time.time(), task))
                    continue
                
                # Check if any dependency failed
                deps_failed = any(dep in self._failed for dep in task.dependencies)
                if deps_failed:
                    self._failed[task.task_id] = TaskResult(
                        task_id=task.task_id,
                        success=False,
                        error="Dependency failed"
                    )
                    continue
            
            # Execute task
            async with self._semaphore:
                asyncio.create_task(self._execute_task(task))
    
    async def _execute_task(self, task: Task) -> None:
        """Execute a single task."""
        start_time = time.time()
        
        try:
            # Create asyncio task
            asyncio_task = asyncio.create_task(task.coro)
            self._running[task.task_id] = asyncio_task
            
            # Wait with timeout
            if task.timeout:
                result = await asyncio.wait_for(
                    asyncio_task,
                    timeout=task.timeout
                )
            else:
                result = await asyncio_task
            
            execution_time = (time.time() - start_time) * 1000
            
            task_result = TaskResult(
                task_id=task.task_id,
                success=True,
                data=result,
                execution_time_ms=execution_time
            )
            
            self._completed[task.task_id] = task_result
            
        except asyncio.TimeoutError:
            task_result = TaskResult(
                task_id=task.task_id,
                success=False,
                error=f"Timeout after {task.timeout}s"
            )
            self._failed[task.task_id] = task_result
            
        except Exception as e:
            task_result = TaskResult(
                task_id=task.task_id,
                success=False,
                error=str(e)
            )
            self._failed[task.task_id] = task_result
        
        finally:
            if task.task_id in self._running:
                del self._running[task.task_id]
            
            # Call callback if provided
            if task.callback:
                try:
                    task.callback(task_result)
                except Exception as e:
                    print(f"Callback error: {e}")
    
    async def wait_for(
        self,
        task_id: str,
        timeout: Optional[float] = None
    ) -> TaskResult:
        """Wait for a specific task to complete."""
        start = time.time()
        
        while True:
            if task_id in self._completed:
                return self._completed[task.task_id]
            
            if task_id in self._failed:
                return self._failed[task.task_id]
            
            if timeout and (time.time() - start) > timeout:
                raise TimeoutError(f"Wait for task {task_id} timed out")
            
            await asyncio.sleep(0.1)
    
    async def wait_for_all(
        self,
        task_ids: Optional[List[str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, TaskResult]:
        """Wait for all tasks to complete."""
        if task_ids is None:
            task_ids = list(self._running.keys())
        
        results = {}
        for task_id in task_ids:
            try:
                results[task_id] = await self.wait_for(task_id, timeout)
            except TimeoutError:
                results[task_id] = TaskResult(
                    task_id=task_id,
                    success=False,
                    error="Wait timeout"
                )
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get executor status."""
        return {
            "pending": self._pending.qsize(),
            "running": len(self._running),
            "completed": len(self._completed),
            "failed": len(self._failed)
        }
    
    async def cancel(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id in self._running:
            self._running[task_id].cancel()
            return True
        return False
    
    async def shutdown(self) -> None:
        """Shutdown the executor."""
        await self.stop()
        
        # Cancel all running tasks
        for task in self._running.values():
            task.cancel()
        
        # Shutdown thread pool
        self._thread_pool.shutdown(wait=True)
