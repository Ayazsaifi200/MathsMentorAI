# -*- coding: utf-8 -*-
"""
MCP (Model Context Protocol) Integration for Math Mentor AI
Implements tool discovery and context sharing using MCP protocol
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class MCPToolType(Enum):
    """Types of MCP tools"""
    COMPUTATION = "computation"
    SEARCH = "search"
    VERIFICATION = "verification"
    FORMATTING = "formatting"
    VISUALIZATION = "visualization"

class MCPTool:
    """MCP Tool definition"""
    
    def __init__(self, 
                 name: str,
                 description: str,
                 tool_type: MCPToolType,
                 execute_fn: Callable,
                 parameters: Dict[str, Any] = None):
        """
        Initialize MCP tool
        
        Args:
            name: Tool name
            description: Tool description
            tool_type: Type of tool
            execute_fn: Function to execute the tool
            parameters: Tool parameter schema
        """
        self.name = name
        self.description = description
        self.tool_type = tool_type
        self.execute_fn = execute_fn
        self.parameters = parameters or {}
        self.created_at = datetime.now()
        self.execution_count = 0
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        try:
            result = self.execute_fn(**kwargs)
            self.execution_count += 1
            return {
                "success": True,
                "result": result,
                "tool_name": self.name,
                "execution_count": self.execution_count
            }
        except Exception as e:
            logger.error(f"Tool execution failed for {self.name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": self.name
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for MCP"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.tool_type.value,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat()
        }


class MCPRegistry:
    """MCP Tool Registry for dynamic tool discovery"""
    
    def __init__(self):
        """Initialize MCP registry"""
        self.tools: Dict[str, MCPTool] = {}
        self.contexts: Dict[str, Any] = {}
        logger.info("MCP Registry initialized")
    
    def register_tool(self, tool: MCPTool) -> bool:
        """
        Register a new tool
        
        Args:
            tool: MCPTool instance
            
        Returns:
            True if registered successfully
        """
        if tool.name in self.tools:
            logger.warning(f"Tool {tool.name} already registered, overwriting")
        
        self.tools[tool.name] = tool
        logger.info(f"Registered MCP tool: {tool.name}")
        return True
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool
        
        Args:
            tool_name: Name of tool to unregister
            
        Returns:
            True if unregistered successfully
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Unregistered MCP tool: {tool_name}")
            return True
        return False
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self, tool_type: MCPToolType = None) -> List[MCPTool]:
        """
        List all registered tools
        
        Args:
            tool_type: Optional filter by tool type
            
        Returns:
            List of tools
        """
        if tool_type:
            return [tool for tool in self.tools.values() if tool.tool_type == tool_type]
        return list(self.tools.values())
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get schema for all registered tools"""
        return [tool.get_schema() for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a registered tool
        
        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool parameters
            
        Returns:
            Execution result
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }
        
        return tool.execute(**kwargs)
    
    def share_context(self, context_id: str, context: Any):
        """
        Share context between tools
        
        Args:
            context_id: Unique context identifier
            context: Context data to share
        """
        self.contexts[context_id] = {
            "data": context,
            "timestamp": datetime.now().isoformat()
        }
        logger.debug(f"Context shared: {context_id}")
    
    def get_context(self, context_id: str) -> Optional[Any]:
        """
        Get shared context
        
        Args:
            context_id: Context identifier
            
        Returns:
            Context data if exists
        """
        context_entry = self.contexts.get(context_id)
        if context_entry:
            return context_entry["data"]
        return None
    
    def clear_contexts(self):
        """Clear all shared contexts"""
        self.contexts.clear()
        logger.debug("All contexts cleared")


class MCPMathToolkit:
    """MCP Toolkit for Mathematical Operations"""
    
    def __init__(self, registry: MCPRegistry):
        """
        Initialize math toolkit with MCP registry
        
        Args:
            registry: MCP Registry instance
        """
        self.registry = registry
        self._register_math_tools()
    
    def _register_math_tools(self):
        """Register mathematical tools with MCP"""
        
        # Symbolic computation tool
        symbolic_tool = MCPTool(
            name="symbolic_compute",
            description="Perform symbolic mathematical computations",
            tool_type=MCPToolType.COMPUTATION,
            execute_fn=self._symbolic_compute,
            parameters={
                "expression": {"type": "string", "required": True},
                "operation": {"type": "string", "required": True, 
                            "enum": ["simplify", "expand", "factor", "solve"]}
            }
        )
        self.registry.register_tool(symbolic_tool)
        
        # Equation solver tool
        solver_tool = MCPTool(
            name="solve_equation",
            description="Solve mathematical equations",
            tool_type=MCPToolType.COMPUTATION,
            execute_fn=self._solve_equation,
            parameters={
                "equation": {"type": "string", "required": True},
                "variable": {"type": "string", "required": False}
            }
        )
        self.registry.register_tool(solver_tool)
        
        # Derivative calculator tool
        derivative_tool = MCPTool(
            name="calculate_derivative",
            description="Calculate derivatives",
            tool_type=MCPToolType.COMPUTATION,
            execute_fn=self._calculate_derivative,
            parameters={
                "expression": {"type": "string", "required": True},
                "variable": {"type": "string", "required": False, "default": "x"}
            }
        )
        self.registry.register_tool(derivative_tool)
        
        # Integral calculator tool
        integral_tool = MCPTool(
            name="calculate_integral",
            description="Calculate integrals",
            tool_type=MCPToolType.COMPUTATION,
            execute_fn=self._calculate_integral,
            parameters={
                "expression": {"type": "string", "required": True},
                "variable": {"type": "string", "required": False, "default": "x"}
            }
        )
        self.registry.register_tool(integral_tool)
        
        # LaTeX formatter tool
        latex_tool = MCPTool(
            name="format_latex",
            description="Format mathematical expressions as LaTeX",
            tool_type=MCPToolType.FORMATTING,
            execute_fn=self._format_latex,
            parameters={
                "expression": {"type": "string", "required": True}
            }
        )
        self.registry.register_tool(latex_tool)
        
        logger.info(f"Registered {len(self.registry.list_tools())} mathematical MCP tools")
    
    def _symbolic_compute(self, expression: str, operation: str) -> Any:
        """Perform symbolic computation"""
        try:
            import sympy as sp
            
            expr = sp.sympify(expression)
            
            if operation == "simplify":
                return str(sp.simplify(expr))
            elif operation == "expand":
                return str(sp.expand(expr))
            elif operation == "factor":
                return str(sp.factor(expr))
            elif operation == "solve":
                return str(sp.solve(expr))
            else:
                return f"Unknown operation: {operation}"
                
        except Exception as e:
            raise Exception(f"Symbolic computation failed: {str(e)}")
    
    def _solve_equation(self, equation: str, variable: str = "x") -> Any:
        """Solve equation"""
        try:
            import sympy as sp
            
            # Parse equation
            var = sp.Symbol(variable)
            if "=" in equation:
                left, right = equation.split("=")
                eq = sp.Eq(sp.sympify(left), sp.sympify(right))
            else:
                eq = sp.sympify(equation)
            
            solution = sp.solve(eq, var)
            return str(solution)
            
        except Exception as e:
            raise Exception(f"Equation solving failed: {str(e)}")
    
    def _calculate_derivative(self, expression: str, variable: str = "x") -> Any:
        """Calculate derivative"""
        try:
            import sympy as sp
            
            var = sp.Symbol(variable)
            expr = sp.sympify(expression)
            derivative = sp.diff(expr, var)
            
            return str(derivative)
            
        except Exception as e:
            raise Exception(f"Derivative calculation failed: {str(e)}")
    
    def _calculate_integral(self, expression: str, variable: str = "x") -> Any:
        """Calculate integral"""
        try:
            import sympy as sp
            
            var = sp.Symbol(variable)
            expr = sp.sympify(expression)
            integral = sp.integrate(expr, var)
            
            return str(integral)
            
        except Exception as e:
            raise Exception(f"Integration failed: {str(e)}")
    
    def _format_latex(self, expression: str) -> str:
        """Format as LaTeX"""
        try:
            import sympy as sp
            
            expr = sp.sympify(expression)
            latex = sp.latex(expr)
            
            return latex
            
        except Exception as e:
            raise Exception(f"LaTeX formatting failed: {str(e)}")


# Global MCP registry instance
_global_registry = None

def get_mcp_registry() -> MCPRegistry:
    """Get or create global MCP registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = MCPRegistry()
        # Initialize math toolkit
        MCPMathToolkit(_global_registry)
    return _global_registry


def initialize_mcp() -> MCPRegistry:
    """Initialize MCP system"""
    registry = get_mcp_registry()
    logger.info("MCP system initialized")
    return registry
