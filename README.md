# Canvas MCP Server

A Model Context Protocol (MCP) server that provides Canvas-related tools for AI assistants.

## Features

- 🎨 Canvas tool integration
- 🔧 Extensible tool architecture
- 🚀 Fast and lightweight

## Installation

### From Source

```bash
git clone https://github.com/sarthakneupane/canvas-mcp-server.git
cd canvas-mcp-server
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/sarthakneupane/canvas-mcp-server.git
cd canvas-mcp-server
pip install -e ".[dev]"
```

## Usage

### As a Standalone Server

```bash
canvas-mcp-server
```

### With Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "canvas-mcp-server": {
      "command": "canvas-mcp-server"
    }
  }
}
```

### Programmatic Usage

```python
from canvas_mcp_server import main

# Run the server
main()
```

## Available Tools

- **hello_world**: A simple greeting tool for testing

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Project Structure

```
canvas-mcp-server/
├── src/canvas_mcp_server/    # Main package
│   ├── server.py             # Server implementation
│   └── tools/                # Available tools
├── tests/                    # Test suite
├── examples/                 # Usage examples
└── scripts/                  # Development scripts
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add new feature'`)
6. Push to the branch (`git push origin feature/new-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Sarthak Neupane**

- GitHub: [@Sarthak-Neupane](https://github.com/Sarthak-Neupane)
